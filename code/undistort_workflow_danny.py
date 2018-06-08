#!/usr/bin/env python3

# http://nipype.readthedocs.io/en/latest/users/examples/fmri_fsl.html
# http://miykael.github.io/nipype-beginner-s-guide/firstSteps.html#input-output-stream
import os                                    # system functions

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
from nipype.interfaces.utility import IdentityInterface

from nipype.interfaces.fsl.preprocess import PRELUDE
from nipype.interfaces.fsl.preprocess import FUGUE
from nipype.interfaces.fsl.preprocess import BET

from nipype.pipeline.engine import Workflow, Node, MapNode, JoinNode

from nipype import config

# This pipeline depends on transform_manual_fmap_mask


def create_workflow(unwarp_direction='y'):
    workflow = Workflow(
        name='func_unwarp')

    inputs = Node(IdentityInterface(fields=[
        # 'subject_id',
        # 'session_id',
        'funcs',
        'funcmasks',
        'fmap_phasediff',
        'fmap_magnitude',
        'fmap_mask',
    ]), name='in')

    outputs = Node(IdentityInterface(fields=[
        'funcs',
        'funcmasks',
    ]), name='out')

    # --- --- --- --- --- --- --- Convert to radians --- --- --- --- --- ---

    # fslmaths $FUNCDIR/"$SUB"_B0_phase -div 100 -mul 3.141592653589793116
    #     -odt float $FUNCDIR/"$SUB"_B0_phase_rescaled

    # in_file --> out_file
    phase_radians = Node(fsl.ImageMaths(
        op_string='-mul 3.141592653589793116 -div 100',
        out_data_type='float',
        suffix='_radians',
    ), name='phaseRadians')

    workflow.connect(inputs, 'fmap_phasediff', phase_radians, 'in_file')

    # --- --- --- --- --- --- --- Unwrap Fieldmap --- --- --- --- --- ---
    # --- Unwrap phase
    # prelude -p $FUNCDIR/"$SUB"_B0_phase_rescaled
    #         -a $FUNCDIR/"$SUB"_B0_magnitude
    #         -o $FUNCDIR/"$SUB"_fmri_B0_phase_rescaled_unwrapped
    #         -m $FUNCDIR/"$SUB"_B0_magnitude_brain_mask
    #  magnitude_file, phase_file [, mask_file] --> unwrapped_phase_file
    unwrap = MapNode(
        PRELUDE(),
        name='unwrap',
        iterfield=['mask_file'],
    )

    workflow.connect([
        (inputs, unwrap, [('fmap_magnitude', 'magnitude_file')]),
        (inputs, unwrap, [('fmap_mask', 'mask_file')]),
        (phase_radians, unwrap, [('out_file', 'phase_file')]),
    ])

    # --- --- --- --- --- --- --- Convert to Radians / Sec --- --- --- --- ---
    # fslmaths $FUNCDIR/"$SUB"_B0_phase_rescaled_unwrapped
    #          -mul 200 $FUNCDIR/"$SUB"_B0_phase_rescaled_unwrapped
    rescale = MapNode(
        fsl.ImageMaths(op_string='-mul 200'),
        name='rescale',
        iterfield=['in_file'],
    )

    workflow.connect(unwrap, 'unwrapped_phase_file',
                     rescale, 'in_file')

    # --- --- --- --- --- --- --- Unmask fieldmap --- --- --- --- ---

    unmask_phase = MapNode(
        FUGUE(
            save_unmasked_fmap=True,
            unwarp_direction=unwarp_direction,
        ),
        name='unmask_phase',
        iterfield=['mask_file', 'fmap_in_file'],
    )

    workflow.connect(rescale, 'out_file', unmask_phase, 'fmap_in_file')
    workflow.connect(inputs, 'fmap_mask', unmask_phase, 'mask_file')

    # --- --- --- --- --- --- --- Undistort functionals --- --- --- --- ---
    # phasemap_in_file = phasediff
    # mask_file = mask
    # in_file = functional image
    # dwell_time = 0.0005585 s
    # unwarp_direction

    undistort = MapNode(
        FUGUE(
            dwell_time=0.0005585,
            # based on Process-NHP-MRI/Process_functional_data.md:
            asym_se_time=0.020,
            smooth3d=2.0,
            median_2dfilter=True,
            unwarp_direction=unwarp_direction,
        ),
        name='undistort',
        iterfield=['in_file', 'mask_file', 'fmap_in_file'],
    )

    workflow.connect(unmask_phase, 'fmap_out_file',
                     undistort, 'fmap_in_file')
    workflow.connect(inputs, 'fmap_mask',
                     undistort, 'mask_file')
    workflow.connect(inputs, 'funcs',
                     undistort, 'in_file')

    undistort_masks = undistort.clone('undistort_masks')
    workflow.connect(unmask_phase, 'fmap_out_file',
                     undistort_masks, 'fmap_in_file')
    workflow.connect(inputs, 'fmap_mask',
                     undistort_masks, 'mask_file')
    workflow.connect(inputs, 'funcmasks',
                     undistort_masks, 'in_file')

    workflow.connect(undistort, 'unwarped_file',
                     outputs, 'funcs')

    workflow.connect(undistort_masks, 'unwarped_file',
                     outputs, 'funcmasks')
    return workflow


