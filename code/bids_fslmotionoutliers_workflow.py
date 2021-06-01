#!/usr/bin/env python3

""" 
This script performs additional motion outlier detection on preprocessed fMRI data.
It assumes that data is in BIDS format and that the data has undergone 
minimal processing, resampling, and preprocessing.

Questions & comments: c.klink@nin.knaw.nl
"""

import os                                    # system functions
import pandas as pd                          # data juggling

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl

from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.utility import Function
from nipype.pipeline.engine import Workflow, Node


def combine_outlier_files(fslmat,rafile,undist=True):
    import numpy as np
    import os
    
    try:
        fsl_mat = np.loadtxt(fslmat)
        fsl_outliers_present = True
    except:
        fsl_outliers_present = False
        fsl_mat = np.array([])
    ra_list = np.loadtxt(rafile) 
    

    if fsl_mat.size == 0: # only merge outlier files if additional outliers are detected
        print('fsl_mat size is 0')
        mergedoutliers_list = ra_list
    elif ra_list.size == 0:
        print('ra_list_size is 0')
        if fsl_mat.ndim > 1:
            mergedoutliers_list = np.nonzero(fsl_mat.sum(axis=1))[0]
            print('fsl_mat dim is > 1')
        else:
            mergedoutliers_list = np.nonzero(fsl_mat)[0]
            print('fsl_mat dim is 1 or less (prob 1)')

        print('mergedoutliers_list')
        print(mergedoutliers_list)
    else:
        print('ra_list_size is not 0')
        if fsl_mat.ndim > 1:
            print('fsl_mat dim is > 1')
            fsl_ind = np.nonzero(fsl_mat.sum(axis=1))[0]
        else:
            print('fsl_mat dim is 1 or less (prob 1)')
            fsl_ind = np.nonzero(fsl_mat)[0]

        print('tyrying to merge the two outliers lists')    
        print('fsl_ind')
        print(fsl_ind)
        print('ra_list')
        print(ra_list)
        
        mergedoutliers_list = np.unique(np.append(fsl_ind, 
            ra_list)).astype(int) 

        print('mergedoutliers_list')
        print(mergedoutliers_list)
   

    fn = rafile.split('/')[-1].split('_')

    print('fn')
    print(fn)

    if fn[7] == 'undistort':
        mergedoutliers_file = (
            fn[0] + '_' + fn[1] + '_' + fn[2] + '_' + fn[3] + '_' +
            fn[4] + '_' + fn[7] + '_mergedoutliers.txt')
    else:
        mergedoutliers_file = (
            fn[0] + '_' + fn[1] + '_' + fn[2] + '_' + fn[3] + '_' + 
            fn[4] + '_mergedoutliers.txt')
    
    print(mergedoutliers_file)    

    np.savetxt(mergedoutliers_file, mergedoutliers_list,fmt="%i")
    mergedoutliers_file = os.path.abspath(mergedoutliers_file)
    return mergedoutliers_file

def run_workflow(session=None, csv_file=None, undist=True):
    from nipype import config
    #config.enable_debug_mode()

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'derivatives/featpreproc/motion_outliers'
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

    # use undistorted epi's if these are requested (need to be generated with undistort workflow)
    if undist:
        func_flag = 'preproc_undistort'
    else:
        func_flag = 'preproc'
    
    
    # SelectFiles
    templates = {
        'motion_outlier_files':
        'derivatives/featpreproc/motion_outliers/sub-{subject_id}/'
        'ses-{session_id}/func/art.sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_' + func_flag + '_mc_maths_outliers.txt',

        'masks':
        'derivatives/featpreproc/motion_outliers/sub-{subject_id}/'
        'ses-{session_id}/func/mask.sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_' + func_flag + '_mc_maths.nii.gz',

        'motion_corrected':
        'derivatives/featpreproc/motion_corrected/sub-{subject_id}/'
        'ses-{session_id}/func/sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_' + func_flag + '_mc.nii.gz',
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
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        ('run_id_', 'run-'),
        ('/merged_outliers/', '/'),
        ('/fslmotionoutlier_file/', '/'),
        ('bold_res-1x1x1_' + func_flag + '_mc_outliers', func_flag + '_fslmotionoutliers'),
    ]

    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_run-([a-zA-Z0-9]*)_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'/sub-\3/ses-\2/func/'),
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
    fslmotionoutliers.connect(inputfiles, 'masks',
                        GetOutliers, 'mask')
    fslmotionoutliers.connect(GetOutliers, 'out_file',
                        outputfiles, 'fslmotionoutlier_file')

    
    # convert the fsl style design matrix to AFNI style volume indeces
    ConvToAFNI = Node(name='ConvtoAFNI',
                        interface=Function(input_names=['fslmat','rafile','undist'],
                                           output_names=['mergedoutliers_file'],
                                           function=combine_outlier_files,
                                           )
                        )

    fslmotionoutliers.connect(GetOutliers, 'out_file',
                        ConvToAFNI,'fslmat')
    fslmotionoutliers.connect(inputfiles, 'motion_outlier_files',
                        ConvToAFNI,'rafile')
    fslmotionoutliers.connect(ConvToAFNI, 'mergedoutliers_file',
                        outputfiles,'merged_outliers')

    fslmotionoutliers.stop_on_first_crash = False  # True
    fslmotionoutliers.keep_inputs = True
    fslmotionoutliers.remove_unnecessary_outputs = False
    fslmotionoutliers.write_graph()
    fslmotionoutliers.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Perform additional motion outlier detection.')
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, and runs.')
    parser.add_argument('--undist',
                        dest='undist', default=True,
                        help='Boolean indicating whether to use undistorted epis (default is True)')
    
    args = parser.parse_args()
    run_workflow(**vars(args))
