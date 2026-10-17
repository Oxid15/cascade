02 - Data Lineage
#################

`Recipe 02_data_lineage on GitHub <https://github.com/Oxid15/cascade_recipes/tree/master/02_data_lineage>`__ • `Cascade Recipes GitHub repository <https://github.com/Oxid15/cascade_recipes/>`__

   Model 00003 regressed. Was it the code, or did the dataset change under me?

Introduction
************

This recipe focuses on data versioning. MLOps tools for experiment tracking like MLflow or Aim focus
on tracking models, their parameters and artifacts and most of the times they overlook tracking datasets.
This includes both source data and data transformations.
It can be argued that data is more important than models in machine learning and Cascade respects that opinion by
adding support for tracking both data transformations and source datasets.
In this recipe you will learn how to use Cascade for automatic versioning of your data pipeline.

Generate Dataset
****************

First script creates synthetic support-ticket corpus - three weekly snapshots of the same dataset.



.. code-block:: python
    
    import json
    import os
    import random
    
    HERE = os.path.dirname(os.path.abspath(__file__))
    
    SUBJECTS = [
        "cannot log in after password reset",
        "invoice charged twice this month",
        "app crashes when opening reports",
        "how do I export my data",
        "refund for cancelled subscription",
        "SSO redirect loop on staging",
        "feature request: dark mode",
        "API returns 500 on bulk upload",
    ]
    LABELS = ["billing", "bug", "account", "question", "feature"]
    MESSY = {"billing": "Billing", "bug": "BUG", "account": "account "}
    
    

This dataset will simulate inconsistent labels and duplicated rows.



.. code-block:: python
    
    
    
    def rows(n, seed, messy):
        rng = random.Random(seed)
        out = []
        for i in range(n):
            subj = rng.choice(SUBJECTS)
            label = rng.choice(LABELS)
            if messy:
                label = MESSY.get(label, label)
            out.append(
                {
                    "id": i,
                    "text": f"{subj} (ref {rng.randint(1000, 9999)})",
                    "label": label,
                    "priority": rng.choice(["low", "normal", "high"]),
                }
            )
        if messy:
            out += rng.sample(out, 40)  # duplicates that need de-duping
        return out
    
    
    

We are writing three JSON files with the following properties:

- Week 1: raw dump, has duplicates and inconsistent label spellings
- Week 2: same rows, one label taxonomy fix applied upstream
- Week 3: more rows arrive



