# -*- coding: utf-8 -*-
'''
    Created on Sun Nov 4 9:08 2018

    Author           : Shaoshu Yang
    Email            : shaoshuyangseu@gmail.com
    Last edit date   : Sat Sun Nov 4 24:00 2018

South East University Automation College
Vision Cognition Laboratory, 211189 Nanjing China
'''

__all__ = ['logger']

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import sys
import os

# logger records the data collected throughout the training process or validation process,
# It is orderly designed so researchers can record raw data and utilize them easily and correctly.
# You can start writing on the logger from scratch or resume from the checkpoint.
class logger():
    def __init__(self, file_path, title=None, resume=False):
        self.title = '' if title == None else title
        self.resume = resume
        # Start from scratch
        if resume == False:
            self.file = open(os.path.join('../' + file_path), 'w')
        else: # Resume from checkpoint
            self.file = open(os.path.join('../' + file_path), 'r')
            # Reading data tags
            tags = self.file.readline()
            self.tags = tags.rstrip().split('\t')
            self.data = {}
            for _, tag in enumerate(self.tags):
                self.data[tag] = []
            # Restoring data
            for data in self.file:
                data = data.rstrip().split('\t')

                for i in range(0, len(data)):
                    self.data[self.tags[i]].append(data[i])
            self.file.close()

            self.file = open(os.path.join('../' + file_path), 'a')

    def set_tags(self, tags):
        if self.resume:
            pass
        # Set tags for new training process
        self.data = {}
        self.tags = tags
        for _, tag in enumerate(self.tags):
            self.file.write(tag)
            self.file.write('\t')
            self.data[tag] = []

        self.file.write('\n')
        self.file.flush()

    def append(self, data):
        # Appending new data to logger
        assert len(self.tags) == len(data)
        for idx, num in enumerate(data):
            self.file.write("{0:.6f}".format(num))
            self.file.write('\t')
            self.data[self.tags[idx]].append(num)

        self.file.write('\n')
        self.file.flush()

    def plot(self, tags=None):
        # Visualize stored data
        tags = tags if tags is not None else self.tags
        for _, tag in enumerate(tags):
            x = np.arange(len(self.data[tag]))
            matplotlib.pyplot.plot(x, np.asarray(self.data[tag]))

        matplotlib.pyplot.legend([self.title + '(' + tag + ')' for tag in tags])
        matplotlib.pyplot.grid(True)
        matplotlib.pyplot.show()

    def close(self):
        if self.file is not None:
            self.file.close()




