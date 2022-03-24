import os

from data import Dataset


class TextClassificationDataset(Dataset):
    def __init__(self, path, encoding='utf-8'):
        self.encoding = encoding
        self.root = os.path.abspath(path)
        folders = os.listdir(self.root)
        self.paths = []
        self.labels = []
        for i, folder in enumerate(folders):
            files = [name for name in os.listdir(os.path.join(self.root, folder))]
            self.paths += [os.path.join(self.root, folder, f) for f in files]
            self.labels += [i for _ in range(len(files))]

        print(f'Found {len(folders)} classes: {[(folder, len(os.listdir(os.path.join(self.root, folder)))) for folder in folders]}')

    def __getitem__(self, index):
        with open(self.paths[index], 'r', encoding=self.encoding) as f:
            text = ' '.join(f.readlines())
            label = self.labels[index]
        return text, label

    def __len__(self):
        return len(self.paths)