.. code-block:: python
    
    
    
    def write(name, data):
        path = os.path.join(HERE, "data", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            for r in data:
                f.write(json.dumps(r) + "\n")
        print(f"{name}: {len(data)} rows")
    
    
    if __name__ == "__main__":
        write("tickets_w1.jsonl", rows(400, seed=1, messy=True))
        write("tickets_w2.jsonl", rows(400, seed=1, messy=False))
        write("tickets_w3.jsonl", rows(600, seed=2, messy=False))
    

Data Transformation Pipeline
****************************

Here is the pipeline definition in a separate file for the ticket dataset.



.. code-block:: python
    
    import json
    import os
    
    from cascade.data import Dataset, Filter, Modifier, Sampler
    
    HERE = os.path.dirname(os.path.abspath(__file__))
    
    CANONICAL = {
        "billing": "billing",
        "bug": "bug",
        "account": "account",
        "question": "question",
        "feature": "feature",
    }
    
    

First we inherit ``cascade.data.Dataset`` to create simple JSON reading custom data source.
Main methods of a custom ``Dataset`` to define are ``get`` and ``__len__``. There is also an
ability to customize its metadata using ``get_meta`` method.
Metadata can then be tracked when we link a dataset to a model.


.. code-block:: python
    
    
    
    class TicketDump(Dataset):
        """Raw JSONL dump as exported by the helpdesk."""
    
        def __init__(self, snapshot: str, **kwargs):
            self._snapshot = snapshot
            with open(os.path.join(HERE, "data", snapshot)) as f:
                self._rows = [json.loads(line) for line in f]
            super().__init__(**kwargs)
    
        def get(self, index):
            return self._rows[index]
    
        def __len__(self):
            return len(self._rows)
    
        def get_meta(self):
            meta = super().get_meta()
            meta[0]["snapshot"] = self._snapshot
            meta[0]["labels"] = sorted({r["label"] for r in self._rows})
            return meta
    
    
    

We build a pipeline by stacking ``Modifier``s on top of a ``Dataset``.
Each modifier can call its dataset, perform some operations over the results
of the previous stage and return.




.. code-block:: python
    
    
    
    class NormalizeLabels(Modifier):
        """Fold 'BUG' / 'Billing' / 'account ' into the canonical taxonomy."""
    
        def get(self, index):
            item = dict(self._dataset[index])
            item["label"] = CANONICAL[item["label"].strip().lower()]
            return item
    
    
    

Modifiers that change dataset's length are called ``Sampler``s. This sampler is
removing duplicate rows. We pass new length to sampler's parent constructor
so that it will be used in ``__len__`` automatically.




.. code-block:: python
    
    
    
    class Dedup(Sampler):
        """
        Drop rows whose id was seen before
        """
    
        def __init__(self, dataset, **kwargs):
            seen = set()
            self._keep = []
            for i in range(len(dataset)):
                tid = dataset[i]["id"]
                if tid not in seen:
                    seen.add(tid)
                    self._keep.append(i)
    
            super().__init__(dataset, len(self._keep), **kwargs)
    
        def get(self, index):
            return self._dataset[self._keep[index]]
    
    
    

We also use default cascade.data.Filter with a filter function that returns `bool`.



.. code-block:: python
    
    
    
    def not_low_priority(item):
        return item["priority"] != "low"
    
    
    def build(snapshot: str, drop_low_priority: bool = False):
        ds = TicketDump(snapshot)
        ds = NormalizeLabels(ds)
        ds = Dedup(ds)
        if drop_low_priority:
            ds = Filter(ds, not_low_priority)
        return ds
    

Version Datasets
****************

In the following file we simulate the process of getting the source data
we have received, building the pipeline we defined previously and then
saving it in ``DataLine`` - special container that allows to track
and automatically version data pipelines.
It can store dataset metadata and even pickle the
pipeline object to be loaded elsewhere exactly as it was created.

We can see an example of how automatic versioning works below.



.. code-block:: python
    
    
    import os
    
    from cascade.repos import Repo
    
    from pipeline import build
    
    HERE = os.path.dirname(os.path.abspath(__file__))
    
    
    def show(dl, ds, note):
        print(f"{note:<46} -> version {dl.get_version(ds)}")
    
    
    

This is the first iteration
We add description, build dataset and use ``update_meta`` to add
more fields to dataset's metadata so that they could be tracked and influence the
automatic versioning when changed.

In the following example we build a pipeline, update its meta and save it in line.



.. code-block:: python
    
    
    
    def main():
        dl = Repo("repo").add_line("dataline", line_type="data")
        dl.describe("Support tickets, weekly snapshots from the helpdesk export")
    
        ds = build("tickets_w1.jsonl")
        ds.update_meta({"snapshot_week": 1, "known_issues": ["dupes", "label spellings"]})
        dl.save(ds)
        show(dl, ds, "w1 raw dump")
    
        

``DataLine`` will assign a version to the dataset at the moment of saving automatically.
It uses metadata to determine if the pipeline changed. The version has two components - major
and minor. Major component changes when the pipeline's contents change. For example with a new
``Modifier`` or when some step is removed. Minor changes on any metadata field change.

Here we just update fields in meta so when we save new dataset it will bump minor component.

    

.. code-block:: python
    
    
        ds.update_meta({"reviewed_by": "data-eng", "ticket": "DATA-114"})
        dl.save(ds)
        show(dl, ds, "w1 + review annotation (meta only)")
    
        

This week should also get a minor bump.

    

.. code-block:: python
    
    
        ds2 = build("tickets_w2.jsonl")
        ds2.update_meta({"snapshot_week": 2, "known_issues": []})
        dl.save(ds2)
        show(dl, ds2, "w2 clean source (same pipeline shape)")
    
        

This week gets a major bump since pipelie also gets ``Filter`` step.

    

.. code-block:: python
    
    
        ds3 = build("tickets_w3.jsonl", drop_low_priority=True)
        ds3.update_meta({"snapshot_week": 3, "known_issues": []})
        dl.save(ds3)
        show(dl, ds3, "w3 + Filter stage (pipeline shape changed)")
    
        print("\nversions on disk:", sorted(os.listdir(dl.get_root())))
        print("latest:", dl.get_latest_version())
    
        

Reproduce Dataset Version Exactly
*********************************

After saving a dataset in line, we can load it exactly
using its version.
Here we ``load`` the dataset of version ``0.1`` and the latest version.

    

.. code-block:: python
    
    
        old = dl.load("0.1")
        print(f"\nreloaded 0.1: {len(old)} rows, first label = {old[0]['label']!r}")
        new = dl.load(str(dl.get_latest_version()))
        print(f"reloaded latest: {len(new)} rows, first label = {new[0]['label']!r}")
    
    
    if __name__ == "__main__":
        main()
    

Pin the Model to Dataset Version
********************************

Trains two classifiers on two different DataLine versions and records
the link, so ``cascade query`` can answer "which data version did this model see?".



.. code-block:: python
    
    
    import os
    
    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.linear_model import SGDClassifier
    
    from cascade.repos import Repo
    from cascade.utils.sklearn import SkMetric, SkModel
    
    HERE = os.path.dirname(os.path.abspath(__file__))
    
    

Here we load two dataset versions and train a classifier on each version.

We can link dataset and even its line to the model using special methods.
This will allow us to not lose track of where the data came from.




.. code-block:: python
    
    
    
    def main():
        repo = Repo(os.path.join(HERE, "repo"))
        dl = repo.add_line("dataline", line_type="data")
        line = repo.add_line("ticket_router", line_type="model")
    
        for version in ("0.2", "1.0"):
            ds = dl.load(version)
            x = [item["text"] for item in ds]
            y = [item["label"] for item in ds]
    
            model = SkModel(
                blocks=[
                    HashingVectorizer(n_features=2048),
                    SGDClassifier(loss="log_loss", random_state=0),
                ],
                data_version=version,
            )
            model.fit(x, y)
            model.evaluate(x, y, [SkMetric("accuracy_score")])
    
            model.link_dataset(ds, name="tickets", split="train", line=dl)
            model.link(name="dataline", uri=dl.get_root())
            model.describe(f"Ticket router trained on dataline version {version}")
            model.tag(f"data-{version}")
    
            line.save(model)
            print(f"data {version}: {len(ds)} rows, acc={model.metrics[0].value:.3f}")
    
    
    if __name__ == "__main__":
        main()
    
    

Conclusion
**********

In this recipe dataset versioning in Cascade is excercised.
It is able to automatically version and track datasets and processing pipeline.
You can also link data to the model you are training and always go back and reproduce
your machine learning experiment exactly.


