#!/usr/bin/env python3

""" 
This script warps preprocessed fMRI timeseries to NMT space via pre-calculated warps

Questions & comments: c.klink@nin.knaw.nl
"""

import os                                    # system functions
import pandas as pd                          # data juggling

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.afni as afni        # afni

from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Workflow, Node


def run_workflow(project, session=None, csv_file=None, undist=True):
    from nipype import config
    #config.enable_debug_mode()

    # ------------------ Specify variables
    # ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # data_dir = ds_root
    # output_dir = 'derivatives/featpreproc/warp2nmt/highpassed_files'
    # working_dir = 'workingdirs'

    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) # NHP-BIDS fld
    data_dir = ds_root + '/projects/' + project
    output_dir = 'projects/' + project + '/derivatives/featpreproc/warp2nmt/highpassed_files'
    working_dir = 'projects/' + project + '/workingdirs'

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'run_id',
        'refsubject_id',
    ]), name="infosource")

    if csv_file is not None:
      print('=== reading csv ===')
      # Read csv and use pandas to set-up image and ev-processing
      df = pd.read_csv(csv_file)
      # init lists
      sub_img=[]; ses_img=[]; run_img=[]; ref_img=[]
      
      # fill lists to iterate mapnodes
      for index, row in df.iterrows():
        for r in row.run.strip("[]").split(" "):
            sub_img.append(row.subject)
            ses_img.append(row.session)
            run_img.append(r)
            if 'refsubject' in df.columns:
                if row.refsubject == 'nan':
                    # empty field
                    ref_img.append(row.subject)
                else:
                    # non-empty field
                    ref_img.append(row.refsubject) 
            else:
                ref_img.append(row.subject)

      infosource.iterables = [
            ('subject_id', sub_img),
            ('session_id', ses_img),
            ('run_id', run_img),
            ('refsubject_id', ref_img),
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
        'image': 
        'projects/' + project + '/derivatives/featpreproc/highpassed_files/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_' + func_flag + '_mc_smooth_mask_gms_tempfilt_maths.nii.gz',

        'imagewarp': 
        'reference-vols/sub-{refsubject_id}/transforms/'
        'sub-{subject_id}_func2nmt_WARP.nii.gz',

        'ref_image': 
        'reference-vols/sub-{refsubject_id}/transforms/'
        'sub-{subject_id}_func2nmt_res-1x1x1.nii.gz',
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
        ('_Nwarp.nii.gz', '_NMTv2.nii.gz'),
        # remove subdirectories:
        ('highpassed_files/reg_func', 'highpassed_files'),
    ]  
       
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1/func'),
        (r'_ref-([a-zA-Z0-9]+)_run_id_[0-9][0-9]', r''),
    ]


    # -------------------------------------------- Create Pipeline
    warp2nmt = Workflow(
        name='warp2nmt',
        base_dir=os.path.join(ds_root, working_dir))

    warp2nmt.connect([
        (infosource, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('run_id', 'run_id'),
          ('refsubject_id', 'refsubject_id'),
          ])])
       
    nwarp = Node(afni.NwarpApply(out_file='%s_Nwarp.nii.gz'),name='nwarp')       
    warp2nmt.connect(inputfiles, 'image',
                        nwarp, 'in_file')
    warp2nmt.connect(inputfiles, 'imagewarp',
                        nwarp, 'warp')
    warp2nmt.connect(inputfiles, 'ref_image',
                        nwarp, 'master')
    warp2nmt.connect(nwarp, 'out_file',
                        outputfiles, 'reg_func')

    warp2nmt.stop_on_first_crash = False  # True
    warp2nmt.keep_inputs = True
    warp2nmt.remove_unnecessary_outputs = False
    warp2nmt.write_graph()
    warp2nmt.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Warp preprocessed functionals to NMT space')
    parser.add_argument('--proj', dest='project', required=True,
                        help='project label for subfolder.')
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, runs, and reference subject.')
    parser.add_argument('--undist', dest='undist', default=True,
                        help='Boolean indicating whether to use undistorted epis (default is True)')
    
    args = parser.parse_args()

    run_workflow(**vars(args))
