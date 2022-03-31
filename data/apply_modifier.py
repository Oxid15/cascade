from . import Modifier, T


class ApplyModifier(Modifier):
    def __init__(self, dataset, func) -> None:
        super().__init__(dataset)
        self.func = func

    def __getitem__(self, index) -> T:
        item = self._dataset(index)
        return self.func(item)

    def __repr__(self) -> str:
        return f'{repr(self)}, {repr(self.func)}'
