import cv2
from . import Dataset, os
from .dataset import T


class FolderImageDataset(Dataset):
    """
    Simple dataset for image folder with lazy loading.
    Accepts the path to the folder with images. In each __getitem__ call
    invokes opencv imread on image and returns it if it exists.
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)
        assert(os.path.exists(self.path))
        self.image_names = os.listdir(self.path)

    def __getitem__(self, index) -> T:
        name = self.image_names[index]
        fullname = os.path.join(self.path, name)
        img = cv2.imread(f'{fullname}')
        if img is not None:
            return img
        else:
            raise RuntimeError(f'cv2 cannot read {fullname}')

    def __len__(self):
        return len(self.image_names)
