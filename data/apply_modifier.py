from . import Modifier


class ApplyModifier(Modifier):
    def __init__(self, dataset, func):
        super().__init__(dataset)
        self.func = func

    def __getitem__(self, index):
        item = self._dataset(index)
        return self.func(item)
