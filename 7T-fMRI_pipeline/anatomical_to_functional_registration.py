#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by Matthew A. Bennett (%(date)s)

Matthew.Bennett@glasgow.ac.uk
"""

#%%% =======================================================================================
# imports
import os, glob
from my_functions.misc import bash

#%%% =======================================================================================
# paths and definitions

base_dir = '/analyse/Project0256/'

sub_folders = ['20190816_PFB06', '20190817_EPA14', '20190817_SLW06', '20190818_FUH13',
               '20190819_LDH12', '20190820_ULA08', '20190901_ALL21', '20190902_MZA30',
               '20190903_CGE02', '20190909_LLN21']

sub_folders = sub_folders[1:]

nifti_ext = '.nii.gz'
# format and store anatomical names

#%% =============================================================================
# register anatomical to functional epi:
# 1) map mp2rage to T2w in itksnap
# 2) map from T2w to epi in itksnap
# 3) nonlinear map from T2w to average epi in using ANTs
# 4) apply above transforms in one step to e.g. mp2rage/segmentation/ROIs

subs_processed_correctly = []

for sub_fold in sub_folders:

    try:
        sub_id = sub_fold[9:]
        print(f'Processing {sub_id}...')
        print('')

        nifti_dir = f'{base_dir}{sub_fold}/sub-{sub_id}/func/'
        os.chdir(f'{nifti_dir}')

        nifti_dir_anat = f'{base_dir}{sub_fold}/sub-{sub_id}/anat/'
        os.chdir(f'{nifti_dir}')

        UNI_name = f'sub-{sub_id}_UNI'
        T2w_name = f'sub-{sub_id}_T2w'

        st_im = f'{nifti_dir}sub-{sub_id}_run-01_bold_mean'
        mv_im = f'{nifti_dir_anat}{T2w_name}_skullstrip_upsample0p4'

        # do the alignments
        bash(f"itksnap -g {st_im}{nifti_ext} -o {mv_im}{nifti_ext}")
        bash(f'itksnap -g {mv_im}{nifti_ext} -o {nifti_dir_anat}dnoised_{UNI_name}_skullstrip_inhom_corr_upsample0p4{nifti_ext}')

        # use ANTs to add a nonlinear algignment of the anatomical to the functional

        T2w_to_func_init = f'{nifti_dir}T2w_to_func_CC_Affine.txt'
        UNI_to_T2w = f'{nifti_dir_anat}UNI_to_T2w.txt'
        #mask=f'{nifti_dir}/alignment_mask{nifti_ext}'

        # put this after the --output flag if using mask
        #--masks [$mask, $mask] \

        call_to_ANTs = f'antsRegistration \
        --verbose 1 \
        --dimensionality 3 \
        --float 0 \
        --output [ANTs_, ANTs_Warped{nifti_ext},ANTs_InverseWarped{nifti_ext}] \
        --interpolation Linear \
        --use-histogram-matching 0 \
        --winsorize-image-intensities [0.005,0.995] \
        --initial-moving-transform {T2w_to_func_init} \
        --transform Rigid[0.05] \
        --metric MI[{st_im}{nifti_ext},{mv_im}{nifti_ext},0.7,32,Regular,0.1] \
        --convergence [1000x500,1e-6,10] \
        --shrink-factors 2x1 \
        --smoothing-sigmas 1x0vox \
        --transform Affine[0.1] \
        --metric MI[{st_im}{nifti_ext},{mv_im}{nifti_ext},0.7,32,Regular,0.1] \
        --convergence [1000x500,1e-6,10] \
        --shrink-factors 2x1 \
        --smoothing-sigmas 1x0vox \
        --transform SyN[0.1,3,0] \
        --metric CC[{st_im}{nifti_ext},{mv_im}{nifti_ext},1,4] \
        --convergence [100x70x50x20,1e-6,10] \
        --shrink-factors 4x4x2x1 \
        --smoothing-sigmas 3x2x1x0vox'

        bash(f'{call_to_ANTs}')

        #%%% =============================================================================
        # move mp2rage into epi space, using above transform

#        mv_im=f'{nifti_dir_anat}dnoised_{UNI_name}_skullstrip_inhom_corr_upsample0p4'
        mv_im=f'{nifti_dir_anat}test_native_upscale'

        #mask=f'{nifti_dir}/alignment_mask{nifti_ext}'

        # put this after the --output flag if using mask
        #--masks [$mask, $mask] \


        call_to_ANTs = f'antsApplyTransforms \
        --interpolation Linear \
        --dimensionality 3 \
        --input {mv_im}{nifti_ext} \
        --reference-image {st_im}{nifti_ext} \
        --transform ANTs_1Warp{nifti_ext} \
        --transform ANTs_0GenericAffine.mat \
        --transform {UNI_to_T2w} \
        --output ANTs_WM_to_func_Warped3{nifti_ext}'

        bash(f'{call_to_ANTs}')


        subs_processed_correctly.append(sub_id)
    except:
        continue

#%%% =======================================================================================
#

#%%% =======================================================================================
#



