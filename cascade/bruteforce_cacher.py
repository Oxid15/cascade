from . import Modifier, tqdm


class BruteforceCacher(Modifier):
    def __init__(self, dataset):
        super(BruteforceCacher, self).__init__(dataset)
        self._dataset = [item for item in tqdm(self._dataset)]  # forcibly calling all previous lazy loads
