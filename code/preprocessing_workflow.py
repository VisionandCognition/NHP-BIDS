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
import nipype.interfaces.utility as util     # utility
from nipype.workflows.fmri.fsl.preprocess import create_susan_smooth
from nipype import LooseVersion

import transform_manualmask
import motioncorrection_workflow
import undistort_workflow
import nipype.interfaces.utility as niu


def getmeanscale(medianvals):
    return ['-mul %.10f' % (10000. / val) for val in medianvals]


def create_workflow():
    featpreproc = pe.Workflow(name="featpreproc")

    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    data_dir = ds_root

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
    subject_list = ['eddy']
    session_list = ['20170511']

    inputnode = pe.Node(niu.IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'fwhm',  # smoothing
        'highpass'
    ]), name="inputspec")

    inputnode.iterables = [
        ('session_id', session_list),
        ('subject_id', subject_list),
    ]
    # SelectFiles
    templates = {
        'manualmask':
        'manual-masks/sub-eddy/ses-20170511/func/'
            'sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold'
            '_res-1x1x1_manualmask.nii.gz',

        'manual_fmapmask':
        'manual-masks/sub-eddy/ses-20170511/fmap/'
            'sub-eddy_ses-20170511_magnitude1_res-1x1x1_manualmask.nii.gz',

        'manual_fmapmask_ref':
        'manual-masks/sub-eddy/ses-20170511/fmap/'
            'sub-eddy_ses-20170511_magnitude1_res-1x1x1_reference.nii.gz',

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
            # '.nii.gz',
            '_nvol10.nii.gz',

        'fmap_phasediff':
        'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
            'sub-{subject_id}_ses-{session_id}_phasediff_res-1x1x1_preproc'
            '.nii.gz',

        'fmap_magnitude':
        'resampled-isotropic-1mm/sub-{subject_id}/ses-{session_id}/fmap/'
            'sub-{subject_id}_ses-{session_id}_magnitude1_res-1x1x1_preproc'
            '.nii.gz',

        # 'fmap_mask':
        # 'transformed-manual-fmap-mask/sub-{subject_id}/ses-{session_id}/fmap/'
        #     'sub-{subject_id}_ses-{session_id}_'
        #     'magnitude1_res-1x1x1_preproc.nii.gz',
    }

    inputfiles = pe.Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir), name="input_files")

    featpreproc.connect(
        [(inputnode, inputfiles,
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
        container='featpreproc',
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
        ('/_mc_method_afni3dAllinSlices/', '/'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1'),

        (r'/_addmean[0-9]+/', r'/func/'),
        (r'/_dilatemask[0-9]+/', r'/func/'),
        (r'/_funcbrain[0-9]+/', r'/func/'),
        (r'/_maskfunc[0-9]+/', r'/func/'),
        (r'/_mc[0-9]+/', r'/func/'),
        (r'/_meanfunc[0-9]+/', r'/func/'),
        (r'/_outliers[0-9]+/', r'/func/'),
        (r'/_undistort_masks[0-9]+/', r'/func/'),
        (r'/_undistort[0-9]+/', r'/func/'),
    ]
    outputnode = pe.Node(interface=util.IdentityInterface(
        fields=['motion_parameters',
                'motion_corrected',
                'motion_plots',
                'motion_outliers',
                'mask',
                'smoothed_files',
                'highpassed_files',
                'mean',
                'func_unwarp']),
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
    transmanmask = transform_manualmask.create_workflow()

    # - - - - - - Connections - - - - - - -
    featpreproc.connect(
        [(inputfiles, transmanmask,
         [('subject_id', 'in.subject_id'),
          ('session_id', 'in.session_id'),
          ])])

    featpreproc.connect(inputfiles, 'manualmask',
                        transmanmask, 'in.manualmask')
    featpreproc.connect(inputfiles, 'funcs',
                        transmanmask, 'in.funcs')
    featpreproc.connect(inputfiles, 'manualmask_func_ref',
                        transmanmask, 'in.manualmask_func_ref')

    trans_fmapmask = transmanmask.clone('trans_fmapmask')
    featpreproc.connect(inputfiles, 'manual_fmapmask',
                        trans_fmapmask, 'in.manualmask')
    featpreproc.connect(inputfiles, 'fmap_magnitude',
                        trans_fmapmask, 'in.funcs')
    featpreproc.connect(inputfiles, 'manualmask_func_ref',
                        trans_fmapmask, 'in.manualmask_func_ref')

    #  |\/| _ _|_. _  _    _ _  _ _ _  __|_. _  _
    #  |  |(_) | |(_)| |  (_(_)| | (/_(_ | |(_)| |
    #
    # Perform motion correction, using some pipeline
    # --------------------------------------------------------
    # mc = motioncorrection_workflow.create_workflow_afni()
    mc = motioncorrection_workflow.create_workflow_allin_slices()

    # - - - - - - Connections - - - - - - -
#    featpreproc.connect(
#        [(inputfiles, mc,
#         [('subject_id', 'in.subject_id'),
#          ('session_id', 'in.session_id'),
#          ])])

    featpreproc.connect(
        [(inputfiles, mc, [
            ('funcs', 'in.funcs'),
            # median func image will be used a reference / base
            # ('manualmask_func_ref', 'in.manualweights_func_ref'),
         ]),
         (transmanmask, mc, [
             ('funcreg.out_file', 'in.transweights'),  # use mask as weights
         ]),
         (mc, outputfiles, [
             ('mc.out_file', 'motioncorrected'),
             #  ('mc.md1d_file', 'motioncorrected@md1d_file'),
             ('mc.oned_file', 'motioncorrected.@oned_file'),
             ('mc.oned_matrix_save', 'motioncorrected.@oned_matrix_save'),
         ]),
         (mc, outputnode, [
             ('mc.out_file', 'motion_corrected'),
             #  ('mc.md1d_file', 'motioncorrected@md1d_file'),
             ('mc.oned_file', 'motion_parameters.@oned_file'),
             ('mc.oned_matrix_save', 'motion_parameters.@oned_matrix_save'),
         ])
    ])

    #  |~. _ | _| _ _  _  _    _ _  _ _ _  __|_. _  _
    #  |~|(/_|(_|| | |(_||_)  (_(_)| | (/_(_ | |(_)| |
    #                    |
    # Unwarp EPI distortions
    # --------------------------------------------------------
    b0_unwarp = undistort_workflow.create_workflow()

    featpreproc.connect(
        [(inputfiles, b0_unwarp,
          [('subject_id', 'in.subject_id'),
           ('session_id', 'in.session_id'),
           ('fmap_phasediff', 'in.fmap_phasediff'),
           ('fmap_magnitude', 'in.fmap_magnitude'),
           ]),
         (mc, b0_unwarp,
          [('mc.out_file', 'in.funcs'),
           ]),
         (transmanmask, b0_unwarp,
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

    #   /\  _  _ |     _ _  _  _|  _
    #  /~~\|_)|_)|\/  | | |(_|_\|<_\
    #      |  |   /
    # Apply brain masks to functionals
    # --------------------------------------------------------

    funcbrain = pe.MapNode(
        fsl.BinaryMaths(operation='mul'),
        iterfield=('in_file', 'operand_file'),
        name='funcbrain'
    )

    featpreproc.connect(
        [(b0_unwarp, funcbrain,
          [('out.funcs', 'in_file'),
           ('out.funcmasks', 'operand_file'),
           ]),
         (funcbrain, outputfiles,
          [('out_file', 'brain'),
           ]),
         ])

    #  |\/| _ _|_. _  _    _   _|_|. _  _ _
    #  |  |(_) | |(_)| |  (_)|_|| ||(/_| _\
    #
    # Detect motion outliers
    # --------------------------------------------------------
    import nipype.algorithms.rapidart as ra
    outliers = pe.MapNode(
        ra.ArtifactDetect(
            mask_type='file',
            norm_threshold=1.0,  # combines translations in mm and rotations
            # translation_threshold=1.0,  # translation in mm
            # rotation_threshold=0.02,  # rotation in radians
            zintensity_threshold=3.0,  # z-score
            use_norm=True,
            parameter_source='AFNI',
            save_plot=True),
        iterfield=('realigned_files', 'realignment_parameters', 'mask_file'),
        name='outliers')

    featpreproc.connect([
        (mc, outliers,
         [  # ('mc.par_file', 'realignment_parameters'),
             ('mc.oned_file', 'realignment_parameters'),
         ]),
        (funcbrain, outliers,
         [('out_file', 'realigned_files'),
          ]),
        (b0_unwarp, outliers,
         [('out.funcmasks', 'mask_file'),
          ]),
        (outliers, outputfiles,
         [('outlier_files', 'outliers.@outlier_files'),
          ('plot_files', 'outliers.@plot_files'),
          ('displacement_files', 'outliers.@displacement_files'),
          ('intensity_files', 'outliers.@intensity_files'),
          ('mask_files', 'outliers.@mask_files'),
          ('statistic_files', 'outliers.@statistic_files'),
          # ('norm_files', 'outliers.@norm_files'),
          ]),
        (outliers, outputnode,
         [('outlier_files', 'motion_outliers.@outlier_files'),
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
    featpreproc.connect(b0_unwarp, 'out.funcs', getthresh, 'in_file')
    """
    Threshold the first run of functional data at 10% of the 98th percentile
    """

    threshold = pe.MapNode(interface=fsl.ImageMaths(out_data_type='char',
                                                    suffix='_thresh'),
                           iterfield=['in_file', 'op_string'],
                           name='threshold')
    featpreproc.connect(b0_unwarp, 'out.funcs', threshold, 'in_file')

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
    featpreproc.connect(b0_unwarp, 'out.funcs', medianval, 'in_file')
    featpreproc.connect(threshold, 'out_file', medianval, 'mask_file')

    """
    Dilate the mask
    """
    dilatemask = pe.MapNode(interface=fsl.ImageMaths(suffix='_dil',
                                                     op_string='-dilF'),
                            iterfield=['in_file'],
                            name='dilatemask')
    featpreproc.connect(b0_unwarp, 'out.funcmasks', dilatemask, 'in_file')
    featpreproc.connect(dilatemask, 'out_file', outputfiles, 'dialate_mask')

    # (~ _  _ _|_. _ |  (~ _ _  _  _ _|_|_ . _  _
    # _)|_)(_| | |(_||  _)| | |(_)(_) | | ||| |(_|
    #   |                                       _|
    # Spatial smoothing (SUSAN)
    # --------------------------------------------------------

    # create_susan_smooth takes care of calculating the mean and median
    #   functional, applying mask to functional, and running the smoothing
    smooth = create_susan_smooth()
    featpreproc.connect(inputnode, 'fwhm', smooth, 'inputnode.fwhm')

    featpreproc.connect(b0_unwarp, 'out.funcs', smooth, 'inputnode.in_files')
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
    featpreproc.connect(b0_unwarp, ('out.funcs', tolist), concatnode, 'in1')
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
    Scale the median value of the run is set to 10000
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
            highpass, 'out_file', outputfiles, 'highpassed_files')
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
            addmean, 'out_file', outputfiles, 'highpassed_files')

    """
    Generate a mean functional image from the first run
    """
    meanfunc3 = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',
                                                    suffix='_mean'),
                           iterfield=['in_file'],
                           name='meanfunc3')

    featpreproc.connect(meanscale, 'out_file', meanfunc3, 'in_file')
    featpreproc.connect(meanfunc3, 'out_file', outputfiles, 'mean')

    featpreproc.connect(meanfunc3, 'out_file', outputnode, 'highpassed_files')

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

def run_workflow():
    featpreproc = create_workflow()

    featpreproc.inputs.inputspec.fwhm = 2.0
    featpreproc.inputs.inputspec.highpass = 50

    featpreproc.stop_on_first_crash = True
    featpreproc.keep_inputs = True
    featpreproc.remove_unnecessary_outputs = False
    featpreproc.write_graph()
    featpreproc.run()


if __name__ == '__main__':
    run_workflow()
