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

from nipype.interfaces.base import File


class ApplyXFMInputSpecRefName(fsl.preprocess.ApplyXFMInputSpec):
    out_file = File(argstr='-out %s', desc='registered output file',
                    name_source=['reference'], name_template='%s_flirt',
                    position=2, hash_files=False)


class ApplyXFMRefName(fsl.FLIRT):
    """Currently just a light wrapper around FLIRT,
    with no modifications
    ApplyXFMRefName uses the reference for naming the functional mask.
    """
    input_spec = ApplyXFMInputSpecRefName


def run_workflow():
    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'transformed-manual-func-mask'
    working_dir = 'workingdirs/transform_manual_func_mask'

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
        'manualmask':
        'manual-masks/sub-eddy/ses-20170511/func/'
            'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold'
            '_res-1x1x1_manualmask.nii.gz',

        'manualmask_func_ref':
        'manual-masks/sub-eddy/ses-20170511/func/'
            'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold'
            '_res-1x1x1_reference.nii.gz',

        'functionals':
        'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/func/'
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
        ('/mask/', '/'),
        ('_preproc_flirt_thresh.nii.gz', '_transformedmask.nii.gz'),
        #   ('/_findtrans0/', '/fmap/'),
        #   ('_magnitude1_res-1x1x1_manualmask_flirt',
        #    '_magnitude1_res-1x1x1_preproc'),
        # BIDS Extension Proposal: BEP003
        # ('_resample.nii.gz', '_res-1x1x1_preproc.nii.gz'),
        # remove subdirectories:
        # ('resampled-isotropic-1mm/isoxfm-1mm', 'resampled-isotropic-1mm'),
        # ('resampled-isotropic-1mm/mriconv-1mm', 'resampled-isotropic-1mm'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)', r'sub-\2/ses-\1'),
        (r'_maskthresh[0-9]*/', r'func/'),
    ]

    # -------------------------------------------- Create Pipeline
    workflow = Workflow(
        name='transform_manual_func_mask',
        base_dir=os.path.join(ds_root, working_dir))

    workflow.connect([(infosource, inputfiles,
                      [('subject_id', 'subject_id'),
                       ('session_id', 'session_id'),
                       ])])

    # Find the transformation matrix func_ref -> func
    # First find transform from func to manualmask's ref func
    findtrans = MapNode(fsl.FLIRT(),
                        iterfield=['in_file'],
                        name='findtrans'
                        )
    workflow.connect(inputfiles, 'functionals',
                     findtrans, 'in_file')
    workflow.connect(inputfiles, 'manualmask_func_ref',
                     findtrans, 'reference')

    # Invert the matrix transform
    invert = MapNode(fsl.ConvertXFM(invert_xfm=True),
                     name='invert',
                     iterfield=['in_file'],
                     )
    workflow.connect(findtrans, 'out_matrix_file',
                     invert, 'in_file')

    # Transform the manualmask to be aligned with func
    funcreg = MapNode(ApplyXFMRefName(),
                      name='funcreg',
                      iterfield=['in_matrix_file', 'reference'],
                      )

    workflow.connect(invert, 'out_file',
                     funcreg, 'in_matrix_file')
    workflow.connect(inputfiles, 'manualmask',
                     funcreg, 'in_file')
    workflow.connect(inputfiles, 'functionals',
                     funcreg, 'reference')

    # Threshold the image
    #  maskthresh = MapNode(fsl.maths.Threshold(thresh=0.3),
    #                       name='maskthresh',
    #                       iterfield=['in_file'])
    #  workflow.connect(funcreg, 'out_file',
    #                   maskthresh, 'in_file')
    #  workflow.connect(maskthresh, 'out_file',
    #                   outputfiles, 'mask')

    workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    run_workflow()
