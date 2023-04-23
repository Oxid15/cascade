"""
Copyright 2022-2023 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import logging
from typing import Iterable, List, Dict, Union, Any

import pendulum
from ..base import Traceable, raise_not_implemented
from ..models import Model, ModelLine, ModelRepo


logger = logging.getLogger(__name__)


class Trainer(Traceable):
    """
    A class that encapsulates training, evaluation and saving of models.
    """
    def __init__(self, repo: Union[ModelRepo, str], *args: Any, **kwargs: Any) -> None:
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

    def train(self, model: Model, *args: Any, **kwargs: Any) -> None:
        raise_not_implemented('cascade.models.Trainer', 'train')

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
    @staticmethod
    def _find_last_model(model: Model, line: ModelLine) -> None:
        model_num = len(line) - 1
        while True:
            path = os.path.join(line.root, line.model_names[model_num])
            try:
                model.load(path)
                break
            except FileNotFoundError as e:
                logger.warning(f'Model {path} files were not found\n{e}')
                model_num -= 1

                if model_num == -1:
                    raise FileNotFoundError(f'No model files were found in line {line}')

    def train(self,
              model: Model,
              *args: Any,
              train_data: Union[Iterable[Any], None] = None,
              test_data: Union[Iterable[Any], None] = None,
              train_kwargs: Union[Dict[Any, Any], None] = None,
              test_kwargs: Union[Dict[Any, Any], None] = None,
              epochs: int = 1,
              start_from: Union[str, None] = None,
              eval_strategy: Union[int, None] = None,
              save_strategy: Union[int, None] = None,
              **kwargs: Any) -> None:
        """
        Trains, evaluates and saves given model. If specified, loads model from checkpoint.

        Parameters:
            model: Model
                a model to be trained or which to load from line specified in `start_from`
            train_data: Iterable
                train data to be passed to model's fit()
            test_data: Iterable, optional
                test data to be passed to model's evaluate()
            train_kwargs: Dict, optional
                arguments for fit()
            test_kwargs: Dict, optional
                arguments for evaluate() - the most common is the dict of metrics
            epochs: int, optional
                how many times to repeat training on data
            start_from: str, optional
                name or index of line from which to start
                starts from the latest model in line
            eval_strategy: int, optional
                Evaluation will take place every `eval_strategy` epochs. If None - the strategy is 'no evaluation'.
            save_strategy: int, optional
                Saving will take place every `save_strategy` epochs. Meta will be saved anyway.
                If None - the strategy is 'save only meta'.
        """

        if train_kwargs is None:
            train_kwargs = {}
        if test_kwargs is None:
            test_kwargs = {}

        if eval_strategy is not None and test_data is None:
            raise ValueError('Eval strategy is specified, but no test data provided')

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
            if len(line) == 0:
                raise RuntimeError(f'Cannot start from line {line_name} as it is empty')
            model_num = self._find_last_model(model, line)

        start_time = pendulum.now()
        self._meta_prefix['train_start_at'] = start_time
        logger.info(f'Training started with parameters:\n{train_kwargs}')
        logger.info(f'repo is {self._repo}')
        logger.info(f'line is {line_name}')
        if start_from is not None:
            logger.info(f'started from model {model_num}')
        logger.info(f'training will last {epochs} epochs')

        for epoch in range(epochs):
            # Empty model's metrics to not to repeat them
            # in epochs where no evaluation
            model.metrics = {}

            # Train model
            model.fit(train_data, **train_kwargs)

            if eval_strategy is not None:
                if epoch % eval_strategy == 0:
                    model.evaluate(test_data, **test_kwargs)

            if save_strategy is not None:
                if epoch % save_strategy == 0:
                    line.save(model)
                else:
                    line.save(model, only_meta=True)
            else:
                line.save(model, only_meta=True)

            # Record metrics:
            # no need to copy since don't reuse model's metrics dict
            self.metrics.append(model.metrics)
            logger.info(f'Epoch {epoch}: {model.metrics}')

        end_time = pendulum.now()
        self._meta_prefix['train_end_at'] = end_time
        logger.info(f'Training finished in {end_time.diff_for_humans(start_time, True)}')
