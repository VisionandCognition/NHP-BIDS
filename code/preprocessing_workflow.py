#!/usr/bin/env python3

""" The following should be ran before this file:

1. bids_minimal_processing.py
2. resample_isotropic_workflow.py (to-do: should be included in this workflow)

After this, modelfit_workflow.py should be ran (may be renamed).

"""

from builtins import range

import nipype.interfaces.io as nio           # Data i/o
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model specification
from nipype.interfaces.base import Bunch
import os                                    # system functions

import nipype.interfaces.fsl as fsl          # fsl

import transform_manualmask
import motioncorrection_workflow
import undistort_workflow
import nipype.interfaces.utility as niu


preprocess = pe.Workflow(name="preprocess")

ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = ds_root

preprocess.base_dir = os.path.join(ds_root, 'workingdirs')

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
subject_list = ['eddy']
session_list = ['20170511']

infosource = pe.Node(niu.IdentityInterface(fields=[
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

    'manualweights':
    'manual-masks/sub-eddy/ses-20170511/func/'
        'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold'
        '_res-1x1x1_manualweights.nii.gz',

    'manualmask_func_ref':
    'manual-masks/sub-eddy/ses-20170511/func/'
        'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold'
        '_res-1x1x1_reference.nii.gz',

    'funcs':
    'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/func/'
        # 'sub-{subject_id}_ses-{session_id}*_bold_res-1x1x1_preproc'
        'sub-{subject_id}_ses-{session_id}*run-01_bold_res-1x1x1_preproc'
        '.nii.gz',

    'fmap_phasediff':
    'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
        'sub-{subject_id}_ses-{session_id}_phasediff_res-1x1x1_preproc'
        '.nii.gz',

    'fmap_magnitude':
    'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
        'sub-{subject_id}_ses-{session_id}_magnitude1_res-1x1x1_preproc'
        '.nii.gz',

    'fmap_mask':
    'transformed-manual-fmap-mask/sub-{subject_id}/ses-{session_id}/fmap/'
        'sub-{subject_id}_ses-{session_id}_'
        'magnitude1_res-1x1x1_preproc.nii.gz',
}

inputfiles = pe.Node(
    nio.SelectFiles(templates,
                    base_directory=data_dir), name="input_files")

preprocess.connect(
    [(infosource, inputfiles,
     [('subject_id', 'subject_id'),
      ('session_id', 'session_id'),
      ])])

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

# ------------------ Output Files
# Datasink
outputfiles = pe.Node(nio.DataSink(
    base_directory=ds_root,
    container='preprocess',
    parameterization=True),
    name="output_files")

# Use the following DataSink output substitutions
outputfiles.inputs.substitutions = [
    ('subject_id_', 'sub-'),
    ('session_id_', 'ses-'),
    ('/mask/', '/'),
    ('_preproc_flirt_thresh.nii.gz', '_transformedmask.nii.gz'),
    ('_preproc_volreg_unwarped.nii.gz', '_preproc.nii.gz'),
    ('_preproc_flirt_unwarped.nii.gz', '_preproc-mask.nii.gz'),
    ('/_mc_method_afni3dvolreg/', '/'),
    ('/funcs/', '/'),
    ('/funcmasks/', '/'),
    ('preproc_volreg.nii.gz', 'preproc.nii.gz'),
]
# Put result into a BIDS-like format
outputfiles.inputs.regexp_substitutions = [
    (r'_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)', r'sub-\2/ses-\1'),
    (r'/_mc[0-9]*/', r'/func/'),
    (r'/_undistort_masks[0-9]*/', r'/func/'),
    (r'/_undistort[0-9]*/', r'/func/'),
]

# ===================================================================
#                  _____ _            _ _
#                 |  __ (_)          | (_)
#                 | |__) | _ __   ___| |_ _ __   ___
#                 |  ___/ | '_ \ / _ \ | | '_ \ / _ \
#                 | |   | | |_) |  __/ | | | | |  __/
#                 |_|   |_| .__/ \___|_|_|_| |_|\___|
#                         | |
#                         |_|
# ===================================================================

#  ~|~ _ _  _  _ |` _  _ _ _    _ _  _  _|  _
#   | | (_|| |_\~|~(_)| | | |  | | |(_|_\|<_\
#
# Transform manual skull-stripped masks to multiple images
# --------------------------------------------------------
transmanmask = transform_manualmask.create_workflow()

# - - - - - - Connections - - - - - - -
preprocess.connect(
    [(inputfiles, transmanmask,
     [('subject_id', 'in.subject_id'),
      ('session_id', 'in.session_id'),
      ])])

preprocess.connect(inputfiles, 'manualmask',
                   transmanmask, 'in.manualmask')
preprocess.connect(inputfiles, 'funcs',
                   transmanmask, 'in.funcs')
preprocess.connect(inputfiles, 'manualmask_func_ref',
                   transmanmask, 'in.manualmask_func_ref')

#  |\/| _ _|_. _  _    _ _  _ _ _  __|_. _  _
#  |  |(_) | |(_)| |  (_(_)| | (/_(_ | |(_)| |
#
# Perform motion correction, using some pipeline
# --------------------------------------------------------
mc = motioncorrection_workflow.create_workflow_afni()

# - - - - - - Connections - - - - - - -
preprocess.connect(
    [(inputfiles, mc,
     [('subject_id', 'in.subject_id'),
      ('session_id', 'in.session_id'),
      ])])

preprocess.connect(inputfiles, 'funcs',
                   mc, 'in.funcs')
preprocess.connect(inputfiles, 'manualweights',
                   mc, 'in.manualweights')
preprocess.connect(inputfiles, 'manualmask_func_ref',
                   mc, 'in.manualweights_func_ref')
preprocess.connect(mc, 'mc.out_file',
                   outputfiles, 'motioncorrected')
preprocess.connect(mc, 'mc.md1d_file',
                   outputfiles, 'motioncorrected.@md1d_file')
preprocess.connect(mc, 'mc.oned_file',
                   outputfiles, 'motioncorrected.@oned_file')
preprocess.connect(mc, 'mc.oned_matrix_save',
                   outputfiles, 'motioncorrected.@oned_matrix_save')

#  |~. _ | _| _ _  _  _    _ _  _ _ _  __|_. _  _
#  |~|(/_|(_|| | |(_||_)  (_(_)| | (/_(_ | |(_)| |
#                    |
# Unwarp EPI distortions
# --------------------------------------------------------
b0_unwarp = undistort_workflow.create_workflow()

preprocess.connect(
    [(inputfiles, b0_unwarp,
      [('subject_id', 'in.subject_id'),
       ('session_id', 'in.session_id'),
       ('fmap_phasediff', 'in.fmap_phasediff'),
       ('fmap_magnitude', 'in.fmap_magnitude'),
       ('fmap_mask', 'in.fmap_mask'),
       ]),
     (mc, b0_unwarp,
      [('mc.out_file', 'in.funcs'),
       ]),
     (transmanmask, b0_unwarp,
      [('funcreg.out_file', 'in.funcmasks'),
       ]),
     (b0_unwarp, outputfiles,
      [('out.funcs', 'func_unwarp.funcs'),
       ('out.funcmasks', 'func_unwarp.funcmasks'),
       ]),
     ])


#   /\  _  _ |     _ _  _  _|  _
#  /~~\|_)|_)|\/  | | |(_|_\|<_\
#      |  |   /
# Apply brain masks to functionals
# --------------------------------------------------------

epimask = pe.MapNode(
    fsl.BinaryMaths(operation='mul'),
    iterfield=('in_file', 'operand_file'),
    name='epimask'
)

preprocess.connect(
    [(b0_unwarp, epimask,
      [('out.funcs', 'in_file'),
       ('out.funcmasks', 'operand_file'),
       ]),
     (epimask, outputfiles,
      [('out_file', 'brain'),
       ]),
     ])


# ===================================================================
#                       ______ _
#                      |  ____(_)
#                      | |__   _ _ __
#                      |  __| | | '_ \
#                      | |    | | | | |
#                      |_|    |_|_| |_|
#
# ===================================================================

preprocess.stop_on_first_crash = True
preprocess.keep_inputs = True
preprocess.remove_unnecessary_outputs = False
preprocess.write_graph()
preprocess.run()