def run_workflow():
    raise Exception("This code was not tested after refactoring to be used by "
                    "preprocessing_workflow.py.")
    config.enable_debug_mode()

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'func_unwarp'
    working_dir = 'workingdirs/func_unwarp'

    subject_list = ['danny']
    session_list = ['20180117']

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
        'funcs':
        'derivatives/resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/func/'
            'sub-{subject_id}_ses-{session_id}_'
            'task-*_bold_res-1x1x1_preproc.nii.gz',

        # Use *-roi for testing
        #    'task-curvetracing_run-01_bold_res-1x1x1_preproc-roi.nii.gz',

        'fmap_phasediff':
        'derivatives/resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
            'sub-{subject_id}_ses-{session_id}_phasediff_res-1x1x1_preproc'
            '.nii.gz',

        'fmap_magnitude':
        'derivatives/resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
            'sub-{subject_id}_ses-{session_id}_magnitude1_res-1x1x1_preproc'
            '.nii.gz',

        'fmap_mask':
        'manual-masks/sub-{subject_id}/ses-{session_id}/fmap/'
            'sub-{subject_id}_ses-{session_id}_'
            'fmap_brainmask.nii.gz',
    }
    inputfiles = Node(
        nio.SelectFiles(
            templates, base_directory=data_dir), name="input_files")

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
        ('/undistorted/', '/'),
        ('/undistorted_masks/', '/'),
        ('_unwarped.nii.gz', '.nii.gz'),
        ('phasediff_radians_unwrapped_mask', '_rec-unwrapped_phasediff'),
    ]
    outputfiles.inputs.regexp_substitutions = [
        (r'_fugue[0-9]+/', r'func/'),
        (r'_undistort_masks[0-9]+/', r'func/'),
        (r'_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)', r'sub-\2/ses-\1')]

    # -------------------------------------------- Create Pipeline

    workflow = Workflow(
        name='undistort',
        base_dir=os.path.join(ds_root, working_dir))

    workflow.connect([(infosource, inputfiles,
                      [('subject_id', 'subject_id'),
                       ('session_id', 'session_id')])])

    undistort_flow = create_workflow()

    # Connect sub-workflow inputs
    workflow.connect([(inputfiles, undistort_flow,
                      [('subject_id', 'in.subject_id'),
                       ('session_id', 'in.session_id'),
                       ('fmap_phasediff', 'in.fmap_phasediff'),
                       ('fmap_magnitude', 'in.fmap_magnitude'),
                       ('fmap_mask', 'in.fmap_mask'),
                       ]),
                      (undistort_flow, outputfiles,
                       [('out.unwarped_file', 'undistorted'),
                        ])
                      ])

    workflow.connect(undistort_flow, 'unwarped_file',
                     outputfiles, 'undistorted')
    workflow.connect(undistort_masks, 'unwarped_file',
                     outputfiles, 'undistorted_masks')

    workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    run_workflow()
