#!/usr/bin/env python3

# http://nipype.readthedocs.io/en/latest/users/examples/fmri_fsl.html
# http://miykael.github.io/nipype-beginner-s-guide/firstSteps.html#input-output-stream
import os                                    # system functions

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as niu      # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
from nipype.interfaces.utility import IdentityInterface

from nipype.pipeline.engine import Workflow, Node, MapNode


def run_workflow(session=None, csv_file=None, use_pbs=False):
    inputnode = pe.Node(niu.IdentityInterface(fields=[
        'subject_id',
        'session_id',
    ]), name="input")
    import bids_templates as bt

    from nipype import config
    config.enable_debug_mode()

    method = 'fs'  # freesurfer's mri_convert is faster
    if method == 'fs':
        import nipype.interfaces.freesurfer as fs    # freesurfer
    else:
        assert method == 'fsl'
        import nipype.interfaces.fsl as fsl          # fsl

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = 'derivatives/resampled-isotropic-1mm'
    working_dir = 'workingdirs'

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
    ]), name="infosource")

    if csv_file is not None:
        reader = niu.CSVReader()
        reader.inputs.header = True  
        reader.inputs.in_file = csv_file
        out = reader.run()  

        infosource.iterables = [
            ('session_id', out.outputs.session),
            ('subject_id', out.outputs.subject),
        ]

        infosource.synchronize = True
    else:  # neglected code
        if session is not None:
            session_list = [session]  # ['20170511']
        else:
            session_list = bt.session_list  # ['20170511']

        infosource.iterables = [
            ('session_id', session_list),
            ('subject_id', bt.subject_list),
        ]

    # SelectFiles
    templates = {
        # 'image': 'sub-{subject_id}/ses-{session_id}/{datatype}/'
        'image': 'sub-{subject_id}/ses-{session_id}/*/'
                'sub-{subject_id}_ses-{session_id}_*.nii.gz',
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
        # BIDS Extension Proposal: BEP003
        ('_resample.nii.gz', '_res-1x1x1_preproc.nii.gz'),
        # remove subdirectories:
        ('resampled-isotropic-1mm/isoxfm-1mm', 'resampled-isotropic-1mm'),
        ('resampled-isotropic-1mm/mriconv-1mm', 'resampled-isotropic-1mm'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_datatype_([a-z]*)_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
        r'sub-\3/ses-\2/\1'),
        (r'_fs_iso1mm[0-9]*/', r''),
        (r'/_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'/sub-\2/ses-\1/'),
    ]

    # -------------------------------------------- Create Pipeline
    isotropic_flow = Workflow(
        name='resample_isotropic1mm',
        base_dir=os.path.join(ds_root, working_dir))

    isotropic_flow.connect([
        (infosource, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ])])

    # --- Convert to 1m isotropic voxels

    if method == 'fs':
        fs_iso1mm = MapNode(
            fs.Resample(
                voxel_size=(1.0, 1.0, 1.0),
                # suffix is not accepted by fs.Resample
                # suffix='_res-1x1x1_preproc',  # BIDS Extension Proposal: BEP003
            ),
            name='fs_iso1mm',
            iterfield=['in_file'],
        )

        isotropic_flow.connect(inputfiles, 'image',
                               fs_iso1mm, 'in_file')
        isotropic_flow.connect(fs_iso1mm, 'resampled_file',
                               outputfiles, 'mriconv-1mm')
    elif method == 'fsl':
        # in_file --> out_file
        isoxfm = Node(fsl.FLIRT(
            apply_isoxfm=1.0,
        ),
            name='isoxfm')

        isotropic_flow.connect(inputfiles, 'image',
                               isoxfm, 'in_file')
        isotropic_flow.connect(inputfiles, 'image',
                               isoxfm, 'reference')
        isotropic_flow.connect(isoxfm, 'out_file',
                               outputfiles, 'isoxfm-1mm')

    isotropic_flow.stop_on_first_crash = False  # True
    isotropic_flow.keep_inputs = True
    isotropic_flow.remove_unnecessary_outputs = False
    isotropic_flow.write_graph()
    outgraph = isotropic_flow.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Perform isotropic resampling for NHP fMRI. Run bids_minimal_processing first.')
    parser.add_argument('-s', '--session', type=str,
            help='Session ID, e.g. 20170511.')
    parser.add_argument('--csv', dest='csv_file', default=None,
                        help='CSV file with subjects, sessions, and runs.')
    parser.add_argument('--pbs', dest='use_pbs', action='store_true',
            help='Whether to use pbs plugin.')

    args = parser.parse_args()

    run_workflow(**vars(args))
