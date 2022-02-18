class Model():
    def fit(self, x, y):
        raise NotImplementedError()

    def predict(self, x):
        raise NotImplementedError()
    
    def evaluate(self, x, y):
        raise NotImplementedError()

    def load(self, filepath):
        raise NotImplementedError()

    def save(self, filepath):
        raise NotImplementedError()
