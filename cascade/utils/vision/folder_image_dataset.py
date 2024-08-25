"""
Copyright 2022-2024 Ilia Moiseev

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

from typing import Any

from typing_extensions import Literal

from ...data import FolderDataset


class ImageBackend:
    def read(self, path: str) -> Any:
        raise NotImplementedError()


class CV2Backend(ImageBackend):
    def __init__(self) -> None:
        super().__init__()
        try:
            import cv2
        except ImportError as e:
            raise ImportError("cv2 backend requires opencv-python package") from e
        self._cv2 = cv2

    def read(self, path: str):
        img = self._cv2.imread(path)
        if img is not None:
            return self._cv2.cvtColor(img, self._cv2.COLOR_BGR2RGB)
        else:
            raise IOError(f"cv2 failed to read {path}")


class PILBackend(ImageBackend):
    def __init__(self) -> None:
        super().__init__()
        try:
            from PIL import Image
        except ImportError as e:
            raise ImportError("PIL backend requires opencv-python package") from e
        self._image = Image

    def read(self, path: str):
        try:
            img = self._image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
        except Exception as e:
            raise IOError(f"PIL failed to read {path}") from e
        return img


class FolderImageDataset(FolderDataset):
    """
    Simple dataset for image folder with lazy loading.
    Accepts the path to the folder with images. In each __getitem__ call
    invokes opencv imread on image and returns it if it exists.

    Supports opencv or pillow backends
    """

    def __init__(
        self,
        root: str,
        backend: Literal["cv2", "PIL"] = "PIL",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        root : str
            The folder with images. Should contain image files only
        backend : Literal["cv2", "PIL"], optional
            What library to use to load images, by default "PIL"
        """
        super().__init__(root, *args, **kwargs)

        if backend == "cv2":
            self._backend = CV2Backend()
        elif backend == "PIL":
            self._backend = PILBackend()
        else:
            raise ValueError(f"Only cv2 or PIL backends are supported, got: {backend}")

    def __getitem__(self, index: int):
        name = self._names[index]
        img = self._backend.read(name)
        return img
