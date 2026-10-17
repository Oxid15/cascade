Track Existing Functional Pipeline
##################################

Cascade offers tools for :ref:`/howtos/pipeline_building.rst` that are based on ``Dataset`` classes, but if you already have a pipeline written with
Python functions it can be hard to migrate without rewriting everything with classes.

After reading this you will learn how to:

* make your data pipeline written using Python functions reproducible
* validate inputs of your data transformations automatically


Your intial data transformation pipeline
****************************************

Here let's consider an example data pipeline. Your project will for sure have a much more complex setup, but here
we will see a toy example of a preprocessing of commerce prices dataset that may go into an ML model downstream.

The example includes ``load_data`` function which mocks a JSON load or a database query.

We also add two data transformation functions like ``select_category`` and ``price_to_cents``. Each one
accepts a dataset with some other arguments and returns a new transformed dataset.

.. code-block:: python

    def load_data():
        return [
            {
                "id": 0,
                "city": "Dusseldorf",
                "product_category": "Electronics",
                "price_usd": 99.99,
            },
            {
                "id": 1,
                "city": "Chicago",
                "product_category": "Grocery",
                "price_usd": 5.00,
            },
            {
                "id": 2,
                "city": "Dubai",
                "product_category": "Grocery",
                "price_usd": 23.50,
            },
        ]

    def select_category(data, category):
        return [item for item in data if item.get("product_category") == category]

    def price_to_cents(data):
        for item in data:
            item["price_cents"] = item["price_usd"] * 100
        return data

    ds = load_data()
    ds = select_category(ds, "Grocery")
    ds = price_to_cents(ds)

.. invisible-code-block: python

    assert len(ds) == 2
    assert ds[0]["price_cents"] == 500.0

The problem with this pipeline is obvious - **it lacks any tracking and validation**.
Sure you can track code changes in git, but most small projects iterate much faster.
You would not pollute your git repo committing each parameter change while tuning the
preprocess pipeline.

While running experiments locally it is easy to lose track of which parameters, datasets
and configuration produced which results.

This is why you can use Cascade to add data validation and lineage to your project effortlessly.

Adding Cascade tracking
***********************

In the following example we are adding ``@dataset`` and ``@modifier`` decorators over exiting functions without changing them.

.. important::
    
    Decorators assume that your functions accept a dataset as a first argument. This is the change that is required to
    turn your functions into Cascade ``Datasets``.

.. code-block:: python

    from cascade.data import dataset, modifier

    @dataset
    def load_data():
        return [
            {
                "id": 0,
                "city": "Dusseldorf",
                "product_category": "Electronics",
                "price_usd": 99.99,
            },
            {
                "id": 1,
                "city": "Chicago",
                "product_category": "Grocery",
                "price_usd": 5.00,
            },
            {
                "id": 2,
                "city": "Dubai",
                "product_category": "Grocery",
                "price_usd": 23.50,
            },
        ]

    @modifier
    def select_category(data, category):
        return [item for item in data if item.get("product_category") == category]

    @modifier
    def price_to_cents(data):
        for item in data:
            item["price_cents"] = item["price_usd"] * 100
        return data

    # We will compare new results with previous
    initial_data = ds

    ds = load_data()
    ds = select_category(ds, "Grocery")
    ds = price_to_cents(ds)

    assert initial_data == ds.result

Not much changed, but only on the surface. ``ds`` is now not a list, but an instance of ``FunctionModifier``
you can access the initial list using ``ds.result`` field.

Computation flow didn't change. ``ds.result`` is not lazy and is still computed immediately as before.

Benefits of tracking functional data pipelines
**********************************************

Here are some things you immediately get when using Cascade to track your datasets.

* Store the pipeline locally
* Version each change automatically
* Validate input fields
* Document useful metadata


Store the pipeline locally
==========================

You can save the pipeline as is using `DataLine` and version it every time it is computed.

.. code-block:: python

    from cascade.lines import DataLine

    line = DataLine("datasets")
    line.save(ds)

.. invisible-code-block: python

    from cascade.data.functions import FunctionModifier
    assert isinstance(ds, FunctionModifier)
    assert len(ds.result) == 2
    assert ds.result[0]["price_cents"] == 500.0
    assert line.get_version(ds) == "0.1"

Dataset is saved and versioned locally and each version can easily be loaded.

.. code-block:: python

    version = line.get_version(ds)
    loaded_ds = line.load(str(version))

    assert loaded_ds.result == ds.result

Version your data
=================

For example here you can see how data versioning is automatically enabled.

.. code-block:: python

    line.get_version(ds) # 0.1

Validate inputs
===============

If something goes wrong in the inputs, the transformations will not happen with zero additional code. Here for example we use
the wrong input type and validation will not let us make an error.

To enable that you need to update a single thing - type annotation. Here we add a constraint for ``category`` to be ``str``.
Cascade will use this annotation to check inputs every time the pipeline is executed.

.. code-block:: python

    from cascade.data import ValidationError

    @modifier
    def select_category(data, category: str): # We expect category to always be str
        return [item for item in data if item.get("product_category") == category]

    try:
        select_category(ds, 1)
    except ValidationError:
        pass

Document useful metadata
========================

Now let's try changing the example a bit and use features of Cascade to the fullest.

For example here we can add a description, tag, track which category we have used.

.. code-block:: python

    ds = load_data()
    ds.describe("Commerce pricing dataset")
    ds.tag("prices")

    ds = select_category(ds, "Grocery")
    ds.update_meta({"category": "Grocery"})

    ds = price_to_cents(ds)

    line.save(ds)


See also
********

* :ref:`howtos/tags.rst`
* :ref:`howtos/links.rst`
