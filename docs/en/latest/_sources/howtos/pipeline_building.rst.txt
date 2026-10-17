Pipeline building
#################

This use case shows how to prepare an MNIST dataset for training a classifier
with Cascade's data pipeline components.

Imports
*******

The example uses PyTorch, torchvision, and ``cascade.data``.

.. code-block:: python

    import torch
    import torchvision
    import cascade.data as cdd
    import torchvision.transforms.functional as F

Load the PyTorch dataset
*************************

Load the training and test partitions of MNIST. Set ``download=True`` for the
training partition when the dataset is not already available locally.

.. skip: next

.. code-block:: python

    MNIST_ROOT = "data"

    train_ds = torchvision.datasets.MNIST(
        root=MNIST_ROOT,
        train=True,
        transform=F.to_tensor,
        download=True,
    )
    test_ds = torchvision.datasets.MNIST(
        root=MNIST_ROOT,
        train=False,
        transform=F.to_tensor,
    )

Creating a Cascade dataset
****************************

Wrap the PyTorch datasets to add Cascade metadata. The description is attached
to the training dataset and remains available through later pipeline stages.

.. skip: next

.. code-block:: python

    train_ds = cdd.Wrapper(train_ds)
    train_ds.describe("This is MNIST dataset of handwritten images")
    test_ds = cdd.Wrapper(test_ds)

Applying noise
**************

Modifiers transform items lazily as they are read. This modifier adds a small
amount of random noise to each image.

.. skip: next

.. code-block:: python

    class NoiseModifier(cdd.Modifier):
        def get(self, index):
            img, label = self._dataset[index]
            img += torch.rand_like(img) * 0.1
            img = torch.clip(img, 0, 255)
            return img, label

    train_ds = NoiseModifier(train_ds)

Viewing metadata
****************

Each modifier adds a stage to the dataset metadata. Use ``pprint`` when
inspecting the complete metadata interactively.

.. skip: next

.. code-block:: python

    from pprint import pprint

    pprint(train_ds.get_meta())

Ready to train a model
**********************

Pass the Cascade datasets to standard PyTorch ``DataLoader`` instances.

.. skip: next

.. code-block:: python

    BATCH_SIZE = 10

    trainldr = torch.utils.data.DataLoader(
        dataset=train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )
    testldr = torch.utils.data.DataLoader(
        dataset=test_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )
