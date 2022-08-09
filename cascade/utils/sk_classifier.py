"""
Copyright 2022 Ilia Moiseev

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

from .sk_model import SkModel


class SkClassifier(SkModel):
    """
    Alias for cascade.utils.SkModel remained for compatibility
    """
    def __init__(self, name=None, blocks=None, **kwargs):
        raise RuntimeError('SkClassifier is not supported anymore.\n'
                           'It was an alias of SkModel and doesn\'t have any additional capabilities.\n'
                           'Please, replace SkClassifier with SkModel.')
