Quickstart
==========

Installation
------------
Install latest version using pip directly from main branch

.. code-block:: bash

    pip install cascade-ml

.. note::
    Cascade has a set of optional dependencies, which can be installed with the following commands

    .. code-block:: bash

        pip install cascade-ml[opencv] # Use opencv as image backend
        pip install cascade-ml[pandera] # Validate pandas dataframes with Pandera
        pip install cascade-ml[pil] # Use Pillow as image backend
        pip install cascade-ml[pydantic] # Use data validation modifiers
        pip install cascade-ml[sklearn] # Scikit-learn integration
        pip install cascade-ml[torch] # PyTorch integration
        pip install cascade-ml[view] # Cascade viewers based on dash
        pip install cascade-ml[all] # Installs everything
