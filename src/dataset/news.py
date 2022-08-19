# -*- coding:utf-8 -*-
import sys
sys.path.append("..")
from model.base import Base


class News(Base):

    def __init__(self, data_label, image_root, augmentation, use_depth=False, original_mask=False):
        self.data_label = data_label
        self.image_root = image_root
        self.augmentation = augmentation
        self.use_depth = use_depth
        self.original_mask = original_mask

    def __getitem__(self, item):
        img = self.data_label['images'][item]
        mask = self.data_label['masks'][item]
        img = np.tile(img[:, :, np.newaxis], (1, 1, 3))
        # img = add_depth_channels(img)
        if self.original_mask:
            img, _ = self.augmentation(img.astype(np.float32).copy(), None)
        else:
            img, mask = self.augmentation(img.astype(np.float32).copy(), mask.copy())
        if self.use_depth:
            depth = self.data_label['depths'][item]
            img[:, :, 2] = (depth / depth_max) * 255.0 - depth_mean
        # img = img[:, :, np.newaxis]
        mask = mask.astype(np.float32) / 255.0

        return torch.from_numpy(img).permute(2, 0, 1), mask.astype(np.long)

    def __len__(self):
        return len(self.data_label['images'])
