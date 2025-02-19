# -*- coding: utf-8 -*-
'''
    Created on Sat Nov 3 21:39 2018

    Author           : Shaoshu Yang
    Email            : shaoshuyangseu@gmail.com
    Last edit date   : Tues Nov 6 24:00 2018

South East University Automation College
Vision Cognition Laboratory, 211189 Nanjing China
'''

from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
from src.utils import file_names
from src.utils import scaling
import numpy as np
import torch
import cv2

__all__ = ['MNIST']

# MNIST dataset definition
class MNIST(Dataset):
    def __init__(self, folder_path, img_size):
        '''
        Args:
             folder_path    : (string) directory storing MNIST data set
             img_size       : (int) input dimensions of MNIST images
        '''
        self.img_list = file_names(folder_path)
        self.img_size = img_size

    def __getitem__(self, idx):
        '''
        Args:
             idx            : (int) required index of corresponding data
        Returns:
             Required image (tensor)
        '''
        img = np.array(cv2.imread(self.img_list[idx]), dtype=float)
        img = scaling(img, 20)
        # Transform from BGR to RGB, HWC to CHW
        img = torch.FloatTensor(img[:, :, ::-1].transpose((2, 0, 1)).copy()).div(255.0)

        return img

    def __len__(self):
        return len(self.img_list)

