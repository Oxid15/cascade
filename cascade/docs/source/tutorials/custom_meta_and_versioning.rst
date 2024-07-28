Custom Meta and Versioning
==========================

Metadata is a very flexible tool. It contains lots of useful info by default,
and can be customized.

In previous steps of the tutorial we created a dataset with an important
parameter, that was not recorded in our meta. If it changes in code, we wouldn't
see the effect in our logs. Now we can fix that issue.

.. code-block:: python
    from cascade.lines import DataLine

    ds.update_meta(
        {
            "long_description": "This is digits pipeline. It was augmented with some uniform noise",
            "noise_magnitude": NOISE_MAGNITUDE,
        }
    )

DataLines are the same thing as ModelLine but for data pipelines. You can use
them to track only metadata of your pipelines or even save and load whole pipelines
to reproduce an experiment.

.. code-block:: python

    dataline = DataLine("dataline")
    dataline.save(ds)

Unlike models, data pipelines are not numbered, but versioned.
Versions are derived from metadata of a pipeline and consist of two
parts - major and minor.

Let's see how it works.

.. code-block:: python

    version = dataline.get_version(ds)
    print(version) # 0.1

Starting version is `0.1` and then, when metadata changes,
parts of the version are bumped automatically. When saving
the version of a dataset that already exists, line will
notice that and overwrite older record with a new object.

.. code-block:: python

    ds.update_meta({"detail_i_almost_forgot": "Changes in meta bump minor version"})
    version = dataline.get_version(ds)
    print(version) # 0.2

    dataline.save(ds)

In previous example minor version was bumped by changing the part of the
pipeline's meta.

In the next one we add a new pipeline stage, which is what will bump
a major part of the version and we will see `1.0`.

.. code-block:: python

    changed_ds = ApplyModifier(ds, add_noise)
    dataline.save(changed_ds)
    version = dataline.get_version(changed_ds)
    print(version) # 1.0

If we plug in an old dataset it will still get us the same version.
As long as meta is the same. Using version string we can load saved 
pipeline object from disk.

.. code-block:: python

    version = dataline.get_version(ds)
    print(version) # 0.2

    loaded_ds = dataline.load("0.2")
    version = dataline.get_version(loaded_ds)
    print(version) # 0.2
