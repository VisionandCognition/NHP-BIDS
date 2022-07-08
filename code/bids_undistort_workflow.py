#!/usr/bin/env python3

""" 
This script undistorts epi-images using blip up/down images
acquired with opposing phase-encoding directions. This will
likely improve alignment both to the reference epi as well
as to any anatomical scan.

- bids_preprocessing_workflow.py
  >> performs preprocessing steps like normalisation and motion correction
- bids_modelfit_workflow.py
  >> Fits a GLM and outputs statistics

Questions & comments: c.klink@nin.knaw.nl
"""

import os, glob                             # system functions
import pandas as pd                          # data juggling

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.afni as afni          # afni

from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Workflow, Node


def run_workflows(project, session=None, csv_file=None):
    from nipype import config
    #config.enable_debug_mode()

    # ------------------ Specify variables
    # ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # data_dir = ds_root
    # output_dir = 'derivatives/undistort'
    # working_dir = 'workingdirs'

    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) # NHP-BIDS fld
    data_dir = ds_root + '/projects/' + project
    output_dir = 'projects/' + project + '/derivatives/undistort'
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


    # SelectFiles
    templates = {
        'image': 
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_preproc.nii.gz',
        'image_invPE': 
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/fmap/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_epi_res-1x1x1_preproc.nii.gz',
    }
    
    inputfiles = Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir), 
                        name="input_files")

    # Datasink
    outfiles = Node(nio.DataSink(
        base_directory=ds_root,
        container=output_dir,
        parameterization=True),
        name="outfiles")

    # Use the following DataSink output substitutions
    outfiles.inputs.substitutions = [
        ('refsubject_id_', 'ref-'),
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        ('resampled-isotropic-1mm','undistort'),
        ('undistort/ud_func', 'undistort'),
    ]  
       
    outfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1/func'),
        (r'_ref-([a-zA-Z0-9]+)_run_id_[0-9][0-9]', r''),
    ]
    
    templates_mv = {
        'ud_minus': 
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_preproc_MINUS.nii.gz',
        'ud_minus_warp': 
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_preproc_MINUS_WARP.nii.gz',
        'ud_plus': 
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_preproc_PLUS.nii.gz',
        'ud_plus_warp': 
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_preproc_PLUS_WARP.nii.gz',
    }
    
    mv_infiles = Node(
        nio.SelectFiles(templates_mv,
                        base_directory=data_dir), 
                        name="mv_infiles")

    # Datasink
    mv_outfiles = Node(nio.DataSink(
        base_directory=ds_root,
        container=output_dir,
        parameterization=True),
        name="mv_outfiles")

    # Use the following DataSink output substitutions
    mv_outfiles.inputs.substitutions = [
        ('refsubject_id_', 'ref-'),
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        ('resampled-isotropic-1mm','undistort'),
        ('undistort/ud_func', 'undistort'),
    ]  
       
    mv_outfiles.inputs.regexp_substitutions = [
        (r'sub-([a-zA-Z0-9]+)_ses-([a-zA-Z0-9]+)', r'sub-\1/ses-\2/func/qwarp_plusminus/sub-\1_ses-\2'),
    ]    
    
    # -------------------------------------------- Create Pipeline
    undistort = Workflow(
        name='undistort',
        base_dir=os.path.join(ds_root, working_dir))

    undistort.connect([
        (infosource, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('run_id', 'run_id'),
          ('refsubject_id', 'refsubject_id'),
          ])])
               
    qwarp = Node(afni.QwarpPlusMinus(
        nopadWARP=True,outputtype='NIFTI_GZ'),
                    iterfield=('in_file'),name='qwarp')       
        
    undistort.connect(inputfiles, 'image',
                        qwarp, 'in_file')
    undistort.connect(inputfiles, 'image_invPE',
                        qwarp, 'base_file') 
    undistort.connect(inputfiles, 'image',
                        qwarp, 'out_file')    
  
    nwarp = Node(afni.NwarpApply(out_file='%s_undistort.nii.gz'),name='nwarp')
    
    undistort.connect(inputfiles, 'image',
                     nwarp, 'in_file')
    undistort.connect(qwarp, 'source_warp',
                     nwarp, 'warp')
    undistort.connect(inputfiles, 'image',
                     nwarp, 'master')
    undistort.connect(nwarp, 'out_file',
                     outfiles, 'ud_func')

    undistort.stop_on_first_crash = False  # True
    undistort.keep_inputs = True
    undistort.remove_unnecessary_outputs = False
    undistort.write_graph()
    undistort.run()

    mv_ud = Workflow(
        name='mv_ud',
        base_dir=os.path.join(ds_root, working_dir))

    mv_ud.connect([
        (infosource, mv_infiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('run_id', 'run_id'),
          ('refsubject_id', 'refsubject_id'),
          ])])
    
    mv_ud.connect(mv_infiles, 'ud_minus',
                        mv_outfiles, 'ud_func.@ud_minus')
    mv_ud.connect(mv_infiles, 'ud_plus',
                        mv_outfiles, 'ud_func.@ud_plus')
    mv_ud.connect(mv_infiles, 'ud_minus_warp',
                        mv_outfiles, 'ud_func.@ud_minus_warp')
    mv_ud.connect(mv_infiles, 'ud_plus_warp',
                        mv_outfiles, 'ud_func.@ud_plus_warp')
    
    mv_ud.stop_on_first_crash = False  # True
    mv_ud.keep_inputs = True
    mv_ud.remove_unnecessary_outputs = False
    mv_ud.write_graph()
    mv_ud.run()

    # remove the undistorted files from the ...derivatives/resampled folder
    for index, row in df.iterrows():
        fpath = os.path.join(data_dir,'derivatives','resampled-isotropic-1mm',
                     'sub-' + row.subject,'ses-' + str(row.session),'func')
        for f in glob.glob(os.path.join(fpath,'*US*.nii.gz')):
            os.remove(f)
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Perform undistortion correction using epi scans with opposing phase-encoding directions. Run bids_minimal_processing and bids_resample_isotropic first.')
    parser.add_argument('--proj', dest='project', required=True,
                        help='project label for subfolder.')
    parser.add_argument('--csv', dest='csv_file', default=None,
                        help='CSV file with at least subjects and sessions columns.')

    args = parser.parse_args()

    run_workflows(**vars(args))
