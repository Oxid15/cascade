11. Data Validation
===================

Data quality in ML projects is as important as the quality of the model.
This is why Cascade focuses on integrated and effortless data validation.

When the project grows, it becomes hard to control what is going on with
different Modifiers. Some may accept on certain formats of data and it is
hard to explicitly define those requirements within Modifier API.

This is where SchemaModifiers come in. They are special kind of Modifiers
that allow defining input schema for when we do ``__getitem__``.

Schema is defined using ``pydantic`` - an established tool for data validation
and also an optional dependency, you'll need to install it if you haven't yet.

The problem with our initial setup is that we operated with tuples, making
our schema implicit. If we were to reuse our datasets later, it would be hard
for us or other engineers to quickly grasp the return value layout and it will
also be easy to introduce errors in datasets that will be hard to debug.

Let's define a simple schema for our dataset from the beginning of the tutorial.

.. code-block:: python

    from pydantic import BaseModel

    class LabeledImage(BaseModel):
        image: np.ndarray
        label: int

        # This is for numpy array
        model_config = {"arbitrary_types_allowed": True}

Previous part is how we define schema in pydantic. You can use complex
schemas and Fields to place requirements on the input of your Modifiers.

Let's convert our dataset to a dataset with schema using this modifier.
It will just wrap the input into a model.

This is the entry point of data in our pipeline, so this part is important.
However, we also can ensure data integrity inside of the pipeline.

.. code-block:: python

    from cascade.data import SchemaModifier

    class LabeledImageModifier(SchemaModifier):
        def __getitem__(self, idx):
            image, label = self._dataset[idx]
            return LabeledImage(image=image, label=label)

Here we define a simple constant padding transform that uses our pydantic model
as an input schema for itself. Each time ``self._dataset[idx]`` is called, it will
automatically check the returned value against our model.

.. code-block:: python

    class Pad5(SchemaModifier):
        in_schema = LabeledImage

        def __getitem__(self, idx):
            item = self._dataset[idx]
            image = item.image.reshape((8, 8))
            h, w = image.shape
            new_image = np.zeros((h + 2 * 5, w + 2 * 5))
            new_image[5: 5 + h, 5: 5 + w] = image
            item.image = new_image.flatten()
            return item

Here we build a pipeline and augment our data using padding.

.. code-block:: python

    ds = LabeledImageModifier(ds)
    pad = Pad5(ds)

    ds = Concatenator([pad, ds])

Let's see the output.

.. code-block:: python

    print(ds[0])

Nothing special - validators are made to be effortless. They allow avoiding
writing manual checks in every instance of a dataset. We just define a schema
inside the whole class of datasets and they automatically check values that they
accept. And the return values stay the same.

Next example will show an actual case of input validation.

We will purposefully define some erroneous data to place before our padding transform.
In this case we mess up the type of a label. This seems to be very real practical situation
that would easily pass in our previous setup at would take some time to debug.

.. code-block:: python

    class FreakyImage(BaseModel):
        image: np.array
        label: str

        model_config = {"arbitrary_types_allowed": True}


    class EvilDataset(Dataset):
        def __getitem__(self, idx):
            return FreakyImage(image=np.zeros(18*18), label="hehe")

        def __len__(self):
            return 69

The following code will raise ValidationError, which we will catch and
display the latest message.

.. code-block:: python

    from cascade.data import ValidationError

    evil = EvilDataset()
    evil = Pad5(evil)

    try:
        evil[0]
    except ValidationError as e:
        print(e)


If we comment try/except out and see the whole traceback
(which is very long), we will see the following lines produced for us
by pydantic. 

.. code-block:: text

      Input should be a valid dictionary or instance of LabeledImage 
      [type=model_type, input_value=FreakyImage(image=array([...     0.]), label='hehe'), input_type=FreakyImage]

We can see that we didn't even get to the validation of a label. Our data was rejected
for being freaky enough without that.
