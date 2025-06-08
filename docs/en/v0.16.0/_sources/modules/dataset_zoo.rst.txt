Dataset Zoo
###########

Cascade has many solutions - basic that are added to the core and more specific
that are in the special ``utils`` module. And if you didn't found suitable component,
you can write it yourself.

Here some of already-made components are presented. These are the ``Dataset``s - building
blocks of Cascade's pipelines, their description and short examples of
how to use them in your workflow.

Wrappers
********

If your solution has some data source that is already accesible in python-code, but you
need to plug it in Cascade's workflow it may be all you need. ``Wrapper`` gives the items
from the source one by one, adding some info about the undelying data to its metadata.

.. code-block:: python

    from cascade.data import Wrapper

    ds = Wrapper([0, 1, 2, 3, 4])

    for item in ds:
        print(item, end=' ')

Iterators
********

If data source doesn't have length - you cannot use ``Wrapper``s, but it is not a problem,
you can use ``Iterator``s instead! It is basically the same dataset, but using different interface.

.. code-block:: python

    from cascade import data as cdd

    def gen():
        for number in range(5):
            yield number

    ds = cdd.Iterator(gen())

    for item in ds:
        print(item, end=' ')


ApplyModifier
*************

The pipelines are frequently applying some python-functions to the items in datasets.
In Cascade this is done by using ``ApplyModifier``.

.. code-block:: python

    from cascade import data as cdd


    The function that will be applied
    def square(x):
        return x ** 2

    ds = cdd.Wrapper([0, 1, 2, 3, 4])
    ds = cdd.ApplyModifier(ds, square) ds now a pipeline of two stages

    for item in ds:
        print(item, end=' ')


Concatenator
************

Concatenation is also frequent operation that is done to unify several datasets
into one. In Cascade it is done easily using ``Concatenator``.

.. code-block:: python

    from cascade import data as cdd

    ds_1 = cdd.Wrapper([0, 1, 2, 3, 4])
    ds_2 = cdd.Wrapper([5, 6, 7, 8, 9])

    ds = cdd.Concatenator((ds_1, ds_2))

    for item in ds:
        print(item, end=' ')


In addition, it also stores metadata of all its datasets.

split
*****

This is the opposite of concatenate - we can split one dataset into train and
test parts easily with ``cdd.split()``

.. code-block:: python

    from cascade import data as cdd

    ds = cdd.Wrapper([0, 1, 2, 3, 4, 5, 6, 7])
    train_ds, test_ds = cdd.split(ds, 0.8)

    for item in train_ds:
        print(item, end=' ')
    print()
    for item in test_ds:
        print(item, end=' ')


Basically, this function creates two RangeSampler dividing input dataset into two parts.


Composer
********

Composer is another way of unifying two datasets, but in this case the
union dataset returns tuples of item from composed datasets. This is useful,
when items and labels for classification are from different datasets.

.. code-block:: python

    from cascade import data as cdd

    items = cdd.Wrapper(['A', 'B', 'C', 'D'])
    labels = cdd.Wrapper([0, 1, 0, 1])

    ds = cdd.Composer((items, labels))

    [item for item in ds]


CyclicSampler
********

When you need an easy way to repeat your dataset several times or the opposite -
restrict the number of items in dataset, you can use this.

.. code-block:: python

    from cascade import data as cdd

    ds = cdd.Wrapper([0, 1, 2, 3, 4])
    ds = cdd.CyclicSampler(ds, 11)

    for item in ds:
        print(item, end=' ')


RandomSampler
********

Undeterministic counterpart of CyclicSampler. Ideal solution for shuffling the data in lazy way.

import numpy as np

.. code-block:: python

    from cascade import data as cdd

    np.random.seed(0)


    ds = cdd.Wrapper([0, 1, 2, 3, 4])
    ds = cdd.RandomSampler(ds, 11)

    for item in ds:
        print(item, end=' ')


With no arguments - shuffles the dataset.

