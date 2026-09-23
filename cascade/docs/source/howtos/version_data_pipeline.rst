Version data pipeline
=====================

Data lineage becomes crucial when quickly experimenting with a small-scale ML project.
Usually the source datasets are a mess and a preprocessing can change frequently.
This is why it is important to start tracking the changes early in the project.

After reading this you will learn how to:

* Version your data pipeline
* Add metadata and fill data cards
* Avoid version explosions due to volatile fields in meta

Your starting data transformation pipeline
------------------------------------------

Here you can see a simplified version of a data pipeline that was built using Cascade.
``ClientProjectDataset`` represents an object that could make a database call or read a JSON file.
Then there is a set of preprocessing functions each applied using ``ApplyModifier``.
The 

.. code-block:: python

    from cascade.data import ApplyModifier, Dataset


    class ClientProjectDataset(Dataset):
        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)

            self._tickets = [
                {"title": "Fix onboarding flow", "owner": "Ava", "effort": 3, "priority": "high"},
                {"title": "Add CSV export", "owner": "Leo", "effort": 5, "priority": "medium"},
                {"title": "Warm cache for dashboard", "owner": "Mina", "effort": 2, "priority": "high"},
            ]

        def __len__(self):
            return len(self._tickets)

        def get(self, index):
            return self._tickets[index]


    def add_slug(item):
        item["slug"] = item["title"].lower().replace(" ", "-")
        return item


    def score_risk(item):
        item["risk_score"] = item["effort"] + (1 if item["priority"] == "high" else 0)
        return item

    RISK_THRESHOLD = 5

    def pick_sprint_candidates(item):
        item["sprint_ready"] = item["risk_score"] <= RISK_THRESHOLD and item["owner"] != "Mina"
        return item


    pipeline = ClientProjectDataset()
    pipeline = ApplyModifier(pipeline, add_slug)
    pipeline = ApplyModifier(pipeline, score_risk)
    pipeline = ApplyModifier(pipeline, pick_sprint_candidates)

This pipeline can easily be tracked using ``DataLine``.

Enable dataset versioning
-------------------------

In this example we create ``client_project_datasets`` line and save our pipeline there with ``only_meta`` flag for this example,
but you can always save the pipeline object itself by turning this off.

We can see that the line now knows the version of this pipeline which is ``0.1``.

.. code-block:: python

    from cascade.lines import DataLine

    line = DataLine("client_project_datasets")
    line.save(pipeline, only_meta=True)

    line.get_version(pipeline) # -> 0.1


.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "0.1"


Add useful metadata
-------------------

If we change something in the source data or code ``DataLine`` would not notice that unless we
added it in the metadata. Here we try to describe our source data using ``DataCard``. It is a helper
object that you can create and fill as a way to describe your dataset.
We also use ``update_meta`` here to track risk threshold parameter and change the pipeline version if
it updates.

When we save this updated dataset it will bump its minor version to ``0.2``.

.. code-block:: python

    from cascade.data import DataCard

    pipeline = ClientProjectDataset(
        data_card=DataCard(
            name="tickets",
            desc="Dataset of tickets from client's project",
            source="client database",
            goal="We want to train ML model to estimate task effort",
            labeling_info=None,
        )
    )
    pipeline = ApplyModifier(pipeline, add_slug)
    pipeline = ApplyModifier(pipeline, score_risk)
    pipeline = ApplyModifier(pipeline, pick_sprint_candidates)

    pipeline.tag("testing")
    pipeline.update_meta(
        {
            "risk_threshold": RISK_THRESHOLD
        }
    )

    line.save(pipeline, only_meta=True)

    line.get_version(pipeline) # -> 0.2

.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "0.2"

Track pipeline changes
----------------------

``Dataset`` version has two components - major and minor. Minor will bump when anything in metadata changes. And Major will
bump if there is a change in the pipeline structure - for example when you add/remove a pipeline stage.

In the following example we add ``RandomSampler`` which will bump the version to ``1.0``.

.. code-block:: python

    from cascade.data import RandomSampler


    pipeline = RandomSampler(pipeline)

    line.save(pipeline, only_meta=True)

    line.get_version(pipeline) # -> 1.0    

.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "1.0"

Avoid version explosions
------------------------

Minor version will always go up if there is a change in any metadata field. 
Meaning that if you have a field that is unique for every run your minor versions will update
with each run while masking real changes.

To avoid this situation Cascade ``Dataset`` provides a method ``declare_volatiles`` which helps
to mask some values from versioning. 

In the following example we subclass the ``ClientProjectDataset`` and add the field that will
always be different each run.

.. code-block:: python

    from datetime import datetime

    class TimedClientProjectDataset(ClientProjectDataset):
        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)

            self.query_time = datetime.now()

        def get_meta(self):
            meta = super().get_meta()
            meta[0]["query_time"] = self.query_time
            return meta

    def build_pipeline():
        pipeline = TimedClientProjectDataset(
            data_card=DataCard(
                name="timed_tickets",
                desc="Dataset of tickets from client's project but now with time of DB query",
                source="client database",
                goal="We want to train ML model to estimate task effort",
                labeling_info=None,
            )
        )
        pipeline = ApplyModifier(pipeline, add_slug)
        pipeline = ApplyModifier(pipeline, score_risk)
        pipeline = ApplyModifier(pipeline, pick_sprint_candidates)

        pipeline.tag("testing")
        pipeline.update_meta(
            {
                "risk_threshold": RISK_THRESHOLD,
            }
        )
        return pipeline

    pipeline = build_pipeline()

    line.get_version(pipeline) # -> 2.0

    line.save(pipeline, only_meta=True)

.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "2.0"

We expected the version to change since we updated the pipeline. But now
if we rebuild it without any changes the minor version will still go up.

.. code-block:: python

    pipeline = build_pipeline()

    line.get_version(pipeline) # -> 2.1

    line.save(pipeline, only_meta=True)

.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "2.1"

Let's avoid it by using ``declare_volatiles``. It will say ``DataLine`` to not use ``query_time`` field
when versioning this dataset.

.. code-block:: python

    class TimedClientProjectDataset(ClientProjectDataset):
        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)

            self.query_time = datetime.now()

            self.declare_volatiles("query_time")

        def get_meta(self):
            meta = super().get_meta()
            meta[0]["query_time"] = self.query_time
            return meta

Now we also expect the version to change since we changed how this field is represented.

.. code-block:: python

    pipeline = build_pipeline()

    line.get_version(pipeline) # -> 2.2

.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "2.2"


But from now on, when creating a new dataset ``DataLine`` will version it consistently.

.. code-block:: python

    pipeline = build_pipeline()

    line.get_version(pipeline) # -> 2.2

.. invisible-code-block: python

    assert str(line.get_version(pipeline)) == "2.2"

See also
--------

* :ref:`/howtos/pipeline_building.rst`
