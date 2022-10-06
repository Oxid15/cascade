import os
import logging
from copy import deepcopy
from typing import Iterable, List, Dict, Union

import pendulum
from ..base import Traceable
from ..models import Model, ModelRepo


logger = logging.getLogger(__name__)


class Trainer(Traceable):
    """
    A class that encapsulates training, evaluation and saving of models.
    """
    def __init__(self, repo: Union[ModelRepo, str], *args, **kwargs) -> None:
        """
        Parameters
        ----------
        repo: Union[ModelRepo, str]
            Either repo or path to it
        """
        if isinstance(repo, str):
            self._repo = ModelRepo(repo)
        elif isinstance(repo, ModelRepo):
            self._repo = repo
        else:
            raise TypeError(f'Repo should be either ModelRepo or path, got {type(repo)}')

        self.metrics = []
        super().__init__(*args, **kwargs)

    def train(self, model, *args, **kwargs):
        raise NotImplementedError()

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0]['metrics'] = self.metrics
        meta[0]['repo'] = self._repo.get_meta()
        return meta


class BasicTrainer(Trainer):
    """
    The most common of concrete Trainers.
    Trains a model for a certain amount of epochs.
    Can start from checkpoint if model file exists.
    """
    def __init__(self, repo, *args, **kwargs) -> None:
        super().__init__(repo, *args, **kwargs)

    def train(self,
              model: Model,
              train_data: Iterable,
              test_data: Iterable,
              *args,
              train_kwargs: Dict = None,
              test_kwargs: Dict = None,
              epochs: int = 1,
              start_from: str = None,
              **kwargs) -> None:
        """
        Trains, evaluates and saves given model. If specified, loads model from checkpoint.

        Parameters:
            model: Model
                a model to be trained or which to load from line specified in `start_from`
            train_data: Iterable
                train data to be passed to model's fit()
            test_data: Iterable
                test data to be passed to model's evaluate()
            train_kwargs: Dict, optional
                arguments for fit()
            test_kwargs: Dict, optional
                arguments for evaluate() - the most common is the dict of metrics
            epochs: int, optional
                how many times to repeat training on data
            start_from: str, optional
                name of line from which to start, start from the latest model in line
        """

        if train_kwargs is None:
            train_kwargs = {}
        if test_kwargs is None:
            test_kwargs = {}

        if start_from is not None:
            line_name = start_from
        else:
            line_name = f'{len(self._repo):0>5d}'
            if line_name in self._repo.get_line_names():
                # Name can appear in the repo if the user manually
                # removed the lines from the middle of the repo

                # This will be handled strictly
                # until it will become clear that some solution needed
                raise RuntimeError(f'Line {line_name} already exists in {self._repo}')

        self._repo.add_line(line_name, type(model))
        line = self._repo[line_name]

        if start_from is not None:
            path = os.path.join(line.root, line.model_names[-1])
            model.load(path)

        self._meta_prefix['train_start_at'] = pendulum.now()
        logger.info(f'Training started with parameters: {train_kwargs}')
        logger.info(f'repo is {self._repo}')
        logger.info(f'line is {line_name}')
        if start_from is not None:
            logger.info(f'started from model {len(line) - 1}')
        logger.info(f'training will last {epochs} epochs')

        for epoch in range(epochs):
            model.fit(train_data, **train_kwargs)
            model.evaluate(test_data, **test_kwargs)
            line.save(model)
            self.metrics.append(deepcopy(model.metrics))

            logger.info(f'Epoch {epoch}: {model.metrics}')

        self._meta_prefix['train_end_at'] = pendulum.now()
