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
    output_dir = 'transformed-manual-fmap-mask'
    working_dir = 'workingdirs/transform_manual_fmap_mask'

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
        'manual-masks/sub-eddy/ses-20170511/fmap/'
            'sub-eddy_ses-20170511_magnitude1_res-1x1x1_manualmask.nii.gz',

        'ref_fmap_magnitude':
        'resampled-isotropic-1mm/sub-eddy/ses-20170511/fmap/'
            'sub-eddy_ses-20170511_magnitude1_res-1x1x1_preproc.nii.gz',

        # 'fmap_magnitude':
        # 'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
        #     'sub-{subject_id}_ses-{session_id}_magnitude1_res-1x1x1_preproc'
        #     '.nii.gz',
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
        ('/_identreg0/', '/fmap/'),
        ('_magnitude1_res-1x1x1_manualmask_flirt',
         '_magnitude1_res-1x1x1_preproc'),
        # BIDS Extension Proposal: BEP003
        # ('_resample.nii.gz', '_res-1x1x1_preproc.nii.gz'),
        # remove subdirectories:
        # ('resampled-isotropic-1mm/isoxfm-1mm', 'resampled-isotropic-1mm'),
        # ('resampled-isotropic-1mm/mriconv-1mm', 'resampled-isotropic-1mm'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)', r'sub-\2/ses-\1'),
        #(r'_fs_iso1mm[0-9]*/', r''),
    ]

    # -------------------------------------------- Create Pipeline
    workflow = Workflow(
        name='transform_manual_fmap_mask',
        base_dir=os.path.join(ds_root, working_dir))

    workflow.connect([(infosource, inputfiles,
                      [('subject_id', 'subject_id'),
                       ('session_id', 'session_id'),
                       ])])

    # --- Copy reference images, for consistency with images that do need
    #       to be transformed

    # First calculate transform with magnitude images and then transform the
    #   mask
    # workflow.connect(inputfiles, 'manualmask',
    #                  reg, 'in_file')
    # workflow.connect(inputfiles, 'ref_fmap_magnitude',
    #                  reg, 'reference')
    # workflow.connect(inputfiles, 'fmap_magnitude',
    #                  reg, 'reference')

    # --- "Dummy" part of pipeline, for consistency
    identreg = MapNode(fsl.FLIRT(),
                       iterfield=['in_file'],
                       name='identreg'
                       )
    workflow.connect(inputfiles, 'manualmask',
                     identreg, 'in_file')
    workflow.connect(inputfiles, 'ref_fmap_magnitude',
                     identreg, 'reference')
    workflow.connect(identreg, 'out_file',
                     outputfiles, 'mask')

    workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    run_workflow()
