#!/usr/bin/env python3

""" 
This script performs preprocessing on fMRI data. It assumes 
that data is in BIDS format and that the data has undergone 
minimal processing and resampling.

After this, you can run:
- bids_modelfit_workflow.py
  >> Fits a GLM and outputs statistics

Questions & comments: c.klink@nin.knaw.nl
"""

import nipype.interfaces.io as nio           # Data i/o
import nipype.pipeline.engine as pe          # pypeline engine

import os                                    # system functions
import argparse
import pandas as pd

import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
from nipype.workflows.fmri.fsl.preprocess import create_susan_smooth
from nipype import LooseVersion

import subcode.bids_transform_manualmask as transform_manualmask
import subcode.bids_motioncorrection_workflow as motioncorrection_workflow
import subcode.bids_undistort_workflow as undistort_workflow

import nipype.interfaces.utility as niu

ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = ds_root


def getmeanscale(medianvals):
    return ['-mul %.10f' % (10000. / val) for val in medianvals]


def create_workflow():
    featpreproc = pe.Workflow(name="featpreproc")

    featpreproc.base_dir = os.path.join(ds_root, 'workingdirs')

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
        'funcs',
        'subject_id',
        'session_id',
        'refsubject_id',
        'fwhm',  # smoothing
        'highpass'
    ]), name="inputspec")

    # SelectFiles
    templates = {
        # FIELDMAP ========
        # fieldmaps are currently not used by this workflow
        # instead, everything is nonlinearly alligned to a reference
        # you should probably 'just' undistort this reference func

        # 'ref_manual_fmapmask':
        # 'manual-masks/sub-{subject_id}/fmap/'
        # 'sub-{subject_id}_ref_fmap_mask_res-1x1x1.nii.gz',

        # 'ref_fmap_magnitude':
        # 'manual-masks/sub-{subject_id}/fmap/'
        # 'sub-{subject_id}_ref_fmap_magnitude1_res-1x1x1.nii.gz',

        # 'ref_fmap_phasediff':
        # 'manual-masks/sub-{subject_id}/fmap/'
        # 'sub-{subject_id}_ref_fmap_phasediff_res-1x1x1.nii.gz',

        # 'fmap_phasediff':
        # 'derivatives/resampled-isotropic-1mm/'
        # 'sub-{subject_id}/ses-{session_id}/fmap/'
        # 'sub-{subject_id}_ses-{session_id}_phasediff_res-1x1x1_preproc.nii.gz',

        # 'fmap_magnitude':
        # 'derivatives/resampled-isotropic-1mm/'
        # 'sub-{subject_id}/ses-{session_id}/fmap/'
        # 'sub-{subject_id}_ses-{session_id}_magnitude1_'
        # 'res-1x1x1_preproc.nii.gz',

        # 'fmap_mask':
        # 'transformed-manual-fmap-mask/sub-{subject_id}/ses-{session_id}/fmap/'
        # 'sub-{subject_id}_ses-{session_id}_'
        # 'magnitude1_res-1x1x1_preproc.nii.gz',


        # FUNCTIONALS ========
        # >> These func references are undistorted with FUGUE <<
        # see the undistort.sh script in:
        # manual-masks/sub-eddy/ses-20170607b/func/
        'ref_func':
        'manual-masks/sub-{refsubject_id}/func/'
        'sub-{subject_id}_ref_func_res-1x1x1.nii.gz',

        'ref_funcmask':
        'manual-masks/sub-{refsubject_id}/func/'
        'sub-{subject_id}_ref_func_mask_res-1x1x1.nii.gz',

        # T1 ========
        # 1 mm iso ---
        # 'ref_t1':
        # 'manual-masks/sub-{subject_id}/anat/'
        # 'sub-{subject_id}_ref_anat_res-1x1x1.nii.gz',

        # 'ref_t1mask':
        # 'manual-masks/sub-{subject_id}/anat/'
        # 'sub-{subject_id}_ref_anat_mask_res-1x1x1.nii.gz',

        # 0.5 mm iso ---
        'ref_t1':
        'manual-masks/sub-{refsubject_id}/anat/'
        'sub-{subject_id}_ref_anat_res-0.5x0.5x0.5.nii.gz',

        'ref_t1mask':
        'manual-masks/sub-{refsubject_id}/anat/'
        'sub-{subject_id}_ref_anat_mask_res-0.5x0.5x0.5.nii.gz',

        # WEIGHTS ========
        # 'manualweights':
        # 'manual-masks/sub-eddy/ses-20170511/func/'
        # 'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold'
        # '_res-1x1x1_manualweights.nii.gz',
    }

    inputfiles = pe.Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir), name="input_files")

    featpreproc.connect(
        [(inputnode, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('refsubject_id', 'refsubject_id'),
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

    # Datasink
    outputfiles = pe.Node(nio.DataSink(
        base_directory=ds_root,
        container='derivatives/featpreproc',
        parameterization=True),
        name="output_files")

    # Use the following DataSink output substitutions
    # each tuple is only matched once per file
    outputfiles.inputs.substitutions = [
        ('/_mc_method_afni3dAllinSlices/', '/'),
        ('/_mc_method_afni3dAllinSlices/', '/'),  # needs to appear twice
        ('/oned_file/', '/'),
        ('/out_file/', '/'),
        ('/oned_matrix_save/', '/'),
        ('refsubject_id_', 'ref-'),
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1'),
        (r'/_addmean[0-9]+/', r'/func/'),
        (r'/_funcbrains[0-9]+/', r'/func/'),
        (r'/_maskfunc[0-9]+/', r'/func/'),
        (r'/_mc[0-9]+/', r'/func/'),
        (r'/_meanfunc[0-9]+/', r'/func/'),
        (r'/_outliers[0-9]+/', r'/func/'),
        (r'_ref-([a-zA-Z0-9]+)_run_id_[0-9][0-9]', r''),
    ]
    outputnode = pe.Node(interface=util.IdentityInterface(
        fields=['motion_parameters',
                'motion_corrected',
                'motion_plots',
                'motion_outlier_files',
                'mask',
                'smoothed_files',
                'highpassed_files',
                'mean',
                'func_unwarp',
                'ref_func',
                'ref_funcmask',
                'ref_t1',
                'ref_t1mask',
                ]),
        name='outputspec')

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
    # should just be used as input to motion correction,
    # after mc, all functionals should be aligned to reference
    transmanmask_mc = transform_manualmask.create_workflow()

    # - - - - - - Connections - - - - - - -
    featpreproc.connect(
        [(inputfiles, transmanmask_mc,
         [('subject_id', 'in.subject_id'),
          ('session_id', 'in.session_id'),
          ('refsubject_id', 'in.refsubject_id'),
          ])])

    #featpreproc.connect(inputfiles, 'ref_funcmask',
    #                    transmanmask_mc, 'in.manualmask')
    featpreproc.connect(inputfiles, 'ref_funcmask',
                        transmanmask_mc, 'in.ref_funcmask')
    featpreproc.connect(inputnode, 'funcs',
                        transmanmask_mc, 'in.funcs')

    featpreproc.connect(inputfiles, 'ref_func',
                        transmanmask_mc, 'in.ref_func')

    # fieldmaps not being used
    if False:
        trans_fmapmask = transmanmask_mc.clone('trans_fmapmask')
        featpreproc.connect(inputfiles, 'ref_manual_fmapmask',
                            trans_fmapmask, 'in.manualmask')
        featpreproc.connect(inputfiles, 'fmap_magnitude',
                            trans_fmapmask, 'in.funcs')
        featpreproc.connect(inputfiles, 'ref_func',
                            trans_fmapmask, 'in.manualmask_func_ref')

    #  |\/| _ _|_. _  _    _ _  _ _ _  __|_. _  _
    #  |  |(_) | |(_)| |  (_(_)| | (/_(_ | |(_)| |
    #
    # Perform motion correction, using some pipeline
    # --------------------------------------------------------
    # mc = motioncorrection_workflow.create_workflow_afni()

    # Register an image from the functionals to the reference image
    median_func = pe.MapNode(
        interface=fsl.maths.MedianImage(dimension="T"),
        name='median_func',
        iterfield=('in_file'),
    )
    pre_mc = motioncorrection_workflow.create_workflow_allin_slices(
        name='premotioncorrection')

    featpreproc.connect(
        [
         (inputnode, median_func,
          [
           ('funcs', 'in_file'),
           ]),
         (median_func, pre_mc,
          [
           ('out_file', 'in.funcs'),
           ]),
         (inputfiles, pre_mc,
          [
           # median func image will be used a reference / base
           ('ref_func', 'in.ref_func'),
           ('ref_funcmask', 'in.ref_func_weights'),
          ]),
         (transmanmask_mc, pre_mc,
          [
           ('funcreg.out_file', 'in.funcs_masks'),  # use mask as weights >>>> are we sure this is correct?
          ]),
         (pre_mc, outputnode,
          [
           ('mc.out_file', 'pre_motion_corrected'),
           ('mc.oned_file', 'pre_motion_parameters.oned_file'),
           ('mc.oned_matrix_save', 'pre_motion_parameters.oned_matrix_save'),
          ]),
         (outputnode, outputfiles,
          [
           ('pre_motion_corrected', 'pre_motion_corrected.out_file'),
           ('pre_motion_parameters.oned_file',
            'pre_motion_corrected.oned_file'),
           # warp parameters in ASCII (.1D)
           ('pre_motion_parameters.oned_matrix_save',
            'pre_motion_corrected.oned_matrix_save'),
           # transformation matrices for each sub-brick
          ]),
        ])

    mc = motioncorrection_workflow.create_workflow_allin_slices(
        name='motioncorrection',
        iterfield=('in_file', 'ref_file', 'in_weight_file'))
    # - - - - - - Connections - - - - - - -
    featpreproc.connect(
        [(inputnode, mc,
          [
           ('funcs', 'in.funcs'),
           ]),
         (pre_mc, mc, [
             # the median image realigned to the reference functional
             # will serve as reference. This way motion correction is
             #  done to an image more similar to the functionals
             ('mc.out_file', 'in.ref_func'),
           ]),
         (inputfiles, mc, [
             # Check and make sure the ref func mask is close enough
             # to the registered median image.
             ('ref_funcmask', 'in.ref_func_weights'),
           ]),
         (transmanmask_mc, mc, [
             ('funcreg.out_file', 'in.funcs_masks'),  # use mask as weights
         ]),
         (mc, outputnode, [
             ('mc.out_file', 'motion_corrected'),
             ('mc.oned_file', 'motion_parameters.oned_file'),
             ('mc.oned_matrix_save', 'motion_parameters.oned_matrix_save'),
         ]),
         (outputnode, outputfiles, [
             ('motion_corrected', 'motion_corrected.out_file'),
             ('motion_parameters.oned_file', 'motion_corrected.oned_file'),
             # warp parameters in ASCII (.1D)
             ('motion_parameters.oned_matrix_save',
              'motion_corrected.oned_matrix_save'),
             # transformation matrices for each sub-brick
         ]),
         ])

    #  |~. _ | _| _ _  _  _    _ _  _ _ _  __|_. _  _
    #  |~|(/_|(_|| | |(_||_)  (_(_)| | (/_(_ | |(_)| |
    #                    |
    # Unwarp EPI distortions
    # --------------------------------------------------------

    # Performing motion correction to a reference that is undistorted,
    # So b0_unwarp is currently not needed or used.
    if False:
        b0_unwarp = undistort_workflow.create_workflow()

        featpreproc.connect(
            [(inputfiles, b0_unwarp,
              [  # ('subject_id', 'in.subject_id'),
               # ('session_id', 'in.session_id'),
               ('fmap_phasediff', 'in.fmap_phasediff'),
               ('fmap_magnitude', 'in.fmap_magnitude'),
               ]),
             (mc, b0_unwarp,
              [('mc.out_file', 'in.funcs'),
               ]),
             (transmanmask_mc, b0_unwarp,
              [('funcreg.out_file', 'in.funcmasks'),
               ]),
             (trans_fmapmask, b0_unwarp,
              [('funcreg.out_file', 'in.fmap_mask')]),
             (b0_unwarp, outputfiles,
              [('out.funcs', 'func_unwarp.funcs'),
               ('out.funcmasks', 'func_unwarp.funcmasks'),
               ]),
             (b0_unwarp, outputnode,
              [('out.funcs', 'func_unwarp.funcs'),
               ('out.funcmasks', 'mask'),
               ]),
             ])

    # undistort the reference images
    if False:
        b0_unwarp_ref = b0_unwarp.clone('b0_unwarp_ref')
        featpreproc.connect(
            [(inputfiles, b0_unwarp_ref,
              [  # ('subject_id', 'in.subject_id'),
               # ('session_id', 'in.session_id'),
               ('ref_fmap_phasediff', 'in.fmap_phasediff'),
               ('ref_fmap_magnitude', 'in.fmap_magnitude'),
               ('ref_manual_fmapmask', 'in.fmap_mask'),
               ('ref_func', 'in.funcs'),
               ('ref_funcmask', 'in.funcmasks'),
               ]),
             (b0_unwarp_ref, outputfiles,
              [('out.funcs', 'func_unwarp_ref.func'),
               ('out.funcmasks', 'func_unwarp_ref.funcmask'),
               ]),
             (b0_unwarp_ref, outputnode,
              [('out.funcs', 'ref_func'),
               ('out.funcmasks', 'ref_mask'),
               ]),
             ])
    else:
        featpreproc.connect(
            [(inputfiles, outputfiles,
              [('ref_func', 'reference/func'),
               ('ref_funcmask', 'reference/func_mask'),
               ]),
             (inputfiles, outputnode,
              [('ref_func', 'ref_func'),
               ('ref_funcmask', 'ref_funcmask'),
               ]),
             ])

    #  |\/| _ _|_. _  _    _   _|_|. _  _ _
    #  |  |(_) | |(_)| |  (_)|_|| ||(/_| _\
    #
    # --------------------------------------------------------

    # Apply brain masks to functionals
    # --------------------------------------------------------

    # Dilate mask
    dilatemask = pe.Node(
            interface=fsl.ImageMaths(suffix='_dil', op_string='-dilF'),
            name='dilatemask')
    featpreproc.connect(inputfiles, 'ref_funcmask', dilatemask, 'in_file')
    featpreproc.connect(dilatemask, 'out_file', outputfiles, 'dilate_mask')

    funcbrains = pe.MapNode(
        fsl.BinaryMaths(operation='mul'),
        iterfield=('in_file', 'operand_file'),
        name='funcbrains'
    )

    featpreproc.connect(
        [(mc, funcbrains,
          [('mc.out_file', 'in_file'),
           ]),
         (dilatemask, funcbrains,
          [('out_file', 'operand_file'),
           ]),
         (funcbrains, outputfiles,
          [('out_file', 'funcbrains'),
           ]),
         ])
    # Detect motion outliers
    # --------------------------------------------------------

    import nipype.algorithms.rapidart as ra
    outliers = pe.MapNode(
        ra.ArtifactDetect(
            mask_type='file',
            # trying to "disable" `norm_threshold`:
            use_norm=True,
            norm_threshold=10.0,  # combines translations in mm and rotations
            # use_norm=Undefined,
            # translation_threshold=1.0,  # translation in mm
            # rotation_threshold=0.02,  # rotation in radians
            zintensity_threshold=3.0,  # z-score
            parameter_source='AFNI',
            save_plot=True),
        iterfield=('realigned_files', 'realignment_parameters', 'mask_file'),
        name='outliers')

    featpreproc.connect([
        (mc, outliers,
         [  # ('mc.par_file', 'realignment_parameters'),
             ('mc.oned_file', 'realignment_parameters'),
         ]),
        (funcbrains, outliers,
         [('out_file', 'realigned_files'),
          ]),
        (dilatemask, outliers,
         [('out_file', 'mask_file'),
          ]),
        (outliers, outputfiles,
         [('outlier_files', 'motion_outliers.@outlier_files'),
          ('plot_files', 'motion_outliers.@plot_files'),
          ('displacement_files', 'motion_outliers.@displacement_files'),
          ('intensity_files', 'motion_outliers.@intensity_files'),
          ('mask_files', 'motion_outliers.@mask_files'),
          ('statistic_files', 'motion_outliers.@statistic_files'),
          # ('norm_files', 'outliers.@norm_files'),
          ]),
        (mc, outputnode,
         [('mc.oned_file', 'motion_parameters'),
          ]),
        (outliers, outputnode,
         [('outlier_files', 'motion_outlier_files'),
          ('plot_files', 'motion_plots.@plot_files'),
          ('displacement_files', 'motion_outliers.@displacement_files'),
          ('intensity_files', 'motion_outliers.@intensity_files'),
          ('mask_files', 'motion_outliers.@mask_files'),
          ('statistic_files', 'motion_outliers.@statistic_files'),
          # ('norm_files', 'outliers.@norm_files'),
          ])
    ])

    """
    Determine the 2nd and 98th percentile intensities of each functional run
    """
    getthresh = pe.MapNode(interface=fsl.ImageStats(op_string='-p 2 -p 98'),
                           iterfield=['in_file'],
                           name='getthreshold')
    if False:
        featpreproc.connect(b0_unwarp, 'out.funcs', getthresh, 'in_file')
    else:
        featpreproc.connect(mc, 'mc.out_file', getthresh, 'in_file')

    """
    Threshold the first run of functional data at 10% of the 98th percentile
    """

    threshold = pe.MapNode(interface=fsl.ImageMaths(out_data_type='char',
                                                    suffix='_thresh'),
                           iterfield=['in_file', 'op_string'],
                           name='threshold')
    if False:
        featpreproc.connect(b0_unwarp, 'out.funcs', threshold, 'in_file')
    else:
        featpreproc.connect(mc, 'mc.out_file', threshold, 'in_file')

    """
    Define a function to get 10% of the intensity
    """
    def getthreshop(thresh):
        return ['-thr %.10f -Tmin -bin' % (0.1 * val[1]) for val in thresh]

    featpreproc.connect(
        getthresh, ('out_stat', getthreshop),
        threshold, 'op_string')

    """
    Determine the median value of the functional runs using the mask
    """
    medianval = pe.MapNode(interface=fsl.ImageStats(op_string='-k %s -p 50'),
                           iterfield=['in_file', 'mask_file'],
                           name='medianval')
    if False:
        featpreproc.connect(b0_unwarp, 'out.funcs', medianval, 'in_file')
    else:
        featpreproc.connect(mc, 'mc.out_file', medianval, 'in_file')

    featpreproc.connect(threshold, 'out_file', medianval, 'mask_file')

    # (~ _  _ _|_. _ |  (~ _ _  _  _ _|_|_ . _  _
    # _)|_)(_| | |(_||  _)| | |(_)(_) | | ||| |(_|
    #   |                                       _|
    # Spatial smoothing (SUSAN)
    # --------------------------------------------------------

    # create_susan_smooth takes care of calculating the mean and median
    #   functional, applying mask to functional, and running the smoothing
    smooth = create_susan_smooth(separate_masks=False)
    featpreproc.connect(inputnode, 'fwhm', smooth, 'inputnode.fwhm')

    featpreproc.connect(mc, 'mc.out_file',
                            smooth, 'inputnode.in_files')

    featpreproc.connect(dilatemask, 'out_file',
                        smooth, 'inputnode.mask_file')

    # -------------------------------------------------------
    # The below is from workflows/fmri/fsl/preprocess.py

    """
    Mask the smoothed data with the dilated mask
    """

    maskfunc3 = pe.MapNode(interface=fsl.ImageMaths(suffix='_mask',
                                                    op_string='-mas'),
                           iterfield=['in_file', 'in_file2'],
                           name='maskfunc3')
    featpreproc.connect(
        smooth, 'outputnode.smoothed_files', maskfunc3, 'in_file')

    featpreproc.connect(dilatemask, 'out_file', maskfunc3, 'in_file2')

    concatnode = pe.Node(interface=util.Merge(2),
                         name='concat')

    tolist = lambda x: [x]

    def chooseindex(fwhm):
        if fwhm < 1:
            return [0]
        else:
            return [1]

    # maskfunc2 is the functional data before SUSAN
    if False:
        featpreproc.connect(b0_unwarp, ('out.funcs', tolist),
                            concatnode, 'in1')
    else:
        featpreproc.connect(mc, ('mc.out_file', tolist), concatnode, 'in1')
    # maskfunc3 is the functional data after SUSAN
    featpreproc.connect(maskfunc3, ('out_file', tolist), concatnode, 'in2')

    """
    The following nodes select smooth or unsmoothed data depending on the
    fwhm. This is because SUSAN defaults to smoothing the data with about the
    voxel size of the input data if the fwhm parameter is less than 1/3 of the
    voxel size.
    """
    selectnode = pe.Node(interface=util.Select(), name='select')

    featpreproc.connect(concatnode, 'out', selectnode, 'inlist')

    featpreproc.connect(inputnode, ('fwhm', chooseindex), selectnode, 'index')
    featpreproc.connect(selectnode, 'out', outputfiles, 'smoothed_files')

    """
    Scale the median value of the run is set to 10000.
    """

    meanscale = pe.MapNode(interface=fsl.ImageMaths(suffix='_gms'),
                           iterfield=['in_file', 'op_string'],
                           name='meanscale')
    featpreproc.connect(selectnode, 'out', meanscale, 'in_file')

    """
    Define a function to get the scaling factor for intensity normalization
    """

    featpreproc.connect(
        medianval, ('out_stat', getmeanscale),
        meanscale, 'op_string')

    # |_|. _ |_  _  _  _ _
    # | ||(_|| ||_)(_|_\_\
    #      _|   |
    # Temporal filtering
    # --------------------------------------------------------

    highpass = pe.MapNode(interface=fsl.ImageMaths(suffix='_tempfilt'),
                          iterfield=['in_file'],
                          name='highpass')
    highpass_operand = lambda x: '-bptf %.10f -1' % x
    featpreproc.connect(
        inputnode, ('highpass', highpass_operand),
        highpass, 'op_string')
    featpreproc.connect(meanscale, 'out_file', highpass, 'in_file')

    version = 0
    if fsl.Info.version() and \
            LooseVersion(fsl.Info.version()) > LooseVersion('5.0.6'):
        version = 507

    if version < 507:
        featpreproc.connect(
            highpass, 'out_file', outputnode, 'highpassed_files')
    else:
        """
        Add back the mean removed by the highpass filter operation as
            of FSL 5.0.7
        """
        meanfunc4 = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',
                                                        suffix='_mean'),
                               iterfield=['in_file'],
                               name='meanfunc4')

        featpreproc.connect(meanscale, 'out_file', meanfunc4, 'in_file')
        addmean = pe.MapNode(interface=fsl.BinaryMaths(operation='add'),
                             iterfield=['in_file', 'operand_file'],
                             name='addmean')
        featpreproc.connect(highpass, 'out_file', addmean, 'in_file')
        featpreproc.connect(meanfunc4, 'out_file', addmean, 'operand_file')
        featpreproc.connect(
            addmean, 'out_file', outputnode, 'highpassed_files')

    """
    Generate a mean functional image from the first run
    """
    meanfunc3 = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',
                                                    suffix='_mean'),
                           iterfield=['in_file'],
                           name='meanfunc3')

    featpreproc.connect(meanscale, 'out_file', meanfunc3, 'in_file')
    featpreproc.connect(meanfunc3, 'out_file', outputfiles, 'mean')

    featpreproc.connect(meanfunc3, 'out_file', outputnode, 'mean_highpassed')
    featpreproc.connect(outputnode, 'highpassed_files',
                        outputfiles, 'highpassed_files')

    return(featpreproc)


