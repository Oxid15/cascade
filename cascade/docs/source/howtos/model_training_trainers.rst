Model training using trainers
#############################

This use case demonstrates the same model-training workflow as
:doc:`model_training`, using Cascade's ``BasicTrainer`` to handle training,
evaluation, saving, and logging.

Imports
*******

The example uses PyTorch, torchvision, scikit-learn metrics, and Cascade's
PyTorch integration.

.. code-block:: python

    import cascade.data as cdd
    from cascade.utils.torch import TorchModel
    from cascade.utils.sklearn import SkMetric
    from tqdm import tqdm
    import torch
    import torchvision
    from torchvision.transforms import functional as F
    from torch import nn

Defining the data pipeline
****************************

The dataset is wrapped with Cascade metadata, transformed with a noise
modifier, and limited to a fixed number of samples to keep this example
shorter.

.. skip: next

.. code-block:: python

    MNIST_ROOT = "data"
    INPUT_SIZE = 784
    BATCH_SIZE = 10

    class NoiseModifier(cdd.Modifier):
        def get(self, index):
            img, label = self._dataset[index]
            img += torch.rand_like(img) * 0.1
            img = torch.clip(img, 0, 255)
            return img, label

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

    train_ds = cdd.Wrapper(train_ds)
    train_ds.describe("This is MNIST dataset of handwritten images, TRAIN PART")
    test_ds = cdd.Wrapper(test_ds)

    train_ds = NoiseModifier(train_ds)
    test_ds = NoiseModifier(test_ds)

    train_dl = torch.utils.data.DataLoader(
        dataset=train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )
    test_dl = torch.utils.data.DataLoader(
        dataset=test_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

The pipeline metadata includes the sampler, modifier, and wrapped dataset.

.. skip: next

.. code-block:: python

    from pprint import pprint

    pprint(train_ds.get_meta())


Model definition
****************

Define a small neural network for classifying the flattened MNIST images.

.. code-block:: python

    class SimpleNN(nn.Module):
        def __init__(self, input_size, hidden_size, num_classes, *args, **kwargs):
            super().__init__()
            self.input_size = input_size
            self.hidden_size = hidden_size
            self.l1 = nn.Linear(input_size, hidden_size)
            self.l2 = nn.Linear(hidden_size, num_classes)
            self.relu = nn.ReLU()

        def forward(self, y):
            out = self.l1(y)
            out = self.relu(out)
            out = self.l2(out)
            return out

The Cascade wrapper only needs to define one training epoch and evaluation.
``BasicTrainer`` calls these methods once per epoch and handles the surrounding
workflow.

.. code-block:: python

    class Classifier(TorchModel):
        def fit(self, train_dl, lr, *args, **kwargs):
            criterion = nn.CrossEntropyLoss()
            optim = torch.optim.Adam(self._model.parameters(), lr=lr)

            for imgs, labels in train_dl:
                imgs = imgs.reshape(-1, self._model.input_size)
                out = self._model(imgs)
                loss = criterion(out, labels)

                optim.zero_grad()
                loss.backward()
                optim.step()

        def evaluate(self, test_dl, metrics, *args, **kwargs):
            pred = []
            gt = []
            for imgs, labels in tqdm(test_dl):
                imgs = imgs.reshape(-1, self._model.input_size)
                out = torch.argmax(self._model(imgs, *args, **kwargs), -1)
                pred.append(out)
                gt.append(labels)

            pred = torch.concat(pred).detach().numpy()
            gt = torch.concat(gt).detach().numpy()

            for metric in metrics:
                metric.compute(gt, pred)
                self.add_metric(metric)

Model initialization
********************

Parameters required by ``SimpleNN`` initialize the module. Additional keyword
arguments are recorded in the model metadata.

.. skip: next

.. code-block:: python

    NUM_EPOCHS = 5
    LR = 1e-3

    model = Classifier(
        SimpleNN,
        input_size=INPUT_SIZE,
        hidden_size=100,
        num_classes=10,
        num_epochs=NUM_EPOCHS,
        lr=LR,
        bs=BATCH_SIZE,
    )

Set up the trainer
******************

Configure logging and create a ``BasicTrainer``. The trainer stores its
results in the repository named ``trainer_repo``.

.. code-block:: python

    import logging
    import sys

    logging.basicConfig(
        handlers=[logging.StreamHandler(sys.stdout)],
        level="INFO",
    )

    from cascade.trainers import BasicTrainer

    trainer = BasicTrainer("trainer_repo")

Train the model
***************

The first call trains, evaluates, saves, and logs the model. The training and
test keyword arguments are passed to ``Classifier.fit`` and
``Classifier.evaluate`` respectively.

.. skip: next

.. code-block:: python

    trainer.train(
        model,
        train_data=train_dl,
        test_data=test_dl,
        train_kwargs={"lr": LR, "bs": BATCH_SIZE},
        test_kwargs={"metrics": [SkMetric("accuracy_score")]},
        epochs=NUM_EPOCHS,
        start_from=None,
        save_strategy=2,
        eval_strategy=1,
    )

Results
*******

Trainer metadata contains the configured epoch and evaluation settings, as
well as timestamps for the run.

.. code-block:: python

    from pprint import pprint

    pprint(trainer.get_meta())


Start from a checkpoint
***********************

To continue training from the existing model line, pass its line name through
``start_from``. The trainer resumes from the latest saved model in that line.

.. skip: next

.. code-block:: python

    trainer.train(
        model,
        train_data=train_dl,
        test_data=test_dl,
        train_kwargs={"lr": LR, "bs": BATCH_SIZE},
        test_kwargs={"metrics": [SkMetric("accuracy_score")]},
        epochs=5,
        start_from="00000",
        save_strategy=4,
        eval_strategy=1,
    )

The metrics collected by the trainer can be inspected after training.

.. code-block:: python

    trainer.metrics
