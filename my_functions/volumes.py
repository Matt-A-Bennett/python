#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage.filters as f

def our_func(data, average_bin_size=1, thresh=0.35):
    """
    Function to be applied to data. MUST return a single value!

    Inputs:
        data:   1D numpy array
    """
    # return np.median(data)

    # return np.sum(data>thresh)/len(data)

    # this requires tuning of thresh by looking at the ground truth curve...
    tmp = np.mean(data[data>thresh])
    np.nan_to_num(tmp, copy=False)
    return tmp

    # sorted_data = np.sort(data)
    # 1/len(data)
    # data[data>thresh]
    # tmp = np.mean(data[data>thresh])
    # np.nan_to_num(tmp, copy=False)
    # return tmp

    # # IDEA: take the size of the current mask bin, RELATIVE TO THE AVERAGE BIN
    # # SIZE, into accout somehow... boost each mean(?) signal in bin by how much
    # # size of the bin reletive to average (i.e. boost thicker parts to counter
    # # extra 'dilution' from thicker parts of the mask:
    # # weighted_mean = mean*(bin_size/average_bin_size)
    # current_bin_size = len(data)
    # weighted_mean = np.mean(data)*(current_bin_size/average_bin_size)
    # return weighted_mean

def label_do(data, labels, func=np.mean, *args, **kwargs):
    """
    Apply any function (default np.mean) to each set of labelled data voxels
    and return the results as a 1D numpy array.

    Inputs:
        data:           Numpy array

        labels:         Numpy array of the same size as data, containing numpy
                        array of non-zero int label value for each voxel.

        func:           Function to be applied to each set of voxels labelled
                        in data. The function MUST return a single value! (the
                        default fuction is np.mean).

        *args:          Any non-named arguments to pass to func.

        **kwargs:       Any named arguments to pass to func.

    Returns:
        func_results:   1D numpy array containing the value returned from the
                        function from each set of labelled voxels.
    """
    func_results = np.zeros((len(np.unique(labels))-1))
    for idx, label in enumerate(np.unique(labels[labels>0])):
        func_results[idx] = func(data[labels==label], *args, **kwargs)
    return func_results

ppi = np.zeros((100,100,50))
ppi[55:65,10:40,:] += 2
ppi[57:68,30:55,:] += 2
ppi[60:70,50:60,:] += 2
ppi[63:73,70:90,:] += 1
ppi = f.gaussian_filter(ppi, 3)
ppi += np.random.rand(100,100,50)

tmp = np.zeros((100,100,50))
for i in range(100):
    tmp[:,i,:] += i+1

mask1 = np.zeros((100,100,50))
mask1[50:75, 5:90, :] += 1
# mask1[50:60, 35:45, :] = 0
mask1 = f.gaussian_filter(mask1, 3)
mask1[mask1>0.5]=1
mask1[mask1<=0.5]=0

mask2 = np.zeros((100,100,50))
mask2[50:75, 5:90, :] += 1
mask2[35:95, 10:25, :] += 1
mask2[5:95, 65:75, :] += 1
# mask2[50:60, 35:45, :] = 0
mask2 = f.gaussian_filter(mask2, 3)
mask2[mask2>0.5]=1
mask2[mask2<=0.5]=0

masked_ppi1 = ppi * mask1
masked_ppi2 = ppi * mask2

mask1 *= tmp
mask2 *= tmp

_, bin_counts = np.unique(mask2[mask2>0], return_counts=True)
average_bin_size = np.min(bin_counts)

out1 = label_do(ppi, mask1)
out1 = np.concatenate((np.ones(5)*-1, out1))
out2 = label_do(ppi, mask2)
out2 = np.concatenate((np.ones(5)*-1, out2))
out3 = label_do(ppi, mask2, our_func)
# out3 = label_do(ppi, mask2, our_func, average_bin_size)

out3 = np.concatenate((np.ones(5)*-1, out3))

masks = [mask1[:,:,0], mask2[:,:,0], mask2[:,:,0]]
masked_ppis = [masked_ppi1[:,:,0], masked_ppi2[:,:,0], masked_ppi2[:,:,0]]
titles = ['unbiased mask (mean)', 'biased mask (mean)', 'biased mask (custom)']
for plot_i in range(3):
    plt.subplot(4,3,plot_i+1)
    plt.title(titles[plot_i])
    plt.imshow(ppi[:,:,0], vmin=0, vmax=3, aspect='auto')
    plt.axis('off')

for i, plot_i in enumerate(range(4,7)):
    plt.subplot(4,3,plot_i)
    plt.imshow(masks[i], aspect='auto')
    plt.axis('off')

for i, plot_i in enumerate(range(7,10)):
    plt.subplot(4,3,plot_i)
    plt.imshow(masked_ppis[i], vmin=0, vmax=3, aspect='auto')
    plt.axis('off')

plt.subplot(4,3,10)
plt.plot(out1, 'r')
plt.xlim(0,100)
plt.ylim(0,2.5)

plt.subplot(4,3,11)
plt.plot(out1, '--r')
plt.plot(out2, 'k')
plt.xlim(0,100)
plt.ylim(0,2.5)

plt.subplot(4,3,12)
plt.plot(out1, '--r')
plt.plot(out3, 'k')
plt.xlim(0,100)
plt.ylim(0,2.5)

plt.show()


