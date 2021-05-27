#!/usr/bin/env python3

# http://nipype.readthedocs.io/en/latest/users/examples/fmri_fsl.html
# http://miykael.github.io/nipype-beginner-s-guide/firstSteps.html#input-output-stream
import os                                    # system functions

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.afni as afni        # afni
from nipype.interfaces.utility import IdentityInterface

from nipype.pipeline.engine import Workflow, Node, MapNode

from nipype import config
config.enable_debug_mode()

from subcode.afni_allin_slices import AFNIAllinSlices

# the create_workflow_allin_slices workflow is the only one that's used
def create_workflow_allin_slices(name='motion_correction', iterfield=['in_file']):
    workflow = Workflow(name=name)
    inputs = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',

        'ref_func', 
        'ref_func_weights',

        'funcs',
        'funcs_masks',

        'mc_method',
    ]), name='in')
    inputs.iterables = [
        ('mc_method', ['afni:3dAllinSlices'])
    ]

    mc = MapNode(
        AFNIAllinSlices(),
        iterfield=iterfield,  
        name='mc')
    workflow.connect(
        [(inputs, mc,
          [('funcs', 'in_file'),
           ('ref_func_weights', 'in_weight_file'),
           ('ref_func', 'ref_file'),
           ])])
    return workflow

    # Outputs:
    #  * out_file
    #  * out_init_mc
    #  * out_warp_params
    #  * out_transform_matrix


def run_workflow(undist):
    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'motion-correction'
    working_dir = 'workingdirs/motion-correction'

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
        ('smooth', [1.0]),
        # ('dof', [6]),
        # ('mcflirt_stages', [3]),
    ]
    
    if undist:
        ud_flag = 'preproc_undist_PLUS'
    else:
        ud_flag = 'preproc' 
    
    # SelectFiles
    templates = {
        'funcs':
        'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/func/'
            'sub-{subject_id}_ses-{session_id}_'
            'task-*run-01*_bold_res-1x1x1_' + ud_flag + '.nii.gz',

        'manualweights':
        'manual-masks/sub-eddy/ses-20170511/func/'
            'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold_'
            'res-1x1x1_manualweights.nii.gz',

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

    mc = create_workflow_afni()

    workflow.connect(inputfiles, 'funcs',
                     mc, 'in.funcs')
    workflow.connect(inputfiles, 'manualweights',
                     mc, 'in.manualweights')
    workflow.connect(inputfiles, 'manualweights_func_ref',
                     mc, 'in.manualweights_func_ref')
    workflow.connect(mc, 'mc.out_file',
                     outputfiles, 'motioncorrected')

    workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    # run_workflow()
