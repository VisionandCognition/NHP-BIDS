#!/usr/bin/env python3

# http://nipype.readthedocs.io/en/latest/users/examples/fmri_fsl.html
# http://miykael.github.io/nipype-beginner-s-guide/firstSteps.html#input-output-stream
import os                                    # system functions

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
import nipype.interfaces.fsl as fsl          # fsl
from nipype.interfaces.utility import IdentityInterface

from nipype.pipeline.engine import Workflow, Node, MapNode

from nipype import config
config.enable_debug_mode()


def run_workflow():
    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'motion-correction'
    working_dir = 'workingdirs/motion-correction'

    subject_list = ['eddy']
    session_list = ['20170511']

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'use_contours',
        'smooth',
        'dof',
        'mcflirt_stages',
    ]), name="infosource")

    infosource.iterables = [
        ('session_id', session_list),
        ('subject_id', subject_list),
        ('use_contours', [False]),
        ('smooth', [1.0]),
        ('dof', [6, 12]),
        ('mcflirt_stages', [3, 4]),
    ]
    # SelectFiles
    templates = {
        'func':
        'skull-stripped-pre-mc/sub-{subject_id}/ses-{session_id}/func/'
            'sub-{subject_id}_ses-{session_id}_'
            'task-*run-01_bold_res-1x1x1_brain.nii.gz',
        # 'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/func/'
        #     'sub-{subject_id}_ses-{session_id}_'
        #     'task-*_bold_res-1x1x1_preproc.nii.gz',
    }
    inputfiles = Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir), name="input_files")

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
        ('/motioncorrected/', '/'),
        ('_mcf.nii.gz', '.nii.gz')
        # BIDS Extension Proposal: BEP003
        # ('_resample.nii.gz', '_res-1x1x1_preproc.nii.gz'),
        # remove subdirectories:
        # ('resampled-isotropic-1mm/isoxfm-1mm', 'resampled-isotropic-1mm'),
        # ('resampled-isotropic-1mm/mriconv-1mm', 'resampled-isotropic-1mm'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)', r'sub-\2/ses-\1'),
        (r'_mcflirt[0-9]+/', r'func/'),
    ]

    # -------------------------------------------- Create Pipeline
    workflow = Workflow(
        name='motion_correction',
        base_dir=os.path.join(ds_root, working_dir))

    workflow.connect([(infosource, inputfiles,
                      [('subject_id', 'subject_id'),
                       ('session_id', 'session_id'),
                       ('use_contours', 'use_contours'),
                       ('mcflirt_stages', 'stages'),
                       ('smooth', 'smooth'),
                       ('dof', 'dof'),
                       ])])

    mcflirt = MapNode(
        fsl.MCFLIRT(
            save_plots=True,
            save_mats=True,
            save_rms=True,
            interpolation='spline',  # interpolation method for final stage
            # mean_vol=True,
            ref_vol=50,
        ),
        iterfield=['in_file'],
        name='mcflirt')

    workflow.connect(inputfiles, 'func',
                     mcflirt, 'in_file')
    workflow.connect(mcflirt, 'out_file',
                     outputfiles, 'motioncorrected')

    workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    run_workflow()
