import pendulum
from typing import Iterable, List, Dict

from ..base import Traceable
from ..models import Model, ModelRepo


class Trainer(Traceable):
    def __init__(self, repo, *args, **kwargs) -> None:
        if isinstance(repo, str):
            self._repo = ModelRepo(repo)
        elif isinstance(repo, ModelRepo):
            self._repo = repo
        
        self.metrics = {}
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
        line_name=None) -> None:

        if line_name is None:
            line_name = f'{len(self._repo):0>5d}'
        self._repo.add_line(line_name, type(model))

        self._meta_prefix['train_start_time'] = pendulum.now()

        model.fit(train_data, **train_kwargs)

        self._meta_prefix['train_end_time'] = pendulum.now()

        model.evaluate(test_data, **test_kwargs)

        self._meta_prefix['evaluate_end_time'] = pendulum.now()

        self._repo[line_name].save(model)

        self.metrics = model.metrics
