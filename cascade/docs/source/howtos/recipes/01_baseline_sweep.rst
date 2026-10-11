Track ML experiments with Cascade
#################################

  I ran six experiments last week - which one won, with which settings, and on which version of the features?

Introduction
************

In machine learning practice there are lots of cases when you are experimenting with various
features, train models and look at their results. Without proper experiment tracking it is
hard to keep those results stored and accessible. In real life they tend to pile up very fast
and memorizing them is not enough.
At enterprise scale there are special experiment tracking tools for that. Even smaller companies
can use som hosted solutions like ClearML or set up their own MLflow. However, at small-scale
MLOps is usually underdeveloped and for individual ML engineers or small teams it can be hard to
set up an infrastructure fot that.
Cascade was built to serve those people - it allows local-first experiment tracking
without complex setups, databases and other infrastructure.

In this example you will learn how to set up local-first experiment tracking with Cascade.

The following script will generate simple synthetic telecom churn table for our experiments.


.. code-block:: python

    import os
    
    import numpy as np
    import pandas as pd
    
    HERE = os.path.dirname(os.path.abspath(__file__))
    OUT = os.path.join(HERE, "data", "churn.csv")
    
    
    def make_df(n: int = 2000, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
    
        tenure = rng.integers(1, 72, size=n)
        monthly = rng.normal(70, 25, size=n).clip(15, 150)
        contract = rng.choice(["month", "year", "two_year"], size=n, p=[0.55, 0.3, 0.15])
        support_calls = rng.poisson(1.2, size=n)
        is_fiber = rng.random(size=n) < 0.45
        paperless = rng.random(size=n) < 0.6
    
        logit = (
            -1.2
            - 0.04 * tenure
            + 0.012 * monthly
            + 0.35 * support_calls
            + 0.6 * is_fiber
            + 0.2 * paperless
            + np.where(contract == "month", 0.9, np.where(contract == "year", 0.0, -0.7))
        )
        p = 1 / (1 + np.exp(-logit))
        churn = (rng.random(size=n) < p).astype(int)
    
        return pd.DataFrame(
            {
                "tenure_months": tenure,
                "monthly_charges": monthly.round(2),
                "contract": contract,
                "support_calls": support_calls,
                "is_fiber": is_fiber.astype(int),
                "paperless_billing": paperless.astype(int),
                "churn": churn,
            }
        )

Run `make_data.py` to generate a .csv for our next steps.

.. code-block:: python

    if __name__ == "__main__":
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        df = make_df()
        df.to_csv(OUT, index=False)
        print(f"wrote {len(df)} rows to {OUT}, churn rate {df['churn'].mean():.3f}")

Let's do necessary imports here.

.. code-block:: python

    import os
    
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier
    
    from cascade import data as cdd
    from cascade.repos import Repo
    from cascade.utils.sklearn import SkMetric, SkModel
    from cascade.utils.tables import TableDataset
    
    HERE = os.path.dirname(os.path.abspath(__file__))
    CSV = os.path.join(HERE, "data", "churn.csv")
    
    CONTRACT_CODES = {"month": 0, "year": 1, "two_year": 2}

Data Loading and Preprocess
***************************

First we define datasets. The csv that we generated previously will be tracked using ``TableDataset``.
After that we will add two processing stages using ``cascade.data.Modifier``. The first will turn each row
into a dict and the second one will turn those into pairs of features and targets.
The main point of wrapping every data processing stage into cascade object is that it allows
for effortless tracking, chekpointing and versioning of your data processing pipeline.

.. code-block:: python

    class Rows(cdd.Modifier):
        """Normalize table to dicts per row"""
    
        def get(self, index):
            item = self._dataset[index]
            if isinstance(item, pd.DataFrame):
                item = item.iloc[0]
            return item.to_dict() if hasattr(item, "to_dict") else item
    
    
    class Featurize(cdd.Modifier):
        """Table row -> {"x": list[float], "y": int}."""
    
        def __init__(self, dataset, use_contract: bool, **kwargs):
            self._use_contract = use_contract
            super().__init__(dataset, **kwargs)
    
        def get(self, index):
            row = self._dataset[index]
            x = [
                row["tenure_months"],
                row["monthly_charges"],
                row["support_calls"],
                row["is_fiber"],
                row["paperless_billing"],
            ]
            if self._use_contract:
                x.append(CONTRACT_CODES[row["contract"]])
            return {"x": x, "y": int(row["churn"])}

Those functions are just convenience utilities to build a pipeline. However, it contains
such features as adding a description to a dataset and tracking dataset
parameters.

.. code-block:: python

    def build_pipeline(use_contract: bool):
        table = TableDataset(t=pd.read_csv(CSV))
        ds = Rows(table)
        ds = Featurize(ds, use_contract=use_contract)
        ds.describe("Churn features from the raw billing export")
        ds.update_meta({"use_contract": use_contract})
        return ds
    
    
    def xy(ds):
        x = [item["x"] for item in ds]
        y = [item["y"] for item in ds]
        return x, y

ML Model Tracking
*****************
Here we build a model similarly to a dataset. We use ``cascade.utils.SkModel`` to wrap
a scikit-learn pipeline. Notice how config is used to configurate the model and also
passed as keywords to the wrapper. This will track all those values as Model's parameters
and can be queried and analyzed afterwards.

.. code-block:: python

    def build_model(cfg):
        if cfg["family"] == "logreg":
            return SkModel(
                blocks=[StandardScaler(), LogisticRegression(C=cfg["C"], max_iter=200)],
                **cfg,
            )
        elif cfg["family"] == "tree":
            return SkModel(
                blocks=[DecisionTreeClassifier(max_depth=cfg["max_depth"], random_state=0)],
                **cfg,
            )
        else:
            raise ValueError(f"Unknown model family {cfg['family']}")

Running an Experiment
*********************

Here we define 6 experiments that in reality could be run one by one by changing
parameters in a script when experimenting naturally.

.. code-block:: python

    SWEEP = [
        {"family": "logreg", "C": 0.1, "use_contract": True},
        {"family": "logreg", "C": 1.0, "use_contract": True},
        {"family": "logreg", "C": 1.0, "use_contract": False},
        {"family": "tree", "max_depth": 3, "use_contract": True},
        {"family": "tree", "max_depth": 6, "use_contract": True},
        {"family": "tree", "max_depth": 6, "use_contract": False},
    ]

And then we finally bring everything together - build pipeline and model, train
, test, add description and tags, then link dataset to the model and save it.
ModelLine inside the Repo will save SkModel's metadata, params, metrics and artifact
you can later load and run once again.

.. code-block:: python

    def main():
        repo = Repo(os.path.join(HERE, "repo"))
        repo.describe("Churn baseline sweep, Q3 planning")
    
        for cfg in SWEEP:
            ds = build_pipeline(cfg["use_contract"])
            train_ds, test_ds = cdd.split(ds, frac=0.8)
    
            model = build_model(cfg)
            model.fit(*xy(train_ds))
    
            x_test, y_test = xy(test_ds)
            model.evaluate(
                x_test,
                y_test,
                [
                    SkMetric("f1_score"),
                    SkMetric("accuracy_score"),
                    SkMetric("roc_auc_score"),
                ],
            )
    
            model.tag(cfg["family"])
            model.describe(
                f"{cfg['family']} baseline, contract feature={cfg['use_contract']}"
            )
            model.link(ds, name="features")
    
            line = repo.add_line(f"baseline_{cfg['family']}", line_type="model")
            line.save(model)
            print(f"saved {cfg} -> {[(m.name, m.value) for m in model.metrics]}")
    
    
    if __name__ == "__main__":
        main()

Conclusion
**********

In this recipe we excercise how Cascade can work with
tabular data, track data pipelines, scikit-learn based models,
how to use Repo and ModelLine to store ML model's artifacts locally
along with their parameters, metric values and other metadata.

