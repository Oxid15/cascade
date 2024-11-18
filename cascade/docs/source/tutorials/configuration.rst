Configuration management
########################

Using ``cascade.base.Config`` class and ``cascade run`` CLI command you can:

1. Configure your scripts in code using class definitions
2. Override config values from CLI without modifying the code
3. Attach configs to models as special files
4. Capture and save script logs


Script config
=============

Here is a sample script featuring a Config inside a file called ``config_demo.py``.

To enable configuration you need to define a new class that inherits from ``cascade.base.Config``.

.. code-block:: python

    from cascade.base import Config


    class TrainConfig(Config):
        lr = 1e-6
        batch_size = 16
        total_iterations = 10000
        image_size = (200, 200)


    def use_as_object(cfg: TrainConfig):
        print(f"This config is for {cfg.total_iterations} iterations")


    def use_as_kwargs(lr, batch_size, total_iterations, image_size):
        print(f"Image height is {image_size[0]} and width is {image_size[1]}")


    if __name__ == "__main__":
        cfg = TrainConfig()

        use_as_object(cfg)

        use_as_kwargs(**cfg.to_dict())

.. important::
    In the current implementation Cascade supports only one config object per file.
    However this may change in the future versions.

Now you can leverage overrides without modifying the code using:

.. code-block:: bash

    cascade run config_demo.py --total_iterations 100 --image_size '(24, 24)'

This will display the current config and your overrides like this:

.. code-block:: text

    You are about to run config_demo.py
    The config is:
    {'batch_size': 16,
    'image_size': '<ast.Tuple object at 0x7955885466b0>',
    'lr': 1e-06,
    'total_iterations': 10000}
    The arguments you passed:
    {'image_size': (24, 24), 'total_iterations': 100}
    Confirm? [y/N]:

After confirmation you should see:

.. code-block:: text

    This config is for 100 iterations
    Image height is 24 and width is 24

In overrides you can use any python literal expressions. In other
words you can write simple things like exponentials ``1e-10``,
passing ``None`` or other constants, but nothing that requires evaluation
or the use of variables.

.. note::

    If you want to launch scripts without confirmation just pass `-y` flag.

Configuration tracking
======================

Having the ability to override hardcoded values with CLI is great, but configs
need to be attached to actual experiments they belong to.
When we do ``cascade run`` it actually knows nothing about what kind of experiment is
inside the script. This means that you can use overrides separately even if you do not track
anything in your scripts. However, at the same time it creates tracking problems because only
``run`` knows about overrides and logs and only the script knows about repos and lines.
To address this problem special ``Model`` methods come into play.

Let's see next example, where we use special ``add_config`` method. Notice how
even while having the actual config in code we do not pass it directly to the method.
It is unnecessary since there is underlying communication between ``run`` and the script.

.. code-block:: python

    from cascade.base import Config
    from cascade.lines import ModelLine
    from cascade.models import BasicModel


    class TrainConfig(Config):
        lr = 1e-6
        batch_size = 16
        total_iterations = 10000
        image_size = (200, 200)


    if __name__ == "__main__":
        cfg = TrainConfig()

        line = ModelLine("line", model_cls=BasicModel)
        model = line.create_model()

        model.add_config()

        line.save(model)

You will find your configs at
``line/00000/files/cascade_config.json``
and overrides at ``line/00000/files/cascade_overrides.json``.

.. note::

    ``run`` creates temporary folder for every launch and stores everything there,
    but only for the time script is executing. When you call ``add_config`` it remembers
    the location of the file and saves it when ``line.save`` is called. The functionality is
    very similar to ``add_file`` and under the hood it actually calls ``add_file``.

Logs tracking
=============

Another useful feature of ``run`` is log tracking. Logs are captured line by line and immediately displayed
just as if you would run the script regularly. While displaying logs ``cascade`` also writes them
into the same temporary folder as configs.

Logs tracking is not enabled by default and can be turned on by adding ``--log`` anywhere after ``cascade run`` command.

Error handling
==============

Logs and configs are saved when ``line.save`` is called, but what if an error will occur before that moment?
This will almost always be the case - something may go wrong in the script and ``save`` will never be called.
This is why ``run`` will not delete temporary folder if an error occurs.
Let's see an example.

.. code-block:: python

    from cascade.base import Config


    class TestConfig(Config):
        a = 0
        b = "hello"


    if __name__ == "__main__":
        print("Script is running")
        raise RuntimeError("An error occured!")

We will run the code above with:

.. code-block:: bash

    cascade run run_error_handling -y --log

Skipping the long trackeback this is what you should see:

.. code-block:: text

    cascade.cli.run.RunFailedException: Run of run_error_handling.py failed.
    See traceback above. The config and logs will be kept at
    /home/ilia/local/cascade_proj/cascade_repo/cascade/docs/source/tutorials/.cascade/20241117_154453_72
    for post-mortem analysis

This is what you should find in ``.cascade/20241117_154453_72/logs/cascade_run.log``

.. code-block:: text

    Script is running
    Traceback (most recent call last):
    File "<string>", line 10, in <module>
    RuntimeError: An error occured!

You will also find config and overrides in ``.cascade`` folder.
