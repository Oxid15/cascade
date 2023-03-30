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
import random
import sys
import numpy as np

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.models import BasicModelModifier


def test_basic_model_with_concrete_case(ones_model):
    def precision(gt, pred):
        pos_gt = gt[gt == 1]
        what_pred = pred[gt == 1]
        tp = (pos_gt == what_pred).sum()

        pos_pred = (pred == 1).sum()
        return tp / pos_pred

    def recall(gt, pred):
        pos_gt = gt[gt == 1]
        pos_pred = pred[gt == 1]
        tp = (pos_gt == pos_pred).sum()

        return tp / pos_gt.sum()

    model = ones_model
    model.evaluate(
        [random.randint(0, 255) for _ in range(3)],
        np.array([0, 1, 1]),
        metrics_dict={
            'precision': precision,
            'recall': recall
        })

    assert model.metrics['precision'] == 2 / 3
    assert model.metrics['recall'] == 1


def test_modifier(ones_model):
    class DoubleModifier(BasicModelModifier):
        def load(self, filepath) -> None:
            pass

        def save(self, filepath) -> None:
            pass

        def predict(self, x, *args, **kwargs):
            return self._model.predict(x) * 2

        def fit(self, x, y, *args, **kwargs) -> None:
            pass

    model = ones_model
    model = DoubleModifier(model)

    y = model.predict([random.randint(0, 255) for _ in range(3)])
    meta = model.get_meta()

    assert all(y == [2, 2, 2])
    assert len(meta) == 2
