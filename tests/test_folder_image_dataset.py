import os
import cv2
import numpy as np
import unittest


class FolderImageDatasetTest(unittest.TestCase):
    def test_length(self):
        from cascade import FolderImageDataset
        # Create dummy folder dataset
        dirname = 'dummy'
        num = 3
        shape = (256, 256, 3)

        os.makedirs(dirname, exist_ok=True)
        for i in range(num):
            cv2.imwrite(os.path.join(dirname, f'{i}.png'), np.random.randint(0, 255, shape))

        # Check correct creation
        ds = FolderImageDataset(dirname)

        self.assertEqual(num, len(ds))

        # Remove dummy folder dataset
        for i in range(num):
            os.remove(f'{dirname}/{i}.png')
        os.rmdir(dirname)

    def test_get_and_rgb(self):
        from cascade import FolderImageDataset
        # Create dummy folder dataset
        dirname = 'dummy'
        num = 3
        shape = (256, 256)
        r = np.full(shape, 255)
        g = np.full(shape, 0)
        b = np.full(shape, 0)
        img = np.dstack((r, g, b))

        os.makedirs(dirname, exist_ok=True)
        for i in range(num):
            cv2.imwrite(os.path.join(dirname, f'{i}.png'), img)

        # Check correctness of the item
        ds = FolderImageDataset(dirname)

        # Check for RGB order and NOT BGR
        self.assertIsNotNone(ds[0])
        self.assertEqual(ds[0][0][0][0], 255)
        self.assertEqual(ds[0][0][0][1], 0)
        self.assertEqual(ds[0][0][0][2], 0)

        # Remove dummy folder dataset
        for i in range(num):
            os.remove(f'{dirname}/{i}.png')
        os.rmdir(dirname)


if __name__ == '__main__':
    unittest.main()
