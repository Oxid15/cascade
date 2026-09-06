Model training
##############

This use case demonstrates how to use Cascade for metadata tracking,
hyperparameter tuning, and model selection. The example uses a small PyTorch
classifier trained on MNIST.

The pipeline-building part of the example is included without detailed
discussion. See :doc:`pipeline_building` for a more thorough introduction to
Cascade data pipelines.

Imports
*******

The example uses PyTorch and torchvision in addition to Cascade.

.. code-block:: python

    import cascade.data as cdd
    from cascade.utils.torch import TorchModel
    from cascade.utils.sklearn import SkMetric
    from tqdm import tqdm
    import torch
    import torchvision
    from torchvision.transforms import functional as F
    from torch import nn

Cascade exposes its installed version through ``cascade.__version__``.

Data pipeline
*************

The data pipeline loads MNIST, wraps the datasets with Cascade metadata, and
adds noise to each image.

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

Module definition
*****************

The model is a simple two-layer neural network.

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

Cascade wrapper
***************

``Classifier`` adapts the PyTorch training and evaluation loops to Cascade's
model interface. Training parameters passed as keywords are recorded in the
model metadata.

.. code-block:: python

    class Classifier(TorchModel):
        def fit(self, train_dl, num_epochs, lr, *args, **kwargs):
            criterion = nn.CrossEntropyLoss()
            optim = torch.optim.Adam(self._model.parameters(), lr=lr)
            ds_size = len(train_dl)
            for epoch in range(num_epochs):
                for x, (imgs, labels) in enumerate(train_dl):
                    imgs = imgs.reshape(-1, self._model.input_size)
                    out = self._model(imgs)
                    loss = criterion(out, labels)
                    optim.zero_grad()
                    loss.backward()
                    optim.step()
                    if x % 500 == 0:
                        print(
                            f"Epochs [{epoch}/{num_epochs}], "
                            f"Step[{x}/{ds_size}], Loss: {loss.item():.4f}"
                        )

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

Model training
**************

The wrapper accepts the model class and the parameters needed to initialize
it. Additional keyword arguments are recorded as training metadata.

.. code-block:: python

    NUM_EPOCHS = 2
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
    model.fit(train_dl, NUM_EPOCHS, LR)

Evaluate the model
******************

Evaluation populates the model's metrics rather than returning a value.

.. code-block:: python

    model.evaluate(test_dl, [SkMetric("accuracy_score")])

Check the metadata
******************

The metadata contains the model parameters and the metric recorded during
evaluation.

.. code-block:: python

    from pprint import pprint

    pprint(model.get_meta())

.. invisible-code-block: python

    metadata = model.get_meta()[0]
    assert sorted(metadata["params"]) == [
        "bs",
        "hidden_size",
        "input_size",
        "lr",
        "num_classes",
        "num_epochs",
    ]
    assert metadata["metrics"][0].name == "accuracy_score"

Saving the model
****************

Model containers are organized hierarchically as
``Workspace`` -> ``Repo`` -> (``ModelLine``/``DataLine``). A model line
manages experiments with similar architectures.

.. code-block:: python

    from cascade.workspaces import Workspace

    line = (
        Workspace("main")
        .add_repo("tutorial")
        .add_line("linear_nn", type="model")
    )

Link the training dataset to the model before saving it.

.. code-block:: python

    model.link(train_ds)
    line.save(model)

The model and metadata are saved under paths similar to
``repo/linear_nn/00000/model`` and ``repo/linear_nn/00000/meta.json``.

Peeking inside the repository
******************************

The CLI can display selected metadata fields from a repository. The exact
slugs, metric values, timestamps, and query duration vary between runs.

.. code-block:: bash

    cd main
    cascade query slug 'metrics[0].name' 'metrics[0].value'

More experiments
****************

To compare several models, define a parameter grid and save each result to
the same model line.

.. code-block:: python

    params = [
        {"hidden_size": 10, "num_epochs": 2, "lr": 0.001, "bs": 10},
        {"hidden_size": 50, "num_epochs": 2, "lr": 0.001, "bs": 10},
        {"hidden_size": 100, "num_epochs": 2, "lr": 0.001, "bs": 10},
    ]
    for p in params:
        model = Classifier(
            SimpleNN,
            **p,
            input_size=INPUT_SIZE,
            num_classes=10,
        )
        model.fit(train_dl, **p)
        model.evaluate(test_dl, [SkMetric("accuracy_score")])
        line.save(model)

The ``sort`` clause orders experiments by their metric value.

.. code-block:: bash

    cd main
    cascade query slug 'metrics[0].name' 'metrics[0].value' \
        sort 'metrics[0].value' desc
