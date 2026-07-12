Track Dataset Errors
####################

.. important::

   This functionality was introduced in Cascade `0.17.0`

There are some cases when working with real life datasets when the error occurs in a random unexpected place.
For example when you have a broken file somewhere in the middle of a large dataset or you have a bug in a pipeline that raises an exception in only 1% of cases.
Such situations are not infrequent in practice and can be very hard to debug. In this how-to the mechanism of error tracking in Cascade pipelines is described.

Consider the following pipeline:

.. code-block:: python

   from cascade.data import Dataset, Modifier


   class RaiseDatasetOverridingGetItem(Dataset):
      def __getitem__(self, index):
         if index == 1:
               raise RuntimeError("on no!")
         else:
               return 0

      def __len__(self):
         return 2


   class ModifierOverridingGetItem(Modifier):
      def __getitem__(self, index):
         return self._dataset[index]


   ds = RaiseDatasetOverridingGetItem()
   ds = ModifierOverridingGetItem(ds)

   for i in range(len(ds)):
      ds[i]

Here we have dummy Dataset and Modifier both overriding default `__getitem__` method. When we execute the code we see only the error message and will require additional runs to trace where exactly the error occured. In case of large datasets and long trainings it can be very costly to run second time to check where the error occurs.

.. code-block:: python

   Traceback (most recent call last):
   File "/home/user/example.py", line 24, in <module>
      ds[i]
      ~~^^^
   File "/home/user/example.py", line 17, in __getitem__
      return self._dataset[index]
            ~~~~~~~~~~~~~^^^^^^^
   File "/home/user/example.py", line 7, in __getitem__
      raise RuntimeError("on no!")
   RuntimeError: on no!


Let's try a simple update - replace all `__getitem__` with `get` methods:

.. code-block:: python

   Traceback (most recent call last):
   File "/home/user/cascade/cascade/data/dataset.py", line 107, in __getitem__
      return self.get(index)
            ^^^^^^^^^^^^^^^
   File "/home/user/example.py", line 33, in get
      raise RuntimeError("on no!")
   RuntimeError: on no!

   The above exception was the direct cause of the following exception:

   Traceback (most recent call last):
   File "/home/user/cascade/cascade/data/dataset.py", line 107, in __getitem__
      return self.get(index)
            ^^^^^^^^^^^^^^^
   File "/home/user/example.py", line 43, in get
      return self._dataset[index]
            ~~~~~~~~~~~~~^^^^^^^
   File "/home/user/cascade/cascade/data/dataset.py", line 106, in __getitem__
      with GetItemHandler(self, index):
   File "/home/user/cascade/cascade/data/dataset.py", line 36, in __exit__
      raise GetItemException(
   cascade.data.dataset.GetItemException: Failed to get item from <class '__main__.RaiseDataset'> at index 1

   The above exception was the direct cause of the following exception:

   Traceback (most recent call last):
   File "/home/user/example.py", line 50, in <module>
      ds[i]
      ~~^^^
   File "/home/user/cascade/cascade/data/dataset.py", line 106, in __getitem__
      with GetItemHandler(self, index):
   File "/home/user/cascade/cascade/data/dataset.py", line 36, in __exit__
      raise GetItemException(
   cascade.data.dataset.GetItemException: Failed to get item from <class '__main__.ModifierWithGet'> at index 1

From the traceback like this we can clearly see that the error originates in the dataset at index 1 and then proparates to modifier at the same index.
In our simplified example it is obvious what the index is and that it is the same for all pipeline steps but in real life with different samplers, dataloaders and lots of steps it can be hard to trace the error to a datapoint.

This approach should help diagnosing such things and should became a standard approach in developing custom Datasets going forward.
