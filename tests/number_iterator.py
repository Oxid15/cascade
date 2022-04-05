import os
import sys

sys.path.append(os.path.abspath('../..'))
from cascade.data import Iterator


class NumberIterator(Iterator):
    def __init__(self, max_val):
        self.max_val = max_val

    def __iter__(self):
        for i in range(self.max_val):
            yield i
