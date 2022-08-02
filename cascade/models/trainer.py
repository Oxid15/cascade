from ..base import Traceable
from ..models import Model, ModelRepo


class Trainer(Traceable):
    def __init__(self, repo, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def train(self, model, *args, **kwargs):
        raise NotImplementedError()


class BasicTrainer(Trainer):
    def __init__(self, repo, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if isinstance(repo, str):
            self.repo = ModelRepo(repo)
        elif isinstance(repo, ModelRepo):
            self.repo = repo

    def train(self, model: Model, train_data, 
        test_data, train_kwargs, test_kwargs) -> None:

        line_name = f'{len(self.repo):0>5d}'
        self.repo.add_line(line_name, type(model))

        model.fit(train_data, **train_kwargs)
        model.evaluate(test_data, **test_kwargs)

        self.repo[line_name].save(model)
