# %% [markdown]
# # Dataset Zoo
# Cascade by itself is **DIY ML-engineering solution**. This means that it provides certain basics on top of which you can easily build own ML-workflow.  
#   
# Cascade has plenty of solutions - basic that are added to the core and more specific that are in the special `utils` module. And if you didn't found suitable component, you can write it yourself.  
#   
# Here some of already-made components are presented. These are the `Dataset`s - building blocks of Cascade's pipelines, their description and short examples of how to use them in your workflow.

# %%
import cascade

print(cascade.__version__)

# %% [markdown]
# ## Wrappers
# [Wrapper documentation](../cascade.data.html#cascade.data.Wrapper)  
#   
# If your solution has some data source that is already accesible in python-code, but you need to plug it in Cascade's workflow it may be all you need. `Wrapper` gives the items from the source one by one, adding some info about the undelying data to its metadata.

# %%
from cascade import data as cdd

ds = cdd.Wrapper([0, 1, 2, 3, 4]) # Here for simplicity the list of numbers is a data source

for item in ds:
    print(item, end=' ')

# %%
ds.get_meta()

# %% [markdown]
# ## Iterators
# [Iterator documentation](../cascade.data.html#cascade.data.Iterator)  
#   
# If data source doesn't have length - you cannot use `Wrapper`s, but it is not a problem, you can use `Iterator`s instead! It is basically the same dataset, but using different interface.

# %%
from cascade import data as cdd


def gen():
    for number in range(5):
        yield number

ds = cdd.Iterator(gen())

for item in ds:
    print(item, end=' ')

# %% [markdown]
# ## ApplyModifier
# [ApplyModifier documentation](../cascade.data.html#cascade.data.ApplyModifier)  
#   
# The pipelines are frequently applying some python-functions to the items in datasets. In Cascade this is done by using `ApplyModifier`.

# %%
from cascade import data as cdd


# The function that will be applied
def square(x):
    return x ** 2

ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.ApplyModifier(ds, square) # ds now a pipeline of two stages

for item in ds:
    print(item, end=' ')

# %% [markdown]
# ## Concatenator
# [Concatenator documentation](../cascade.data.html#cascade.data.Concatenator)  
#   
# Concatenation is also frequent operation that is done to unify several datasets into one. In Cascade it is done easily using `Concatenator`.

# %%
from cascade import data as cdd

ds_1 = cdd.Wrapper([0, 1, 2, 3, 4])
ds_2 = cdd.Wrapper([5, 6, 7, 8, 9])

ds = cdd.Concatenator((ds_1, ds_2))

for item in ds:
    print(item, end=' ')

# %% [markdown]
# In addition, it also stores metadata of all its datasets.

# %%
ds.get_meta()

# %% [markdown]
# ## split
# [split documentation](../cascade.data.html#cascade.data.split)  
#   
# This is the opposite of concatenate - we can split one dataset into train and test parts easily with `cdd.split()`

# %%
from cascade import data as cdd

ds = cdd.Wrapper([0, 1, 2, 3, 4, 5, 6, 7])
train_ds, test_ds = cdd.split(ds, 0.8)

for item in train_ds:
    print(item, end=' ')
print()
for item in test_ds:
    print(item, end=' ')

# %% [markdown]
# Basically, this function creates two RangeSampler dividing input dataset into two parts.

# %%
train_ds.get_meta()

# %% [markdown]
# ## Composer
# [Composer documentation](../cascade.data.html#cascade.data.Composer)  
# 
# Composer is another way of unifying two datasets, but in this case the union dataset returns tuples of item from composed datasets. This is useful, when items and labels for classification are from different datasets.

# %%
from cascade import data as cdd

items = cdd.Wrapper(['A', 'B', 'C', 'D'])
labels = cdd.Wrapper([0, 1, 0, 1])

ds = cdd.Composer((items, labels))

[item for item in ds]

# %% [markdown]
# ## CyclicSampler
# [CyclicSampler documentation](../cascade.data.html#cascade.data.CyclicSampler)  
#   
# When you need an easy way to repeat your dataset several times or the opposite - restrict the number of items in dataset, you can use this.

# %%
from cascade import data as cdd

ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.CyclicSampler(ds, 11)

for item in ds:
    print(item, end=' ')

# %% [markdown]
# ## RandomSampler
# [RandomSampler documentation](../cascade.data.html#cascade.data.RandomSampler)  
#   
# Undeterministic counterpart of CyclicSampler. Ideal solution for shuffling the data in lazy way.

import numpy as np

# %%
from cascade import data as cdd

np.random.seed(0)


ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.RandomSampler(ds, 11)

for item in ds:
    print(item, end=' ')

