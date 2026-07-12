# from cascade.data import Dataset, Modifier


# class RaiseDatasetOverridingGetItem(Dataset):
#     def __getitem__(self, index):
#         if index == 1:
#             raise RuntimeError("on no!")
#         else:
#             return 0

#     def __len__(self):
#         return 2


# class ModifierOverridingGetItem(Modifier):
#     def __getitem__(self, index):
#         return self._dataset[index]


# ds = RaiseDatasetOverridingGetItem()
# ds = ModifierOverridingGetItem(ds)

# for i in range(len(ds)):
#     ds[i]


from cascade.data import Dataset, Modifier


class RaiseDataset(Dataset):
    def get(self, index):
        if index == 1:
            raise RuntimeError("on no!")
        else:
            return 0

    def __len__(self):
        return 2


class ModifierWithGet(Modifier):
    def get(self, index):
        return self._dataset[index]


ds = RaiseDataset()
ds = ModifierWithGet(ds)

for i in range(len(ds)):
    ds[i]
