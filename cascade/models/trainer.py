import sys
import logging
from copy import deepcopy
from typing import Iterable, List, Dict

import pendulum
from ..base import Traceable
from ..models import Model, ModelRepo


logger = logging.getLogger(__name__)

class Trainer(Traceable):
    def __init__(self, repo, *args, **kwargs) -> None:
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
    def __init__(self, repo, *args, **kwargs) -> None:
        super().__init__(repo, *args, **kwargs)

    def train(self, 
        model: Model,
        train_data: Iterable,
        test_data: Iterable,
        train_kwargs: Dict,
        test_kwargs: Dict,
        epochs=1,
        line_name=None) -> None:

        if line_name is None:
            line_name = f'{len(self._repo):0>5d}'
        self._repo.add_line(line_name, type(model))

        self._meta_prefix['train_start_at'] = pendulum.now()
        logger.info(f'Training started with parameters: {train_kwargs}')
        logger.info(f'it will last {epochs} epochs')

        for epoch in range(epochs):
            model.fit(train_data, **train_kwargs)
            model.evaluate(test_data, **test_kwargs)
            self._repo[line_name].save(model)
            self.metrics.append(deepcopy(model.metrics))

            logger.info(f'Epoch {epoch}: {model.metrics}')

        self._meta_prefix['train_end_at'] = pendulum.now()