.. code-block:: python

    ds = cdd.Wrapper([0, 1, 2, 3, 4])
    ds = cdd.RandomSampler(ds)

    for item in ds:
        print(item, end=' ')


RangeSampler
************

This is if you need python's range in Cascade realm. Has just similar interface as ``range``.

.. code-block:: python

    from cascade import data as cdd

    ds = cdd.Wrapper([0, 1, 2, 3, 4 , 5, 6, 7, 8, 9, 10])
    ds = cdd.RangeSampler(ds, 1, 10, 2)

    for item in ds:
        print(item, end=' ')


BruteforceCacher
****************

Modifiers are lazy and not storing all data in memory. This is important when datasets
are big and do not fit into memory, but can slow down some processes. If your data fits
into memory, you can cache previous stages of pipeline to speed up next stages.
  
Suppose for example that we need to obtain our data through very slow network

.. code-block:: python

    import time


    class LongLoadingDataSource(cdd.Dataset):
        def __init__(self, length, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._length = length

        def __getitem__(self, index):
            time.sleep(1)
            return index
        
        def __len__(self):
            return self._length

    ds = LongLoadingDataSource(10)
    ds = cdd.BruteforceCacher(ds)


Now we waited all loading process and cached everything. Since that all data is in memory and the loading is no problem.
But what if we have a script that should be executed every time and then caching has no sense?


Pickler
*******

For these purposes ``Pickler`` was implemented. You can cache and then pickle previous pipeline on the disk,
then load it and use without problems. 

.. code-block:: python

    ds = LongLoadingDataSource(10)
    ds = cdd.BruteforceCacher(ds)
    ds = cdd.Pickler('ds.pkl', ds)

.. code-block:: python

    from tqdm import tqdm

    ds = cdd.Pickler('ds.pkl')

    for item in tqdm(ds):
        print(item, end=' ')


Note that after unpickling we don't need to wait for loading again.


OverSampler and UnderSampler
****************************

These sampling strategies placed into utils module because they make quite big assumtions about datasets - that
they emit tuples and the second element of each tuple is a classification label. 
   
Using that labels they equalize label distribution by repeating or deleting some elements. The sampler themselves
are lazy, but to obtain label distribution, they load elements one-by-one not storing them in memory in initialization.  
  
They are also deterministic and place elements with similar labels together. Consider using ``RandomSampler`` to
shuffle datasets before passing them to learning.

.. code-block:: python

    from cascade import data as cdd
    from cascade.utils.samplers import OverSampler

    ds = cdd.Wrapper([
        ('a', 0),
        ('b', 1),
        ('c', 1),
        ('d', 2),
    ])

    ds = OverSampler(ds)
    [item for item in ds]

.. code-block:: python

    from cascade.utils.samplers import UnderSampler

    ds = cdd.Wrapper([
        ('a', 0),
        ('b', 1),
        ('c', 1),
        ('d', 2),
    ])

    ds = UnderSampler(ds)
    [item for item in ds]


WeighedSampler
**************

If you need more freedom in how to sample your data according to the label you have, you can use this

.. code-block:: python

    from cascade import data as cdd
    from cascade.utils.samplers import WeighedSampler

    ds = cdd.Wrapper([
        ('A', 0),
        ('B', 0),
        ('C', 1),
        ('D', 2),
    ])

    ds = WeighedSampler(ds, partitioning={
        0: 4,
        1: 2
    })

    [item for item in ds]


Specific datasets
*****************
  
Some data types require specific functionality from its dataset wrapper. Some wrappers are already implemented and
contain a number of useful tools and features.


TimeSeriesDataset
=================
``TimeSeriesDataset`` contains whole time series data. They require separate time and data channels to initialize.

.. code-block:: python

    import datetime

    from cascade.utils.time_series import TimeSeriesDataset

    ds = TimeSeriesDataset(time=[
        datetime.datetime(2022, 11, 5),
        datetime.datetime(2022, 11, 6),
        datetime.datetime(2022, 11, 7),
    ], data=[0, 1, 2])

    ds.to_pandas()


The important thing about these datasets is that they *always should be initialized with keywords*. The usage
of ``time`` and ``data`` is mandatory for dataset to work. The same applies to other specific datasets such as
TableDataset and its keyword ``t`` for table.

.. code-block:: python

    ds = TimeSeriesDataset([
        datetime.datetime(2022, 11, 5),
        datetime.datetime(2022, 11, 6),
        datetime.datetime(2022, 11, 7),
    ], [0, 1, 2])

    ds.to_pandas()


This is due to unification of two interfaces in ``Modifier``s for these datasets. A ``Modifier`` should be also ``TimeSeriesDataset``. 
   
Let's initialize ds again:

.. code-block:: python

    ds = TimeSeriesDataset(time=[
        datetime.datetime(2022, 11, 5),
        datetime.datetime(2022, 11, 6),
        datetime.datetime(2022, 11, 7),
        datetime.datetime(2022, 11, 8),
    ], data=[1, 0, 2, 5])


You can use several convenience access methods such as any type of indexing: using integers or dates.

.. code-block:: python

    ds[2]

.. code-block:: python

    ds[datetime.datetime(2022, 11, 7)]


The slices are also available.

.. code-block:: python

    ds[1:].to_pandas() Using integers

.. code-block:: python

    ds[datetime.datetime(2022, 11, 6):].to_pandas() Or using time


Note that every slice returns new ``TimeSerisDataset`` instance.


There is always a general way to extract all data, which is most useful for plotting data.

.. code-block:: python

    ds.get_data()

.. code-block:: python

Install matplotlib if required

.. code-block:: python

    pip3 install matplotlib

.. code-block:: python

    from matplotlib import pyplot as plt

    plt.plot(*ds.get_data())


You can always get the data alone using ``to_numpy()``

.. code-block:: python

    ds.to_numpy()


Interpolation in case of any missing data is crucial when working with real-life time series. Here it is implemented in ``Modifier``.  
  
First - dataset is initialized with nan-value. Nan-value is ``numpy.nan`` because Interpolate uses pandas under-the-hood.

.. code-block:: python

    import numpy as np

    ds = TimeSeriesDataset(time=[
        datetime.datetime(2022, 11, 5),
        datetime.datetime(2022, 11, 6),
        datetime.datetime(2022, 11, 7),
    ], data=[0, np.nan, 2])

    ds.to_pandas()

.. code-block:: python

    from cascade.utils.time_series import Interpolate

    Interpolate(ds, method='linear', limit_direction='both').to_pandas() These arguments are defaults


Averaging over some time-window is also a frequent task in work with time-series. Here in ``Average`` you
can set the time grain and a quantity to average.

.. code-block:: python

    import pendulum

    ds = TimeSeriesDataset(time=[
        pendulum.datetime(2022, 11, 5),
        pendulum.datetime(2022, 11, 6),
        pendulum.datetime(2022, 11, 7),
        pendulum.datetime(2022, 11, 8),
    ], data=[0, 1, 2, 3])

.. code-block:: python

    from cascade.utils.time_series import Average

    Average(ds, unit='days', amount=2).to_pandas()

.. code-block:: python

    from cascade.utils.time_series import Align

    Align(ds, [pendulum.datetime(2022, 11, 8)]).to_pandas()


TableDataset
============

Frequently the work with tables is done. To track them efficiently using Cascade this wrapper was created.

.. code-block:: python

    import pandas as pd
    from cascade.utils.tables import TableDataset

    ds = TableDataset(t=pd.DataFrame(data=[[2, 0], [1, 0], [1, 0]]))


The most important thing here is the extensive metadata that this wrapper holds.

.. code-block:: python

    ds.get_meta()


Filtering is common when using tables. This modifier accepts binary mask and records new stage in the pipeline's metadata.

.. code-block:: python

    from cascade.utils.tables import TableFilter

    ds = TableFilter(ds, ds._table[0] == 1)

.. code-block:: python

    ds.get_meta()


More to come
************

Cascade is rapidly developing and shaped to the needs of its users, so there are more new tools to come!
