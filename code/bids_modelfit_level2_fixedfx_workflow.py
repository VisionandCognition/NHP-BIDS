#!/usr/bin/env python3

""" 
This script performs modelfits on preprocessed fMRI data. It assumes 
that data is in BIDS format and that the data has undergone 
minimal processing, resampling, and preprocessing.

Level2 fixed effects analysis

Questions & comments: c.klink@nin.knaw.nl
"""

from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range

import os, shutil                             # system functions
import pandas as pd                           

import nipype.interfaces.io as nio            # Data i/o
import nipype.interfaces.fsl as fsl           # fsl
from nipype.interfaces import utility as niu  # Utilities
import nipype.pipeline.engine as pe           # pypeline engine
import nipype.algorithms.modelgen as model    # model generation

#import nipype.workflows.fmri.fsl as fslflows
import niflow.nipype1.workflows.fmri.fsl as fslflows
from subcode.filter_numbers import FilterNumsTask

ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = ds_root


def get_csv_stem(csv_file):
    csv_filename = csv_file.split('/')[-1]
    csv_stem = csv_filename.split('.')[0]
    return csv_stem


def create_workflow(out_label, contrasts_name, RegSpace):
    level2_workflow = pe.Workflow(name='level2flow')
    level2_workflow.base_dir = os.path.abspath(
        './workingdirs/level2flow/' + contrasts_name + '/' + RegSpace + '/level1')

    # ===================================================================
    #                  _____                   _
    #                 |_   _|                 | |
    #                   | |  _ __  _ __  _   _| |_
    #                   | | | '_ \| '_ \| | | | __|
    #                  _| |_| | | | |_) | |_| | |_
    #                 |_____|_| |_| .__/ \__,_|\__|
    #                             | |
    #                             |_|
    # ===================================================================

    # ------------------ Specify variables
    inputnode = pe.Node(niu.IdentityInterface(fields=[
        'ref_funcmask',
        'copes',
        'dof_file',
        'varcopes',
    ]), name="inputspec")


    # -------------------------------------------------------------------
    #            /~_ _  _  _  _. _   _ . _  _ |. _  _
    #            \_/(/_| |(/_| |(_  |_)||_)(/_||| |(/_
    #                               |   |
    # -------------------------------------------------------------------
    """
    Preliminaries
    -------------
    Setup any package specific configuration. The output file format for FSL
    routines is being set to compressed NIFTI.
    """

    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    fixed_fx = fslflows.create_fixed_effects_flow()

    def sort_copes(files):
        """ Sort by copes and the runs, ie.
            [[cope1_run1, cope1_run2], [cope2_run1, cope2_run2]]
        """
        assert files[0] is not str

        numcopes = len(files[0])
        assert numcopes > 1

        outfiles = []
        for i in range(numcopes):
            outfiles.insert(i, [])
            for j, elements in enumerate(files):
                outfiles[i].append(elements[i])
        return outfiles

    def num_copes(files):
        return len(files)

    # Level2 fixed effects
    level2_workflow.connect([
        (inputnode, fixed_fx,
        [('ref_funcmask', 'flameo.mask_file'),
         (('copes', sort_copes), 'inputspec.copes'),
         ('dof_file', 'inputspec.dof_files'),
         (('varcopes', sort_copes), 'inputspec.varcopes'),
         (('copes', num_copes), 'l2model.num_copes'),
        ])
    ])


    # ===================================================================
    #                   ____        _               _
    #                  / __ \      | |             | |
    #                 | |  | |_   _| |_ _ __  _   _| |_
    #                 | |  | | | | | __| '_ \| | | | __|
    #                 | |__| | |_| | |_| |_) | |_| | |_
    #                  \____/ \__,_|\__| .__/ \__,_|\__|
    #                                  | |
    #                                  |_|
    # ===================================================================

    # Datasink
    outputfiles = pe.Node(nio.DataSink(
                base_directory=ds_root,
                container='derivatives/modelfit/' +  contrasts_name + '/' + RegSpace + '/level2',
                parameterization=True),
                name="output_files")

    # Use the following DataSink output substitutions
    outputfiles.inputs.substitutions = [
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        ('/_mc_method_afni3dAllinSlices/', '/'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1'),
        (r'_refsub([a-zA-Z0-9]+)', r''),
    ]
    
    level2_workflow.connect([
        (fixed_fx, outputfiles,
         [('outputspec.res4d', 'fx.res4d'),
          ('outputspec.copes', 'fx.copes'),
          ('outputspec.varcopes', 'fx.varcopes'),
          ('outputspec.zstats', 'fx.zstats'),
          ('outputspec.tstats', 'fx.tstats'),
          ]),
        ])

    return(level2_workflow)


# ===================================================================
#                       ______ _
#                      |  ____(_)
#                      | |__   _ _ __
#                      |  __| | | '_ \
#                      | |    | | | | |
#                      |_|    |_|_| |_|
#
# ===================================================================

def run_workflow(csv_file, res_fld, contrasts_name, RegSpace):
    # Define outputfolder
    if res_fld == 'use_csv':
        # get a unique label, derived from csv name
        csv_stem = get_csv_stem(csv_file)
        out_label = csv_stem.replace('-', '_')  # replace - with _
    else:
        out_label = res_fld.replace('-', '_')  # replace - with _
    workflow = pe.Workflow(name='run_level2flow_' + out_label)
    workflow.base_dir = os.path.abspath('./workingdirs')

    from nipype import config, logging
    config.update_config(
        {'logging':
         {'log_directory': os.path.join(workflow.base_dir, 'logs'),
          'log_to_file': True,
          # 'workflow_level': 'DEBUG', #  << massive output
          # 'interface_level': 'DEBUG', #  << massive output
          'workflow_level': 'INFO',
          'interface_level': 'INFO',
          }})
    logging.update_logging(config)
    config.enable_debug_mode()

    # redundant with enable_debug_mode() ...
    workflow.stop_on_first_crash = True
    workflow.remove_unnecessary_outputs = False
    workflow.keep_inputs = True
    workflow.hash_method = 'content'

    modelfit = create_workflow(out_label, contrasts_name, RegSpace)

    inputnode = pe.Node(niu.IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'run_id',
        'refsubject_id',
    ]), name='input')

    assert csv_file is not None, "--csv argument must be defined!"

    if csv_file is not None:
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

      inputnode.iterables = [
            ('subject_id', sub_img),
            ('session_id', ses_img),
            ('run_id', run_img),
            ('refsubject_id', ref_img),
        ]
      inputnode.synchronize = True
    else:
      print("No csv-file specified. Don't know what data to process.")

   
    # Registration space determines which files to use
    if RegSpace == 'nmt':
        # use the warped files
        templates = {
            'ref_funcmask':  # was: manualmask
            'manual-masks/sub-{refsubject_id}/warps/'
            'sub-{subject_id}_func2nmt_mask_res-1x1x1.nii.gz',
            'copes':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'copes/sub-{subject_id}_ses-{session_id}_run-{run_id}/cope*.nii.gz',
            'dof_file':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'dof_files/sub-{subject_id}_ses-{session_id}_run-{run_id}/dof',
            'roi_file':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'roi_file/sub-{subject_id}_ses-{session_id}_run-{run_id}/*.nii.gz',
            'varcopes':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'varcopes/sub-{subject_id}_ses-{session_id}_run-{run_id}/varcope*.nii.gz',
        }  
    elif RegSpace == 'native':
        # use the functional files
        templates = {
            'ref_funcmask':  # was: manualmask
            'manual-masks/sub-{refsubject_id}/func/'
            'sub-{subject_id}_ref_func_mask_res-1x1x1.nii.gz',
            'copes':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'copes/sub-{subject_id}_ses-{session_id}_run-{run_id}/cope*.nii.gz',
            'dof_file':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'dof_files/sub-{subject_id}_ses-{session_id}_run-{run_id}/dof',
            'roi_file':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'roi_file/sub-{subject_id}_ses-{session_id}_run-{run_id}/*.nii.gz',
            'varcopes':
            'derivatives/modelfit/' + contrasts_name +'/' + RegSpace + '/level1/'
            'varcopes/sub-{subject_id}_ses-{session_id}_run-{run_id}/varcope*.nii.gz',
        }  
    else:
        raise RuntimeError('ERROR - Unknown reg-space "%s"' % RegSpace)

    inputfiles = pe.Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir),
        name='in_files')

    workflow.connect([
        (inputnode, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('refsubject_id', 'refsubject_id'),
          ('run_id', 'run_id'),
          ]),
    ])

    join_input = pe.JoinNode(
        niu.IdentityInterface(fields=[
            'copes',
            'dof_file',
            'varcopes',
            'ref_funcmask',
            ]
            ),
        joinsource='input',
        joinfield=[
            'copes',
            'dof_file',
            'varcopes',
            ],
        # unique=True,
        name='join_input')

    workflow.connect([
        (inputfiles, join_input,
         [
          ('copes', 'copes'),
          ('dof_file', 'dof_file'),
          ('varcopes', 'varcopes'),
          ('ref_funcmask', 'ref_funcmask'),
          ]),
        (join_input, modelfit,
         [
          ('copes', 'inputspec.copes'),
          ('dof_file', 'inputspec.dof_file'),
          ('varcopes', 'inputspec.varcopes'),
          ('ref_funcmask', 'inputspec.ref_funcmask'),
          ]),
    ])

    workflow.workflow_level = 'INFO'    # INFO/DEBUG
    # workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph(simple_form=True)
    workflow.write_graph(graph2use='colored', format='png', simple_form=True)
    workflow.run()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='Analyze model fit.')
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, and runs.')
    parser.add_argument('--contrasts', dest='contrasts_name', required=True,
                        help='Contrasts to use. Look in contrasts directory '
                        'for valid names (e.g. "ctcheckerboard" for '
                        'curve-tracing checkerboard localizer or '
                        '"curvetracing" or curve tracing experiment).')
    parser.add_argument('--resultfld', dest='res_fld', default='use_csv',
                        help='Define the name for output and workingdir '
                        'folders. If not unique it will append.'
                        'Default is the stem of the csv filename')
    parser.add_argument('--RegSpace',
                        dest='RegSpace', default='nmt',
                        help='Set space to perform modelfit in. ([nmt]/native)')

    args = parser.parse_args()
    run_workflow(**vars(args))
