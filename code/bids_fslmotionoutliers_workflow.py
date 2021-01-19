#!/usr/bin/env python3

""" 
This script performs additional motion outlier detection on preprocessed fMRI data.
It assumes that data is in BIDS format and that the data has undergone 
minimal processing, resampling, and preprocessing.

Questions & comments: c.klink@nin.knaw.nl
"""

import os, shutil                             # system functions
import pandas as pd                          # data juggling
import numpy as np

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl

from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Workflow, Node


def combine_outlier_files(org_file,new_mat)
	fsl_mat = np.loadtxt('new_mat.txt')
	ra_list = np.loadtxt('org_file')
	fsl_mat=np.nonzero(fsl_mat.sum(axis=1))[0]
	new_list=np.sort(np.append(fsl_mat, ra_list, axis=0)).astype(int)
	np.savetxt('newoutliers.txt',new_list,fmt="%i")


def run_workflow(session=None, csv_file=None):
    from nipype import config
    config.enable_debug_mode()

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'derivatives/featpreproc/fslmotionoutliers'
    working_dir = 'workingdirs'

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'run_id',
    ]), name="infosource")

    if csv_file is not None:
      print('=== reading csv ===')
      # Read csv and use pandas to set-up image and ev-processing
      df = pd.read_csv(csv_file)
      # init lists
      sub_img=[]; ses_img=[]; run_img=[];
      
      # fill lists to iterate mapnodes
      for index, row in df.iterrows():
        for r in row.run.strip("[]").split(" "):
            sub_img.append(row.subject)
            ses_img.append(row.session)
            run_img.append(r)

      infosource.iterables = [
            ('subject_id', sub_img),
            ('session_id', ses_img),
            ('run_id', run_img),
        ]
      infosource.synchronize = True
    else:
      print("No csv-file specified. Don't know what data to process.")


    # SelectFiles
    templates = {
        'motion_outlier_files':
        'derivatives/featpreproc/motion_outliers/sub-{subject_id}/'
        'ses-{session_id}/func/art.sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_preproc_mc_maths_outliers.txt',

        'masks':
        'derivatives/featpreproc/motion_outliers/sub-{subject_id}/'
        'ses-{session_id}/func/mask.sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_preproc_mc_maths.nii.gz',

        'motion_corrected':
        'derivatives/featpreproc/motion_corrected/sub-{subject_id}/'
        'ses-{session_id}/func/sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_preproc_mc.nii.gz',
        }  

    inputfiles = Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir), 
                        name="input_files")


    # ------------------ Output Files
    # Datasink
    outputfiles = Node(nio.DataSink(
        base_directory=ds_root,
        container=output_dir,
        parameterization=True),
        name="output_files")

    # Use the following DataSink output substitutions
    outputfiles.inputs.substitutions = [
        ('refsubject_id_', 'ref-'),
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        # remove subdirectories:
        ('fslmotionoutlier_file', 'fslmotionoutliers'),
    ]

    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1'),
        (r'_ref-([a-zA-Z0-9]+)_run_id_[0-9][0-9]', r''),
    ]

    # -------------------------------------------- Create Pipeline
    fslmotionoutliers = Workflow(
        name='fslmotionoutliers',
        base_dir=os.path.join(ds_root, working_dir))

    fslmotionoutliers.connect([
        (infosource, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('run_id', 'run_id'),
          ])])

    GetOutliers = Node(fsl.MotionOutliers(),
                        name='GetOutliers')

    GetOutliers.inputs.no_motion_correction=True

    fslmotionoutliers.connect(inputfiles, 'motion_corrected',
                        GetOutliers, 'in_file')
    fslmotionoutliers.connect(inputfiles, 'mask',
                        GetOutliers, 'mask')
    fslmotionoutliers.connect(GetOutliers, 'out_file',
                        outputfiles, 'fslmotionoutlier_file')

# outliers2 = MotionOutliers(
#     in_file='/*_preproc_mc.nii.gz',
#     no_motion_correction=True,
#     mask='/*_mask_res-1x1x1_dil.nii.gz',    
#     out_file='outliers2.txt',
#     out_metric_plot='outliers2.png'
# )

    fslmotionoutliers.stop_on_first_crash = False  # True
    fslmotionoutliers.keep_inputs = True
    fslmotionoutliers.remove_unnecessary_outputs = False
    fslmotionoutliers.write_graph()
    fslmotionoutliers.run()

    #

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Perform additional motion outlier detection.')
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, and runs.')

    args = parser.parse_args()
    run_workflow(**vars(args))
