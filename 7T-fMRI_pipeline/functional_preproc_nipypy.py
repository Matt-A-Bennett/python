#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by Matthew A. Bennett (%(date)s)
Matthew.Bennett@glasgow.ac.uk
"""

#%%% =============================================================================
# imports
# Import modules
import os
from os.path import join as opj

from nipype.pipeline.engine import Workflow, Node
from nipype import Function
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces import fsl
from nipype.interfaces import nipy

import json
import nibabel as nib

#%%% =============================================================================
# paths and definitions

base_dir = '/analyse/Project0075/Test_GVW19'

dicom_dir = base_dir
nifti_dir = f'{base_dir}/Nifti_conversion'
output_dir = f'{base_dir}/Nifti_conversion/output'
working_dir = f'{base_dir}/Nifti_conversion/working'

# if we need to create the directory
if not os.path.isdir(nifti_dir):
    os.mkdir(nifti_dir)

os.chdir(nifti_dir)

functional_names = ['cmrr_mbep2d_bold_AP_MB2_run1_16.nii.gz']

nifti_ext = '.nii.gz'

# determine slice timings and TR from json
with open(f'{nifti_dir}/{functional_names[0][:-7]}.json') as json_file:
    json_contents = json.load(json_file)
    slice_times = json_contents['SliceTiming']
    TR = json_contents['RepetitionTime']

#%%% =============================================================================
# Specify Nodes for the main workflow

# this does both at once:
# Roche, A. (2011). A four-dimensional registration algorithm with application to joint
# correction of motion and slice timing in fMRI. IEEE transactions on medical imaging,
# 30(8), 1546-1554.
realign = Node(nipy.SpaceTimeRealigner(), name="spacetime_realign")
realign.inputs.in_file = f'{nifti_dir}/{functional_names[0]}'
realign.inputs.slice_times = slice_times # CHECK HOW THESE ARE INTERPRETED
realign.inputs.tr = TR
realign.inputs.slice_info = 2
realign.run()


import matplotlib.pyplot as plt

no_moco = nib.load(f'{nifti_dir}/{functional_names[0]}')

moco = nib.load(f'/tmp/tmpi0ohe3ca/spacetime_realign/corr_{functional_names[0]}')

data = moco.get_fdata()

plt.figure()
for volume in range(data.shape[3]):

    plt.imshow(data[:,:,30,volume])
    plt.pause(0.05)
    plt.draw()
plt.show()



# topup
topup = fsl.TOPUP(name="topup")
topup.inputs.in_file = "b0_b0rev.nii"
topup.inputs.encoding_file = "topup_encoding.txt"
topup.inputs.output_type = "NIFTI_GZ"

applytopup = fsl.ApplyTOPUP(name="applytopup")
applytopup.inputs.in_files = ["epi.nii", "epi_rev.nii"]
applytopup.inputs.encoding_file = "topup_encoding.txt"
applytopup.inputs.in_topup_fieldcoef = "topup_fieldcoef.nii.gz"
applytopup.inputs.in_topup_movpar = "topup_movpar.txt"
applytopup.inputs.output_type = "NIFTI_GZ"

# average run to a single volume


#%%% =============================================================================
# Specify Workflows & Connect Nodes
func_preproc = Workflow(name='func_preproc')
func_preproc.base_dir = opj(nifti_dir, working_dir)

func_preproc.connect([(mcflirt, slicetimer, [('out_file', 'in_file')])
                    ])

#%% =============================================================================
# Input & Output Stream

# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['scan_id']),
    name="infosource")

infosource.iterables = [('scan_id', scan_list)]

# SelectFiles
templates = {'struct': f'{anat_name}.nii'}
selectfiles = Node(SelectFiles(templates,
                               base_directory=nifti_dir),
    name="selectfiles")

# Datasink
datasink = Node(DataSink(base_directory=nifti_dir,
                         container=output_dir),
    name="datasink")

## Connect SelectFiles and DataSink to the workflow
#func_preproc.connect([(infosource, selectfiles, [('scan_id', 'scan_id')]),
#                 (selectfiles, extract, [('struct', 'in_file')]),
#                 (extract, datasink, [('out_file', 'extract')]),
#                 (segmentation, datasink, [('tissue_class_map', 'segmentation')]),
#                 ])

# Connect SelectFiles and DataSink to the workflow
func_preproc.connect([(infosource, selectfiles, [('scan_id', 'scan_id')]),
                            (selectfiles, mcflirt, [('struct', 'in_file')]),
                            (mcflirt, datasink, [('par_file', 'preproc.@par')]),
                    ])

#%%% =============================================================================
#