# %% [markdown]
# With no arguments - shuffles the dataset.

# %%
ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.RandomSampler(ds)

for item in ds:
    print(item, end=' ')

# %% [markdown]
# ## RangeSampler
# [RangeSampler documentation](../cascade.data.html#cascade.data.RangeSampler)  
#   
# This is if you need python's range in Cascade realm. Has just similar interface as `range`.

# %%
from cascade import data as cdd

ds = cdd.Wrapper([0, 1, 2, 3, 4 , 5, 6, 7, 8, 9, 10])
ds = cdd.RangeSampler(ds, 1, 10, 2)

for item in ds:
    print(item, end=' ')

# %% [markdown]
# ## BruteforceCacher
# [BruteforceCacher documentation](../cascade.data.html#cascade.data.BruteforceCacher)  
#   
# Modifiers are lazy and not storing all data in memory. This is important when datasets are big and do not fit into memory, but can slow down some processes. If your data fits into memory, you can cache previous stages of pipeline to speed up next stages.  
#   
# Suppose for example that we need to obtain our data through very slow network

# %%
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

# %% [markdown]
# Now we waited all loading process and cached everything. Since that all data is in memory and the loading is no problem.
# But what if we have a script that should be executed every time and then caching has no sense?

# %% [markdown]
# ## Pickler
# [Pickler documentation](../cascade.data.html#cascade.data.Pickler)  
#   
# 
# For these purposes `Pickler` was implemented. You can cache and then pickle previous pipeline on the disk, then load it and use without problems. 

# %%
ds = LongLoadingDataSource(10)
ds = cdd.BruteforceCacher(ds)
ds = cdd.Pickler('ds.pkl', ds)

# %%
from tqdm import tqdm

ds = cdd.Pickler('ds.pkl')

for item in tqdm(ds):
    print(item, end=' ')

# %% [markdown]
# Note that after unpickling we don't need to wait for loading again.

# %% [markdown]
# ## VersionAssigner
# [VersionAssigner documentation](../cascade.data.html#cascade.data.VersionAssigner)  
#   
# Dataset versioning is the way to compress whole information about a pipeline into human-readable form of semantically significant numbers separated by a dot.  
# The principle is basically the same as in SemVer - the version structure is `MAJOR.MINOR`. The first component changes when the change is in the pipeline composition i.e. some modifiers added/deleted. The second changes when any field of meta data changes.  
# VersionAssigner tracks versions using special log file, which can be used by the user to determine which kind of dataset corresponds to which version.

# %%
from cascade import data as cdd

ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.VersionAssigner(ds, 'data_log.yml', verbose=True)

# %%
# Change its structure - add new modifier
ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.RangeSampler(ds, 0, len(ds), 2)
ds = cdd.VersionAssigner(ds, 'data_log.yml', verbose=True)


# %%
# Revert changes - version downgrades back using records
# in the data_log
ds = cdd.Wrapper([0, 1, 2, 3, 4])
ds = cdd.VersionAssigner(ds, 'data_log.yml', verbose=True)


# %%
# Update input data - minor update
ds = cdd.Wrapper([0, 1, 2, 3, 4, 5])
ds = cdd.VersionAssigner(ds, 'data_log.yml', verbose=True)

# %% [markdown]
# ## OverSampler and UnderSampler
# [OverSampler documentation](../cascade.utils.html#cascade.utils.samplers.OverSampler)  
# [UnderSampler documentation](../cascade.utils.html#cascade.utils.samplers.UnderSampler)  
#   
# These sampling strategies placed into utils module because they make quite big assumtions about datasets - that they emit tuples and the second element of each tuple is a classification label. 
#    
# Using that labels they equalize label distribution by repeating or deleting some elements. The sampler themselves are lazy, but to obtain label distribution, they load elements one-by-one not storing them in memory in initialization.  
#   
# They are also deterministic and place elements with similar labels together. Consider using `RandomSampler` to shuffle datasets before passing them to learning.

# %%
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

# %%
from cascade.utils.samplers import UnderSampler

ds = cdd.Wrapper([
    ('a', 0),
    ('b', 1),
    ('c', 1),
    ('d', 2),
])

ds = UnderSampler(ds)
[item for item in ds]

# %% [markdown]
# ## WeighedSampler
# [WeighedSampler documentation](../cascade.utils.html#cascade.utils.samplers.WeighedSampler)  
# 
# If you need more freedom in how to sample your data according to the label you have, you can use this

# %%
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

# %% [markdown]
# ## Specific datasets
#   
# Some data types require specific functionality from its dataset wrapper. Some wrappers are already implemented and contain a number of useful tools and features.

