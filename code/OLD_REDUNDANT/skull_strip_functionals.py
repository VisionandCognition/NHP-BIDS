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
    output_dir = 'skull-stripped-pre-mc'
    working_dir = 'workingdirs/skull-strip-functionals'

    subject_list = ['eddy']
    session_list = ['20170511']

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
    ]), name="infosource")

    infosource.iterables = [
        ('session_id', session_list),
        ('subject_id', subject_list),
    ]
    # SelectFiles
    templates = {
        'masks':
        'transformed-manual-func-mask/sub-{subject_id}/ses-{session_id}/func/'
            #  'sub-{subject_id}_ses-{session_id}*run-01_bold_res-1x1x1'
            'sub-{subject_id}_ses-{session_id}*_bold_res-1x1x1'
            '_transformedmask.nii.gz',

        'functionals':
        #  'func_unwarp/sub-{subject_id}/ses-{session_id}/func/'
        'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/func/'
            #  'sub-{subject_id}_ses-{session_id}*run-01_bold_res-1x1x1_preproc'
            'sub-{subject_id}_ses-{session_id}*_bold_res-1x1x1_preproc'
            '.nii.gz',
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
        ('/funcbrain/', '/'),
        ('_preproc_masked.nii.gz', '_brain.nii.gz'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)', r'sub-\2/ses-\1'),
        (r'_funcbrain[0-9]*/', r'func/'),
    ]

    # -------------------------------------------- Create Pipeline
    workflow = Workflow(
        name='transform_manual_func_mask',
        base_dir=os.path.join(ds_root, working_dir))

    workflow.connect([(infosource, inputfiles,
                      [('subject_id', 'subject_id'),
                       ('session_id', 'session_id'),
                       ])])

    dilmask = MapNode(fsl.DilateImage(
        operation='mean',
        kernel_shape=('boxv'),
        kernel_size=7,
    ), iterfield=['in_file'], name='dilmask')
    workflow.connect(inputfiles, 'masks',
                     dilmask, 'in_file')

    erode = MapNode(fsl.ErodeImage(
        kernel_shape=('boxv'),
        kernel_size=3,
    ), iterfield=['in_file'], name='erode')

    workflow.connect(dilmask, 'out_file',
                     erode, 'in_file')

    funcbrain = MapNode(
        fsl.ApplyMask(),
        iterfield=['in_file', 'mask_file'], name='funcbrain')
    workflow.connect(erode, 'out_file',
                     funcbrain, 'mask_file',
                     )
    workflow.connect(inputfiles, 'functionals',
                     funcbrain, 'in_file',
                     )
    workflow.connect(funcbrain, 'out_file',
                     outputfiles, 'funcbrain'
                     )

    workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    run_workflow()
