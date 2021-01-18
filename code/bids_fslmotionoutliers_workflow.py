#!/usr/bin/env python3

""" 
This script performs additional motion outlier detection on preprocessed fMRI data.
It assumes that data is in BIDS format and that the data has undergone 
minimal processing, resampling, and preprocessing.

Questions & comments: c.klink@nin.knaw.nl
"""


from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range

import os, shutil                             # system functions
import pandas as pd                           

import nipype.interfaces.io as nio            # Data i/o
import nipype.interfaces.fsl as fsl           # fsl
from nipype.interfaces import utility as niu  # Utilities
import nipype.pipeline.engine as pe           # pypeline engine
import nipype.algorithms.modelgen as model    # model generation

try: # facilitate different nipype versions
    import nipype.workflows.fmri.fsl as fslflows
except:
    import niflow.nipype1.workflows.fmri.fsl as fslflows
    
from subcode.filter_numbers import FilterNumsTask

ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = ds_root


def get_csv_stem(csv_file):
    csv_filename = csv_file.split('/')[-1]
    csv_stem = csv_filename.split('.')[0]
    return csv_stem

def create_workflow():
    fsl_workflow = pe.Workflow(name='fslmotoutliers')
    level1_workflow.base_dir = os.path.abspath(
        './workingdirs/level1flow/' + contrasts_name + '/' + RegSpace + '/level1')

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
        # 'funcmasks',
        'fwhm',  # smoothing
        'highpass',

        'funcs',
        'event_log',
        'motion_parameters',
        'motion_outlier_files',

        'ref_func',
        'ref_funcmask',
    ]), name="inputspec")

    def remove_runs_missing_funcs(in_files, in_funcs):
        import os
        import re

        assert not isinstance(in_files, str), "in_files must be list"
        assert not isinstance(in_funcs, str), "in_funcs must be list"

        if isinstance(in_files, str):
            in_files = [in_files]

        if isinstance(in_funcs, str):
            in_funcs = [in_funcs]

        has_func = set()
        for f in in_funcs:
            base = os.path.basename(f)
            try:
                sub = re.search(r'sub-([a-zA-Z0-9]+)_', base).group(1)
                ses = re.search(r'ses-([a-zA-Z0-9]+)_', base).group(1)
                run = re.search(r'run-([a-zA-Z0-9]+)_', base).group(1)
            except AttributeError as e:
                raise RuntimeError('Could not process "sub-*_", "ses-*_", " \
                    "or "run-*_" from func "%s"' % f)
            has_func.add((sub, ses, run))

        files = []
        for f in in_files:
            base = os.path.basename(f)
            try:
                sub = re.search(r'sub-([a-zA-Z0-9]+)_', base).group(1)
                ses = re.search(r'ses-([a-zA-Z0-9]+)_', base).group(1)
                run = re.search(r'run-([a-zA-Z0-9]+)_', base).group(1)
            except AttributeError as e:
                raise RuntimeError('Could not process "sub-*_", "ses-*_", " \
                    "or "run-*_" from event file "%s"' % f)
            if (sub, ses, run) in has_func:
                files.append(f)
        return files

    input_events = pe.Node(
        interface=niu.Function(input_names=['in_files', 'in_funcs'],
                               output_names=['out_files'],
                               function=remove_runs_missing_funcs),
        name='input_events',
    )

    level1_workflow.connect([
        (inputnode, input_events,
         [('funcs', 'in_funcs'),
          ('event_log', 'in_files'),
          ]),
    ])

    # -------------------------------------------------------------------
    #            /~_ _  _  _  _. _   _ . _  _ |. _  _
    #            \_/(/_| |(/_| |(_  |_)||_)(/_||| |(/_
    #                               |   |
    # -------------------------------------------------------------------
    """
    Preliminaries
    -------------
    Setup any package specific configuration. The output file format for FSL
    routines is being set to compressed NIFTI.
    """

    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

    modelfit = fslflows.create_modelfit_workflow()
    modelspec = pe.Node(model.SpecifyModel(), name="modelspec")

    """
    Set up first-level workflow
    ---------------------------
    """

    def sort_copes(files):
        """ Sort by copes and the runs, ie.
            [[cope1_run1, cope1_run2], [cope2_run1, cope2_run2]]
        """
        assert files[0] is not str

        numcopes = len(files[0])
        assert numcopes > 1

        outfiles = []
        for i in range(numcopes):
            outfiles.insert(i, [])
            for j, elements in enumerate(files):
                outfiles[i].append(elements[i])
        return outfiles

    def num_copes(files):
        return len(files)


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
    # --- LEV1 ---
    # Datasink
    outputfiles_lev1 = pe.Node(nio.DataSink(
                base_directory=ds_root,
                container='derivatives/modelfit/' +  contrasts_name + '/' + RegSpace + '/level1',
                parameterization=True),
                name="output_files")

    # Use the following DataSink output substitutions
    outputfiles_lev1.inputs.substitutions = [
        ('subject_id_', 'sub-'),
        ('session_id_', 'ses-'),
        ('/_mc_method_afni3dAllinSlices/', '/'),
    ]
    # Put result into a BIDS-like format
    outputfiles_lev1.inputs.regexp_substitutions = [
        (r'_ses-([a-zA-Z0-9]+)_sub-([a-zA-Z0-9]+)', r'sub-\2/ses-\1'),
        (r'_refsub([a-zA-Z0-9]+)', r''),
    ]
    level1_workflow.connect([
        (modelfit, outputfiles_lev1,
         [(('outputspec.copes', sort_copes), 'copes'),
          ('outputspec.dof_file', 'dof_files'),
          (('outputspec.varcopes', sort_copes), 'varcopes'),
          ]),
    ])

    # -------------------------------------------------------------------
    #          (~   _  _  _. _ _  _  _ _|_   _ _  _  _. |`. _
    #          (_><|_)(/_| || | |(/_| | |   _\|_)(/_(_|~|~|(_
    #              |                          |
    # -------------------------------------------------------------------

    """
    Use the get_node function to retrieve an internal node by name. Then set
    iterables on this node to perform two different extents of smoothing.
    """

    featinput = level1_workflow.get_node('modelfit.inputspec')
    featinput.inputs.fwhm = fwhm

    hpcutoff_s = HighPass  # FWHM in seconds
    TR = 2.5
    hpcutoff_nvol = hpcutoff_s / 2.5  # FWHM in volumns

    # Use Python3 for processing. See code/requirements.txt for pip packages.
    featinput.inputs.highpass = hpcutoff_nvol / 2.355  # Gaussian: σ in vols

    """
    Setup a function that returns subject-specific information about the
    experimental paradigm. This is used by the
    :class:`nipype.modelgen.SpecifyModel` to create the information necessary
    to generate an SPM design matrix. In this tutorial, the same paradigm was
    used for every participant. Other examples of this function are available
    in the `doc/examples` folder. Note: Python knowledge required here.
    """

    # from timeevents.curvetracing import calc_curvetracing_events
    from timeevents import process_time_events

    timeevents = pe.MapNode(
        interface=process_time_events,  # calc_curvetracing_events,
        iterfield=('event_log', 'in_nvols', 'TR'),
        name='timeevents')

    def get_nvols(funcs):
        import nibabel as nib
        nvols = []

        if isinstance(funcs, str):
            funcs = [funcs]

        for func in funcs:
            func_img = nib.load(func)
            header = func_img.header
            try:
                nvols.append(func_img.get_data().shape[3])
            except IndexError as e:
                # if shape only has 3 dimensions, then it is only 1 volume
                nvols.append(1)
        return(nvols)

    def get_TR(funcs):
        import nibabel as nib
        TRs = []

        if isinstance(funcs, str):
            funcs = [funcs]

        for func in funcs:
            func_img = nib.load(func)
            header = func_img.header
            try:
                TR = round(header.get_zooms()[3], 5)
            except IndexError as e:
                TR = 2.5
                print("Warning: %s did not have TR defined in the header. "
                      "Using default TR of %0.2f" %
                      (func, TR))

            assert TR > 1
            TRs.append(TR)
        return(TRs)

    level1_workflow.connect([
        (inputnode, timeevents,
         [(('funcs', get_nvols), 'in_nvols'),
          (('funcs', get_TR), 'TR'),
          ]),
        (input_events, timeevents,
         [('out_files', 'event_log')]),
        (inputnode, modelspec,
         [('motion_parameters', 'realignment_parameters')]),
        (modelspec, modelfit,
         [('session_info', 'inputspec.session_info')]),
    ])

    # Ignore volumes after last good response
    filter_outliers = pe.MapNode(
        interface=FilterNumsTask(),
        name='filter_outliers',
        iterfield=('in_file', 'max_number')
    )

    level1_workflow.connect([
        (inputnode, filter_outliers,
         [('motion_outlier_files', 'in_file')]),
        (filter_outliers, modelspec,
         [('out_file', 'outlier_files')]),
        (timeevents, filter_outliers,
         [('out_nvols', 'max_number')]),
    ])

    def evt_info(cond_events):
        output = []

        # for each run
        for ev in cond_events:
            from nipype.interfaces.base import Bunch
            from copy import deepcopy
            names = []

            for name in ev.keys():
                if ev[name].shape[0] > 0:
                    names.append(name)

            onsets = [deepcopy(ev[name].time)
                      if ev[name].shape[0] > 0 else [] for name in names]
            durations = [deepcopy(ev[name].dur)
                         if ev[name].shape[0] > 0 else [] for name in names]
            amplitudes = [deepcopy(ev[name].amplitude)
                          if ev[name].shape[0] > 0 else [] for name in names]

            run_results = Bunch(
                conditions=names,
                onsets=[deepcopy(ev[name].time) for name in names],
                durations=[deepcopy(ev[name].dur) for name in names],
                amplitudes=[deepcopy(ev[name].amplitude) for name in names])

            output.append(run_results)
        return output

    modelspec.inputs.input_units = 'secs'
    modelspec.inputs.time_repetition = TR  # to-do: specify per func
    modelspec.inputs.high_pass_filter_cutoff = hpcutoff_s

    # Find out which HRF function we want to use
    if hrf == 'fsl_doublegamma':  # this is the default
        modelfit.inputs.inputspec.bases = {'dgamma': {'derivs': True}}
    else:
        # use a custom hrf as defined in arguments
        currpath = os.getcwd()
        hrftxt = currpath + hrf[1:]
        modelfit.inputs.inputspec.bases = {'custom': {'bfcustompath': hrftxt}}
        
    modelfit.inputs.inputspec.interscan_interval = TR
    modelfit.inputs.inputspec.contrasts = contrasts
    modelfit.inputs.inputspec.model_serial_correlations = True
    modelfit.inputs.inputspec.film_threshold = 1000

    modelfit.config['execution'] = dict(
        crashdump_dir=os.path.abspath('.'))

    # Ignore volumes after subject has finished working for the run
    beh_roi = pe.MapNode(
        fsl.ExtractROI(t_min=0),
        name='beh_roi',
        iterfield=['in_file', 't_size'])

    level1_workflow.connect([
        (timeevents, modelspec,
         [(('out_events', evt_info), 'subject_info'),
          ]),
        (inputnode, beh_roi,
         [('funcs', 'in_file'),
          ]),
        (timeevents, beh_roi,
         [('out_nvols', 't_size'),
          ]),
        (beh_roi, modelspec,
         [('roi_file', 'functional_runs'),
          ]),
        (beh_roi, modelfit,
         [('roi_file', 'inputspec.functional_data'),
          ]),
        (beh_roi, outputfiles_lev1,
         [('roi_file', 'roi_file'),
          ]),
        # (inputnode, datasource, [('in_data', 'base_directory')]),
        # (infosource, datasource, [('subject_id', 'subject_id')]),
        # (infosource, modelspec, [(('subject_id', subjectinfo),
        # 'subject_info')]),
        # (datasource, preproc, [('func', 'inputspec.func')]),
    ])
    return(level1_workflow)