# ===================================================================
#                       ______ _
#                      |  ____(_)
#                      | |__   _ _ __
#                      |  __| | | '_ \
#                      | |    | | | | |
#                      |_|    |_|_| |_|
#
# ===================================================================


def run_workflow(csv_file, fwhm, HighPass):
    # Using the name "level1flow" should allow the workingdirs file to be used
    # by the fmri_workflow pipeline.
    workflow = pe.Workflow(name='level1flow')
    workflow.base_dir = os.path.abspath('./workingdirs')

    featpreproc = create_workflow()

    inputnode = pe.Node(niu.IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'run_id',
        'refsubject_id',
    ]), name="input")
    
    if csv_file is not None:
      print('=== reading csv ===')
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
      print(sub_img)
      print(ref_img)
    else:
      print("No csv-file specified. Don't know what data to process.")

    templates = {
        'funcs':
        'derivatives/resampled-isotropic-1mm/'
        'sub-{subject_id}/ses-{session_id}/func/'
        'sub-{subject_id}_ses-{session_id}*run-{run_id}_bold_res-1x1x1_preproc.nii.gz',
    }
    inputfiles = pe.Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir), name="input_files")

    workflow.connect([
        (inputnode, inputfiles,
         [('subject_id', 'subject_id'),
          ('refsubject_id', 'refsubject_id'),
          ('session_id', 'session_id'),
          ('run_id', 'run_id'),
          ]),
        (inputnode, featpreproc,
         [('subject_id', 'inputspec.subject_id'),
          ('refsubject_id', 'inputspec.refsubject_id'),
          ('session_id', 'inputspec.session_id'),
          ]),
        (inputfiles, featpreproc,
         [('funcs', 'inputspec.funcs'),
          ])
    ])

    featpreproc.inputs.inputspec.fwhm = fwhm     # spatial smoothing (default=2)
    featpreproc.inputs.inputspec.highpass = HighPass  # FWHM in seconds (default=50)
    
    workflow.workflow_level = 'INFO'    # INFO/DEBUG
    # workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Perform pre-processing step for NHP fMRI.')
    parser.add_argument('--csv',
                        dest='csv_file', default=None,
                        help='CSV file with subjects, sessions, and runs.')
    parser.add_argument('--fwhm',
                        dest='fwhm', default=2.0,
                        help='Set FWHM for smoothing in mm. (default is 2.0 mm)')
    parser.add_argument('--HighPass',
                        dest='HighPass', default=50,
                        help='Set high pass filter in seconds. (default = 50 s)')

    args = parser.parse_args()

    run_workflow(**vars(args))
