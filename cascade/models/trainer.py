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

import logging
from typing import Any, Dict, Iterable, Tuple, Union

import pendulum
from typing_extensions import deprecated

from ..base import Meta, Traceable, raise_not_implemented
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
            raise TypeError(
                f"Repo should be either ModelRepo or path, got {type(repo)}"
            )

        self.metrics = []
        super().__init__(*args, **kwargs)

    def train(self, model: Model, *args: Any, **kwargs: Any) -> None:
        raise_not_implemented("cascade.models.Trainer", "train")

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["metrics"] = self.metrics
        meta[0]["repo"] = self._repo.get_meta()
        return meta


@deprecated(
    "cascade.models.BasicTrainer is deprecated since 0.14.0, consider using"
    " cascade.trainers.BasicTrainer"
)
class BasicTrainer(Trainer):
    """
    The most common of concrete Trainers.
    Trains a model for a certain amount of epochs.
    Can start from checkpoint if model file exists.
    """

    def __init__(self, repo: Union[ModelRepo, str], *args: Any, **kwargs: Any) -> None:
        self.train_start_at = None
        self.train_end_at = None
        super().__init__(repo, *args, **kwargs)

    @staticmethod
    def _load_last_model(line: ModelLine) -> Tuple[Model, int]:
        model_num = len(line) - 1
        while True:
            try:
                model = line.load(model_num, only_meta=False)
                return model, model_num
            except Exception as e:
                logger.warning(f"Model {model_num} files were not found\n{e}")
                model_num -= 1

                if model_num == -1:
                    raise FileNotFoundError(f"No model files were found in line {line}")

    def _handle(self, error: Exception, model: Model, line: ModelLine):
        line.save(model, only_meta=True)
        logger.exception(error)

    def train(
        self,
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
        **kwargs: Any,
    ) -> None:
        """
        Trains, evaluates and saves given model. If specified, loads model from checkpoint.

        Parameters:
            model: Model
                a model to be trained or which to load from line specified in ``start_from``
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
                Evaluation will take place every ``eval_strategy`` epochs. If None - the strategy
                is ``no evaluation``.
            save_strategy: int, optional
                Saving will take place every ``save_strategy`` epochs. Meta will be saved anyway.
                If None - the strategy is 'save only meta'.
        """

        if train_kwargs is None:
            train_kwargs = {}
        if test_kwargs is None:
            test_kwargs = {}

        if eval_strategy is not None and test_data is None:
            raise ValueError("Eval strategy is specified, but no test data provided")

        if start_from is not None:
            line_name = start_from
        else:
            line_name = f"{len(self._repo):0>5d}"
            if line_name in self._repo.get_line_names():
                # Name can appear in the repo if the user manually
                # removed the lines from the middle of the repo

                # This will be handled strictly
                # until it will become clear that some solution needed
                raise RuntimeError(f"Line {line_name} already exists in {self._repo}")

        self._repo.add_line(line_name, type(model))
        line = self._repo[line_name]

        if start_from is not None:
            if len(line) == 0:
                raise RuntimeError(f"Cannot start from line {line_name} as it is empty")
            model, model_num = self._load_last_model(line)

        # Since the model is created externally, we
        # need to register a callback manually
        model.add_log_callback(line._save_only_meta)

        start_time = pendulum.now()
        self.train_start_at = start_time
        logger.info(f"Training started with parameters:\n{train_kwargs}")
        logger.info(f"repo is {self._repo}")
        logger.info(f"line is {line_name}")
        if start_from is not None:
            logger.info(f"started from model {model_num}")
        logger.info(f"training will last {epochs} epochs")

        for epoch in range(epochs):
            # Empty model's metrics to not to repeat them
            # in epochs where no evaluation
            model.metrics = []

            # Train model
            try:
                model.fit(train_data, **train_kwargs)
            except Exception as e:
                self._handle(e, model, line)
                return

            if eval_strategy is not None:
                if epoch % eval_strategy == 0:
                    try:
                        model.evaluate(test_data, **test_kwargs)
                    except Exception as e:
                        self._handle(e, model, line)
                        return

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
            logger.info(f"Epoch: {epoch}")
            for metric in model.metrics:
                logger.info(metric)

        end_time = pendulum.now()
        self.train_end_at = end_time
        logger.info(
            f"Training finished in {end_time.diff_for_humans(start_time, True)}"
        )

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0]["train_start_at"] = self.train_start_at
        meta[0]["train_end_at"] = self.train_end_at
        return meta
