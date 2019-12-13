#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Various segmentation tools.

Created by Matthew A. Bennett (Thu Jul 11 12:13:31 2019)
Matthew.Bennett@glasgow.ac.uk
"""

#%% =============================================================================
# imports
import os
from warnings import warn

import subprocess
import numpy as np
from scipy.ndimage import morphology
from nibabel import load, save, Nifti1Image
from skimage.measure import label

from my_functions import misc

#%% =============================================================================
def launch_itksnap(anat_file, segmentation_file='', data_path=''):
    """Launch itksnap with main image and optional segmentation image.

    Mandatory arguments:
    anat_file: this will be the main image.

    Optional arguments:
    segmentation_file: this will be overlayed.

    data_path: if you want to specify a path to the data.
    """

    if data_path != '' and data_path[-1] != '/':
        data_path += '/'

    if segmentation_file != '':
        seg_string = f' -s {data_path}{segmentation_file}'
    else:
        seg_string = ''

    subprocess.run(f'itksnap -g {data_path}{anat_file}{seg_string}',
                   shell=True, check=True, text=True)

    return None

#%% =============================================================================
def launch_segmentator(anat_file, data_path='', data_range=''):
    """Launch segmentator with with an image and optional data range.

    Mandatory arguments:
    anat_file: this will be the loaded image.

    Optional arguments:
    data_range: a list containing [min, max] will be passed to --valmin and
    --valmax, respectively.

    data_path: if you want to specify a path to the data.
    """

    if data_path != '' and data_path[-1] != '/':
        data_path += '/'

    if data_range != '':
        data_range = f' --valmin {data_range[0]} --valmax {data_range[1]}'

    subprocess.run(f'. ~/segmentator_env/bin/activate; segmentator {data_path}{anat_file}{data_range}',
                   shell=True, check=True, text=True)

    return None

#%% =============================================================================
def segmentator_filter(path_to_data, anat_name, nr_iterations=1,
                       verbose_inner_func=False):
    """Apply filter from segmentator to a nifti file.

    Mandatory arguments:
    path_to_data: path_to_data...

    anat_name: anat_name (if no extension is found, we will assume '.nii.gz').

    nr_iterations: number of iterations of the filter.

    Optional arguments:
    verbose_inner_func: if True, the functions called by this function will
    alert the user when making assumptions
    """

    anat_name = misc.add_extesnion_if_missing(anat_name, '.nii',
                                              verbose = verbose_inner_func)
    anat_name = misc.add_extesnion_if_missing(anat_name, '.gz',
                                              verbose = verbose_inner_func)

    if path_to_data[-1] != '/':
        path_to_data += '/'

#    print('try os.system')
#    os.system(f'. ~/segmetator_env/bin/activate; segmentator_filters \
#              {path_to_data}{anat_name} --nr_iterations {nr_iterations}')

    subprocess.run([f'~/segmentator_env/bin/activate; segmentator_filters {path_to_data}{anat_name} --nr_iterations {nr_iterations}'],
              shell=True, check=True)

    # remove the extension
    anat_name = anat_name.replace('.nii', '')
    anat_name = anat_name.replace('.gz', '')

    anat_name  = f'{anat_name}_STEDI_n{nr_iterations}_s0pt5_r0pt5_g1'

    return anat_name

#%% =============================================================================
def laynii_dnoise_mp2rage(path_to_data, path_to_function, INV1, INV2, UNI):
    """Apply dnoise algorithm from LAYNII to an MP2RAGE nifti file.

        Important: The files must be in .nii format not .nii.gz

        Mandatory arguments:
        path_to_data: path_to_data...

        path_to_function: where is LAYNII installed?

        INV1, INV1, UNI: the usual 3 MP2RAGE images
        """

    if path_to_function[-1] != '/':
        path_to_function += '/'

    os.chdir(path_to_data)

    subprocess.run([f'{path_to_function}LN_MP2RAGE_DNOISE -INV1 {INV1} -INV2 {INV2} -UNI {UNI} -beta 2.0'],
                    shell=True, check=True)

    return 'dnoised_' + UNI

#%% =============================================================================
def morphology_op(filename, operation, n_iterations=1, verbose_inner_func=False):
    """Opening closing operations on MRI data (nifti).

    Takes a nifti (filename) and performs either:
    erosion, dilation, erosion+dialtion (i.e. 'opening')
    or dialtion+erosion (i.e. 'closing').

    Mandatory arguments:
    filename: filename...

    operation: one of the following strings: 'erode', 'dilate', 'close', 'open'

    Optional arguments:
    n_iterations: set to 1 as default.

    verbose_inner_func: if True, the functions called by this function will
    alert the user when making assumptions

    Adapted from From Faruk's gist.github:
    https://gist.github.com/ofgulban/21f9b257de849c546f34863aa26f3dd3#file-dilate_erode_mri_data-py-L13
    """

    filename = misc.add_extesnion_if_missing(filename, '.nii',
                                             verbose = verbose_inner_func)
    filename = misc.add_extesnion_if_missing(filename, '.gz',
                                             verbose = verbose_inner_func)

    # load data
    nii = load(filename)
    basename = nii.get_filename().split(os.extsep, 1)[0]
    data = nii.get_data()

    if operation == 'erode':
        data = morphology.binary_erosion(data, iterations=n_iterations)
    elif operation == 'dilate':
        data = morphology.binary_dilation(data, iterations=n_iterations)
    elif operation == 'close':
        # perform closing
        data = morphology.binary_dilation(data, iterations=n_iterations)
        data = morphology.binary_erosion(data, iterations=n_iterations)
    elif operation == 'open':
        # perform opening
        data = morphology.binary_erosion(data, iterations=n_iterations)
        data = morphology.binary_dilation(data, iterations=n_iterations)

    # save as nifti
    out = Nifti1Image(data, header=nii.header, affine=nii.affine)
    out_name = basename + f'_{operation}.nii.gz'
    save(out, out_name)

    return out_name

#%% =============================================================================
def connected_clusters(filename, threshold=False, cluster_size=26,
                       connectivity=2, binarize_labels=1,
                       verbose_inner_func=False):
    """Connected clusters cluster size thresholdesholding.

    Mandatory arguments:
    filename: Path to nii file with image data

    Optional arguments:
    threshold: Binarization threshold for the input data (assign
               zero to anything below the number and 1 to above).
               (default value = False).

    cluster_size: Minimum cluster size (voxels).
                  (default value = 26).

    connectivity: Maximum number of orthogonal hops to consider a
                  pixel/voxel as a neighbor. Accepted values are
                  ranging from 1 to input.ndim.
                  (default value = 2).

    binarize_labels: Return binarized(1) or unbinarized(0) labels.
                     (default value = 1).

    verbose_inner_func: if True, the functions called by this function will
    alert the user when making assumptions

    Adapted (removed use of argparse) from From Faruk's gist.github:
    https://gist.github.com/ofgulban/27c4491592126dce37e97c578cbf307b
    """

    filename = misc.add_extesnion_if_missing(filename, '.nii',
                                             verbose = verbose_inner_func)
    filename = misc.add_extesnion_if_missing(filename, '.gz',
                                             verbose = verbose_inner_func)

    nii = load(filename)
    basename = nii.get_filename().split(os.extsep, 1)[0]
    data = nii.get_data()

    # binarize
    if threshold:
        print('Data will be intensity threshold (' + str(threshold + ').'))
        data = np.where(data <= threshold, 0, 1)
    else:
        print('Data will not be intensity threshold.')

    # connected clusters
    data = label(data, connectivity=connectivity)
    labels, counts = np.unique(data, return_counts=True)
    print(str(labels.size) + ' clusters are found.')

    print('Applying connected clusters thresholdeshold (' + str(cluster_size) + ' voxels).')
    for i, (i_label, i_count) in enumerate(zip(labels[1:], counts[1:])):
        if i_count < cluster_size:
            data[data == i_label] = 0
    data[data != 0] = 1

    # output binarized or cluster connectedness threshold data.
    if binarize_labels == 1:
        print('Binarizing cluster labels.')
        out = Nifti1Image(data, header=nii.get_header(), affine=nii.get_affine())
        out_name = basename + '_threshold' + str(threshold) + '_c' + str(cluster_size) + '_bin.nii.gz'
    elif binarize_labels == 0:
        print('Not binarizing cluster labels.')
        orig = nii.get_data()
        orig[data == 0] = 0
        out = Nifti1Image(orig, header=nii.get_header(), affine=nii.get_affine())
        out_name = basename + '_threshold' + str(threshold) + '_c' + str(cluster_size) + '.nii.gz'
    else:
        print("Incorrect binarization value. Enter 1 or 0.")

    save(out, out_name)
    print('\nSaved as: ' + out_name + '\n')
    return out_name

#%% =============================================================================
def c3d_dilate(filename, nvox=5, seg_label=1, verbose=False,
               verbose_inner_func=False):
    """Apply c3d dilate.

    Mandatory arguments:
    filename: path_to_data and filename (if no extension is found, we will
              assume '.nii.gz').

    nvox: number of voxels to dilate.
          (default = 5).

    seg_label: which label in the segmentation should we dilate?
               (default = 1).

    Optional arguments:
    verbose: if True, the function will alert the user when making assumptions

    verbose_inner_func: if True, the functions called by this function will
    alert the user when making assumptions
    """

    # if the extension has been provided, make sure we alter the out_name
    # taking this into account
    out_name = misc.inject_substring_before_extension(filename,
                                                      f'_dilate_{nvox}','.nii.gz',
                                                      verbose = verbose_inner_func)
    if out_name is None:
        out_name = misc.inject_substring_before_extension(filename,
                                                          f'_dilate_{nvox}',
                                                          '.nii.gz',
                                                          verbose = verbose_inner_func)
    if out_name is None:
        if verbose: warn('No file extension on filename - assuming .nii.gz')
        out_name = f'{filename}_dilate_{nvox}.nii.gz'

#    os.system(f'c3d {filename} -dilate {seg_label} {nvox}x{nvox}x{nvox}vox -o {out_name}')

    subprocess.run([f'c3d {filename} -dilate {seg_label} {nvox}x{nvox}x{nvox}vox -o {out_name}'],
                   shell=True, check=True)

    return out_name