# %% [markdown]
# ### TimeSeriesDataset
# [TimeSeriesDataset documentation](../cascade.utils.html#cascade.utils.time_series.TimeSeriesDataset)  
# 
# One `TimeSeriesDataset` contains whole time series data. They require separate time and data channels to initialize.

# %%
import datetime

from cascade.utils.time_series import TimeSeriesDataset

ds = TimeSeriesDataset(time=[
    datetime.datetime(2022, 11, 5),
    datetime.datetime(2022, 11, 6),
    datetime.datetime(2022, 11, 7),
], data=[0, 1, 2])

ds.to_pandas()

# %% [markdown]
# The important thing about these datasets is that they *always should be initialized with keywords*. The usage of `time` and `data` is mandatory for dataset to work. The same applies to other specific datasets such as TableDataset and its keyword `t` for table.

# %%
ds = TimeSeriesDataset([
    datetime.datetime(2022, 11, 5),
    datetime.datetime(2022, 11, 6),
    datetime.datetime(2022, 11, 7),
], [0, 1, 2])

ds.to_pandas()

# %% [markdown]
# This is due to unification of two interfaces in `Modifier`s for these datasets. A `Modifier` should be also `TimeSeriesDataset`. 
#    
# Let's initialize ds again:

# %%
ds = TimeSeriesDataset(time=[
    datetime.datetime(2022, 11, 5),
    datetime.datetime(2022, 11, 6),
    datetime.datetime(2022, 11, 7),
    datetime.datetime(2022, 11, 8),
], data=[1, 0, 2, 5])

# %% [markdown]
# You can use several convenience access methods such as any type of indexing: using integers or dates.

# %%
ds[2]

# %%
ds[datetime.datetime(2022, 11, 7)]

# %% [markdown]
# The slices are also available.

# %%
ds[1:].to_pandas() # Using integers

# %%
ds[datetime.datetime(2022, 11, 6):].to_pandas() # Or using time

# %% [markdown]
# Note that every slice returns new `TimeSerisDataset` instance.

# %% [markdown]
# There is always a general way to extract all data, which is most useful for plotting data.

# %%
ds.get_data()

# %%
# Install matplotlib if required
# !pip3 install matplotlib

# %%
from matplotlib import pyplot as plt

plt.plot(*ds.get_data())

# %% [markdown]
# You can always get the data alone using `to_numpy()`

# %%
ds.to_numpy()

# %% [markdown]
# Interpolation in case of any missing data is crucial when working with real-life time series. Here it is implemented in `Modifier`.  
#   
# First - dataset is initialized with nan-value. Nan-value is `numpy.nan` because Interpolate uses pandas under-the-hood.

# %%
import numpy as np

ds = TimeSeriesDataset(time=[
    datetime.datetime(2022, 11, 5),
    datetime.datetime(2022, 11, 6),
    datetime.datetime(2022, 11, 7),
], data=[0, np.nan, 2])

ds.to_pandas()

# %%
from cascade.utils.time_series import Interpolate

Interpolate(ds, method='linear', limit_direction='both').to_pandas() # These arguments are defaults

# %% [markdown]
# Averaging over some time-window is also a frequent task in work with time-series. Here in `Average` you can set the time grain and a quantity to average.

# %%
import pendulum

ds = TimeSeriesDataset(time=[
    pendulum.datetime(2022, 11, 5),
    pendulum.datetime(2022, 11, 6),
    pendulum.datetime(2022, 11, 7),
    pendulum.datetime(2022, 11, 8),
], data=[0, 1, 2, 3])

# %%
from cascade.utils.time_series import Average

Average(ds, unit='days', amount=2).to_pandas()

# %%
from cascade.utils.time_series import Align

Align(ds, [pendulum.datetime(2022, 11, 8)]).to_pandas()

# %% [markdown]
# ### TableDataset
# [TableDataset documentation](../cascade.utils.html#cascade.utils.tables.TableDataset)  
# 
#   
# Frequently the work with tables is done. To track them efficiently using Cascade this wrapper was created.

# %%
import pandas as pd
from cascade.utils.tables import TableDataset

ds = TableDataset(t=pd.DataFrame(data=[[2, 0], [1, 0], [1, 0]]))
ds

# %% [markdown]
# The most important thing here is the extensive metadata that this wrapper holds.

# %%
ds.get_meta()

# %% [markdown]
# Filtering is common when using tables. This modifier accepts binary mask and records new stage in the pipeline's metadata.

# %%
from cascade.utils.tables import TableFilter

ds = TableFilter(ds, ds._table[0] == 1)

# %%
ds.get_meta()

# %% [markdown]
# ## More to come
# Cascade is rapidly developing and shaped to the needs of its users, so there are more new tools to come!


