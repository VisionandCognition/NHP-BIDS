#!/usr/bin/env python3

# http://nipype.readthedocs.io/en/latest/users/examples/fmri_fsl.html
# http://miykael.github.io/nipype-beginner-s-guide/firstSteps.html#input-output-stream
import os                                    # system functions

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
from nipype.interfaces.utility import IdentityInterface

from nipype.pipeline.engine import Workflow, Node, MapNode

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
output_dir = 'resampled-isotropic-1mm'
working_dir = 'workingdirs/resample-isotropic-1mm'

subject_list = ['eddy']
session_list = ['20170511']

# ------------------ Input Files
# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=[
    'subject_id',
    'session_id',
    'datatype',
]), name="infosource")

infosource.iterables = [
    ('session_id', session_list),
    ('subject_id', subject_list),
    ('datatype', ['anat', 'fmap', 'func']),
]
# SelectFiles
templates = {
    'image': 'sub-{subject_id}/ses-{session_id}/{datatype}/'
             'sub-{subject_id}_ses-{session_id}_*.nii.gz',
}
inputfiles = Node(nio.SelectFiles(templates,
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
]

# -------------------------------------------- Create Pipeline
isotropic_flow = Workflow(
    name='resample_isotropic1mm',
    base_dir=os.path.join(ds_root, working_dir))

isotropic_flow.connect([(infosource, inputfiles,
                       [('subject_id', 'subject_id'),
                        ('session_id', 'session_id'),
                        ('datatype', 'datatype')])])

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


if __name__ == '__main__':
    isotropic_flow.stop_on_first_crash = True
    isotropic_flow.keep_inputs = True
    isotropic_flow.remove_unnecessary_outputs = False
    isotropic_flow.write_graph()
    outgraph = isotropic_flow.run()