# ===================================================================
#                       ______ _
#                      |  ____(_)
#                      | |__   _ _ __
#                      |  __| | | '_ \
#                      | |    | | | | |
#                      |_|    |_|_| |_|
#
# ===================================================================

def run_workflow(csv_file):
    workflow = pe.Workflow(name='run_fslmotionoutliers')
    workflow.base_dir = os.path.abspath('./workingdirs')

    from nipype import config, logging
    config.update_config(
        {'logging':
         {'log_directory': os.path.join(workflow.base_dir, 'logs'),
          'log_to_file': True,
          # 'workflow_level': 'DEBUG', #  << massive output
          # 'interface_level': 'DEBUG', #  << massive output
          'workflow_level': 'INFO',
          'interface_level': 'INFO',
          }})
    logging.update_logging(config)
    config.enable_debug_mode()

    # redundant with enable_debug_mode() ...
    workflow.stop_on_first_crash = True
    workflow.remove_unnecessary_outputs = False
    workflow.keep_inputs = True
    workflow.hash_method = 'content'

    fslmotionoutliers = create_workflow()

    inputnode = pe.Node(niu.IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'run_id',
    ]), name='input')

    assert csv_file is not None, "--csv argument must be defined!"

    if csv_file is not None:
      # Read csv and use pandas to set-up image and ev-processing
      df = pd.read_csv(csv_file)
      # init lists
      sub_img=[]; ses_img=[]; run_img=[];
      
      # fill lists to iterate mapnodes
      for index, row in df.iterrows():
        for r in row.run.strip("[]").split(" "):
            sub_img.append(row.subject)
            ses_img.append(row.session)
            run_img.append(r)

      inputnode.iterables = [
            ('subject_id', sub_img),
            ('session_id', ses_img),
            ('run_id', run_img),
        ]
      inputnode.synchronize = True
    else:
      print("No csv-file specified. Don't know what data to process.")

  
    templates = {
        'motion_outlier_files':
        'derivatives/featpreproc/motion_outliers/sub-{subject_id}/'
        'ses-{session_id}/func/art.sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_preproc_mc_maths_outliers.txt',

        'masks':
        'derivatives/featpreproc/motion_outliers/sub-{subject_id}/'
        'ses-{session_id}/func/mask.sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_preproc_mc_maths.nii.gz',

        'motion_corrected':
        'derivatives/featpreproc/motion_corrected/sub-{subject_id}/'
        'ses-{session_id}/func/sub-{subject_id}_ses-{session_id}_*_'
        'run-{run_id}_bold_res-1x1x1_preproc_mc.nii.gz',
        }  


    inputfiles = pe.Node(
        nio.SelectFiles(templates,
                        base_directory=data_dir),
        name='in_files')

    workflow.connect([
        (inputnode, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('run_id', 'run_id'),
          ]),
    ])

    join_input = pe.JoinNode(
        niu.IdentityInterface(fields=[
            'motion_outlier_files',
            'masks',
            'motion_corrected',
            ]
            ),
        joinsource='input',
        joinfield=[
            'motion_outlier_files',
            'masks',
            'motion_corrected',
            ],
        name='join_input')

    workflow.connect([
        (inputfiles, join_input,
         [
          ('motion_outlier_files', 'motion_outlier_files'),
          ('masks', 'masks'),
          ('motion_corrected', 'motion_corrected'),
          ]),
        (join_input, fslmotionoutliers,
         [
          ('motion_outlier_files', 'inputspec.motion_outlier_files'),
          ('masks', 'inputspec.masks'),
          ('motion_corrected', 'inputspec.motion_corrected'),
          ]),
    ])

    fslmotionoutliers.write_graph(simple_form=True)
    fslmotionoutliers.write_graph(graph2use='orig', format='png', simple_form=True)

    workflow.workflow_level = 'INFO'    # INFO/DEBUG
    # workflow.stop_on_first_crash = True
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph(simple_form=True)
    workflow.write_graph(graph2use='colored', format='png', simple_form=True)
    workflow.run()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='Perform additional motion outlier detection.')
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, and runs.')

    args = parser.parse_args()
    run_workflow(**vars(args))
