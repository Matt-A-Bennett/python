#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created by Matthew A. Bennett (%(date)s)
Matthew.Bennett@glasgow.ac.uk
"""

#%%% =============================================================================
# imports
import os, glob
import json

from my_functions.misc import bash

#import nibabel
#import nipy
#from nipy.algorithms.registration import SpaceTimeRealign

from nipype.pipeline.engine import Node
from nipype.interfaces import nipy

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_plt

from pylab import MaxNLocator
#%%% =============================================================================
# paths and definitions

base_dir = '/analyse/Project0256/'

sub_folders = ['20190816_PFB06', '20190817_EPA14', '20190817_SLW06', '20190818_FUH13',
               '20190819_LDH12', '20190820_ULA08', '20190901_ALL21', '20190902_MZA30',
               '20190903_CGE02', '20190909_LLN21']

sub_folders = sub_folders[2:]

nifti_ext = '.nii.gz'
# format and store anatomical names

#%%% =============================================================================
# slice time, motion, and low freq drift correction
# use nipype here to get all the interplotations into one step? - did I make that up?

subs_processed_correctly = []
#%% =============================================================================
# preprocess the anatomical prior to segmentation
for sub_fold in sub_folders:

    try:
        sub_id = sub_fold[9:]
        print(f'n\Processing {sub_id}...')

        nifti_dir = f'{base_dir}{sub_fold}/sub-{sub_id}/func/'
        os.chdir(f'{nifti_dir}')

        # get run names
        runs = glob.glob('*.nii.gz')
        # remove extension
        runs = [run for run in runs]
        runs.sort()
        # move retmap run to end of list (if not PFB06)
        if sub_id != 'PFB06':
            runs.append(runs.pop(runs.index(f'sub-{sub_id}_bold_rmpaecc.nii.gz')))

        print('\n*** GET SLICE TIMES AND TR ***\n')
        with open(f'{runs[0][:-7]}.json') as json_file:
            json_contents = json.load(json_file)
            slice_times = json_contents['SliceTiming']
            TR = json_contents['RepetitionTime']

        print('\n*** SPACETIME_REALIGN ***\n')
        # Roche, A. (2011). A four-dimensional registration algorithm with application to joint
        # correction of motion and slice timing in fMRI. IEEE transactions on medical imaging,
        # 30(8), 1546-1554.
        realign = Node(nipy.SpaceTimeRealigner(), name="spacetime_realign")
        realign.base_dir = nifti_dir
        realign.inputs.in_file = [nifti_dir+run for run in runs]
        realign.inputs.slice_times = slice_times # CHECK HOW THESE ARE INTERPRETED
        realign.inputs.tr = TR
        realign.inputs.slice_info = 2
        realign.run()

        print('\n*** MOVE DATA ***\n')
        for file in glob.glob(f'spacetime_realign/*.nii.gz'):
            new_name = file[23:]
            new_name_parts = new_name.split('.')
            os.rename(file, f"{new_name_parts[0]}_corr.{'.'.join(new_name_parts[1:])}")

        print('\n*** MOCO PLOTS ***\n')
        pdf = pdf_plt.PdfPages(f'spacetime_realign/{sub_id}_motion_correction_plots.pdf')
        for run in runs:
            with open(f'spacetime_realign/{run}.par') as moco_params:
                moco_params = moco_params.readlines()
                # remove '\n'
                moco_params = [vol[:-1] for vol in moco_params]
                moco_params = [vol.split() for vol in moco_params]
                moco_params = np.array(moco_params, dtype='float64')
                # set first vol to zero
                moco_params -= moco_params[0]

                moco_params = [moco_params[:,0:3], moco_params[:,3:6]]

                plt.style.use('seaborn-whitegrid')
                fig = plt.figure()

                for plot in range(2):
                    plt.subplot(2,1,plot+1)
                    ax = fig.gca()
                    x_ax = ax.get_xaxis()
                    x_ax.set_major_locator(MaxNLocator(integer=True))
                    if plot == 0:
                        plt.title(f'Motion correction: {run}')
                        plt.ylim(-1, 1)
                        if np.max(moco_params[0])>1 or np.min(moco_params[0])<-1:
                            plt.autoscale(enable=True, axis='y')
                        plt.ylabel('Translation (mm)')
                    elif plot == 1:
                        plt.ylim(-0.02, 0.02)
                        if np.max(moco_params[1])>0.02 or np.min(moco_params[1])<-0.02:
                            plt.autoscale(enable=True, axis='y')
                        plt.xlabel('Volumes')
                        plt.ylabel('Rotation')

                    plt.plot(range(1,len(moco_params[plot])+1), moco_params[plot], '-')

                pdf.savefig(fig)
        pdf.close()
        plt.close('all')

        # create a single volume using the average of all run1 volumes
        bash(f"fslmaths {nifti_dir}{runs[2]} -Tmean {nifti_dir}{runs[2].split('.')[0]}_mean.{'.'.join(runs[2].split('.')[1:])}")

#        print('\n*** LOAD FUNCTION RUNS ***\n')
#        runs = [nibabel.load(f'{run}{nifti_ext}') for run in runs]
#
#        print('\n*** CREATE SPACETIME_REALIGN OBJECT ***\n')
#        sptr = SpaceTimeRealign(images=runs, tr=TR, slice_times=slice_times, slice_info=2)
#
#        print('\n*** ESTIMATE MOTION AND SLICE TIME CORRECTIONS ***\n')
#        sptr.estimate()
#
#        print('\n*** APPLY MOTION AND SLICE TIME CORRECTIONS ***\n')
#        # what resample method do they use? sinc?
#        corr_runs = sptr.resample()
#
#        print('\n*** SAVE CORRECTED RUNS ***\n')
#        for idx, corr_run in enumerate(corr_runs):
#            nipy.io.files.save(corr_run, filename=f'{runs[idx]}_corr{nifti_ext}')

        subs_processed_correctly.append(sub_id)

        # ESTIMATE TOPUP??

        # APPLY TOPUP? TO T2w??

    except:
        continue
