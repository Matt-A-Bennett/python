#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline for processing 7T anatomical and functional data completely.

Steps:
    convert dicoms to nifti
    open the functional and anatomical scans in one window so I can do intial registation
    use ANTs to add a nonlinear algignment of the anatomical to the functional
    preprocess the anatomical prior to segmentation
    segment anatomical
    make layers
    project layers into EPI space

Convert dicoms
Created by Matthew A. Bennett (Wed Jun 26 13:16:48 2019)
Matthew.Bennett@glasgow.ac.uk
"""
#%% =============================================================================
# Notes
# Multiple transformations can be composed using the FSL tools convertwarp and applywarp
# or using the AFNI tools 3dNwarpCat and 3dNwarpApply.

# If I could figure out how to make nipype do this, it would be parallel and fast...

#%% =============================================================================
# imports
import os, subprocess

import nibabel
from nibabel.processing import resample_to_output

from my_functions import seg_tools
from my_functions.misc import bash

#%% =============================================================================
# paths and definitions

base_dir = '/analyse/Project0256/'

sub_folders = ['20190816_PFB06', '20190817_EPA14', '20190817_SLW06', '20190818_FUH13',
               '20190819_LDH12', '20190820_ULA08', '20190901_ALL21', '20190902_MZA30',
               '20190903_CGE02', '20190909_LLN21']

laynii_path = '/home/mattb/laynii/'
nifti_ext = '.nii.gz'
wm_seg_name = 'initial_wm_seg.nii.gz'

upsample_to_res = 0.4
upsample_with_order = 5 # 0-5
# number of iterations for segmentator filter
nr_iterations = 5


subs_processed_correctly = []
#%% =============================================================================
# preprocess the anatomical prior to segmentation
for sub_fold in [sub_folders[0]]:

    try:
        sub_id = sub_fold[9:]
        print(f'Processing {sub_id}...')
        print('')

        nifti_dir = f'{base_dir}{sub_fold}/sub-{sub_id}/anat/'
        os.chdir(f'{nifti_dir}')

        INV1_name = f'sub-{sub_id}_INV1'
        INV2_name = f'sub-{sub_id}_INV2'
        UNI_name = f'sub-{sub_id}_UNI'
        T2w_name = f'sub-{sub_id}_T2w'

        # I get a segfault if I pass the mprage as UNI and a proton density and INV2 and the
        # division as UNI...

        # apply denoise to the mp2rage
        print('\n*** LAYNII DENOISE ***\n')
        bash(f'gunzip -d -k {INV1_name}{nifti_ext} {INV2_name}{nifti_ext} {UNI_name}{nifti_ext}')
        seg_tools.laynii_dnoise_mp2rage(nifti_dir, laynii_path, f'{INV1_name}.nii', f'{INV2_name}.nii', f'{UNI_name}.nii')
        # clean up
        bash(f'rm {INV1_name}.nii {INV2_name}.nii {UNI_name}.nii')
        UNI_name = f'dnoised_{UNI_name}'
        bash(f'gzip -v {UNI_name}.nii Border_enhance.nii')

        print('\n*** BET EXTRACT UNI ***\n')
        bash(f'bet {UNI_name}{nifti_ext} {UNI_name}_skullstrip{nifti_ext} -m -f 0.05')
        UNI_name += '_skullstrip'

        print('\n*** APPLY MASK TO T2s ***\n')
        subprocess.run([f'fslmaths {T2w_name}{nifti_ext} -mas {UNI_name}_mask{nifti_ext} {T2w_name}_skullstrip{nifti_ext}'], shell=True, check=True)
        subprocess.run([f'fslmaths {INV1_name}{nifti_ext} -mas {UNI_name}_mask{nifti_ext} {INV1_name}_skullstrip{nifti_ext}'], shell=True, check=True)
        T2w_name += '_skullstrip'
        INV1_name += '_skullstrip'

        print('\n*** BIAS CORRECTION ***\n')
        bash(f'N4BiasFieldCorrection -i {UNI_name}{nifti_ext} -o {nifti_dir}/{UNI_name}_inhom_corr{nifti_ext}')
        bash(f'N4BiasFieldCorrection -i {INV1_name}{nifti_ext} -o {nifti_dir}/{INV1_name}_inhom_corr{nifti_ext}')
        UNI_name += '_inhom_corr'
        INV1_name += '_inhom_corr'

        print('\n*** UPSAMPLE ANATOMICALS ***\n')
        for anat_name in [UNI_name, INV1_name, T2w_name]:
            tmp = nibabel.load(f'{anat_name}{nifti_ext}')
            upsampled = resample_to_output(tmp, voxel_sizes=upsample_to_res, order=upsample_with_order)
            anat_name += f'_upsample{upsample_to_res}'
            anat_name = anat_name.replace('.', 'p')
            nibabel.save(upsampled, f'{anat_name}{nifti_ext}')
        del tmp

        UNI_name += f'_upsample{upsample_to_res}'
        UNI_name = UNI_name.replace('.', 'p')
        INV1_name += f'_upsample{upsample_to_res}'
        INV1_name = INV1_name.replace('.', 'p')
        T2w_name += f'_upsample{upsample_to_res}'
        T2w_name = INV1_name.replace('.', 'p')

        print('\n*** SEGMENTATOR FILTER ***\n')
        # filter to smooth noise but presever edge info
        UNI_name = seg_tools.segmentator_filter(nifti_dir, f'{UNI_name}{nifti_ext}', nr_iterations)
        INV1_name = seg_tools.segmentator_filter(nifti_dir, f'{INV1_name}{nifti_ext}', nr_iterations)
        UNI_name = UNI_name.replace(f'{nifti_ext}', '')
        INV1_name = INV1_name.replace(f'{nifti_ext}', '')

        subs_processed_correctly.append(sub_id)
    except:
        continue
#%% =============================================================================
# now make a white matter segmentation in itksnap for dilation to full brain mask

# =============================================================================
# seg_tools.launch_itksnap(f'{UNI_name}{nifti_ext}', data_path=nifti_dir)
#
# brain_mask = seg_tools.c3d_dilate(wm_seg_name, nvox=6)
#
# # apply mask to the anatomical
# bash(f'fslmaths {UNI_name}{nifti_ext} -mas {brain_mask} {UNI_name}_masked{nifti_ext}')
# UNI_name += '_masked'
#
#
# #%% =============================================================================
# # now segment white matter with segmentator (will be exported as _labels_0)
# # also segment white+grey matter with segmentator (will be exported as _labels_1)
#
# seg_tools.launch_segmentator(f'{UNI_name}{nifti_ext}', data_path=nifti_dir, data_range=[800, 3200])
#
# #%% =============================================================================
# # white matter
#
# seg_name = seg_tools.connected_clusters(f'{UNI_name}_labels_0{nifti_ext}', cluster_size=500)
#
# #%% =============================================================================
# # grey matter
#
# # erode to disconnect klingons, cluster threshold them away, dilate back out again
# seg_name = seg_tools.morphology_op(f'{UNI_name}_labels_1{nifti_ext}', operation='erode', n_iterations=2)
# seg_name = seg_tools.connected_clusters(seg_name, cluster_size=500)
# seg_name = seg_tools.morphology_op(f'{UNI_name}_labels_1{nifti_ext}', operation='dilate', n_iterations=2)
#
# seg_tools.launch_itksnap(f'{UNI_name}{nifti_ext}', segmentation_file=f'{UNI_name}_labels_1{nifti_ext}')
#
# #%% =============================================================================
# # make layers
#
# #%% =============================================================================
# # project layers into EPI space
# =============================================================================


