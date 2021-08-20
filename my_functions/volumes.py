#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

def mask_region(data, mask):
    return data * mask

test_data = np.zeros((3,3,3))
test_data[0,0:2,0] += 1
test_data[0,1,1] += 1

test_labels = np.zeros((3,3,3))
test_labels[0,:,0] += 1
test_labels[0,:,1] += 2
test_labels[0,:,2] += 3
test_labels
test_data[test_labels<2]

test_data

label_do(test_data, test_labels, func=np.std)

def label_average(data, labels, func=np.mean):
    """
    Inputs:
        data: numpy array
        labels: numpy array, containing non-zero label value for each voxel
        func: function applied to each set of labelled data voxels contained in
              a 1D numpy array. The function MUST return a single value!
              (default np.mean)
    Returns: 1D numpy array containing the value returned from the function
             from each set of labelled voxels.
    """
    average = np.zeros((len(np.unique(labels))-1))
    for idx, label in enumerate(np.unique(labels[labels>0])):
        average[idx] = func(data[labels==label])
    return average


t1 = np.random.rand(50,100,50)
t1[10:20,70:90,:] += 1
t1[30:40,10:40,:] += 1
t1[35:45,50:60,:] += 1
t1[32:43,30:55,:] += 1

mask1 = np.zeros((50,100,50))
mask1[25:50, 5:90, :] += 1
mask2 = np.zeros((50,100,50))
mask2[5:20, 50:95, :] += 1

plt.subplot(3,1,1)
plt.imshow(t1[:,:,0])
plt.subplot(3,1,2)
plt.imshow(mask1[:,:,0])
plt.subplot(3,1,3)
plt.imshow(mask2[:,:,0])
plt.show()

thing = mask_region(t1, mask1)

plt.subplot(4,1,1)
plt.imshow(t1[:,:,0])
plt.subplot(4,1,2)
plt.imshow(mask1[:,:,0])
plt.subplot(4,1,3)
plt.imshow(mask2[:,:,0])
plt.subplot(4,1,4)
plt.imshow(thing[:,:,0])
plt.show()

