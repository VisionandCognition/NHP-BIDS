#!/usr/bin/env python3

""" This is the first file to run (after copying the source files from
DATA_raw).

After this, you should run:

1. resample_isotropic_workflow.py (to-do: incorporate with
    preprocessing_workflow.py)
2. preprocessing_workflow.py

"""

import glob
import os
import sys
import errno

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as niu      # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
from nipype.interfaces.utility import IdentityInterface

from nipype.pipeline.engine import Workflow, Node, MapNode

import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.freesurfer as fs    # freesurfer

from bids_convert_csv_eventlog import ConvertCSVEventLog


def create_images_workflow():
    """ Correct for the sphinx position and use reorient to standard.
    """
    workflow = Workflow(
        name='minimal_proc')

    inputs = Node(IdentityInterface(fields=[
        'images',
    ]), name="in")
    outputs = Node(IdentityInterface(fields=[
        'images',
    ]), name="out")

    sphinx = MapNode(
        fs.MRIConvert(
            sphinx=True,
        ),
        iterfield=['in_file'],
        name='sphinx')

    workflow.connect(inputs, 'images',
                     sphinx, 'in_file')

    ro = MapNode(
        fsl.Reorient2Std(),
        iterfield=['in_file'],
        name='ro')

    workflow.connect(sphinx, 'out_file',
                     ro, 'in_file')
    workflow.connect(ro, 'out_file',
                     outputs, 'images')

    return workflow


def print_run(cmd):
    print('%s\n' % cmd)
    return os.system(cmd)


def process_functionals(raw_dir, glob_pat):
    for fn in glob.glob("%s/%s" % (raw_dir, glob_pat)):
        fn = os.path.basename(fn)
        print("Processing %s" % fn)

        print_run("mri_convert -i %s/%s -o /tmp/%s --sphinx" %
                  (raw_dir, fn, fn))
        print_run("fslreorient2std /tmp/%s %s" % (fn, fn))


def run_workflow(session, csv_file, use_pbs, stop_on_first_crash,
                 ignore_events, types):
    import bids_templates as bt

    from nipype import config
    config.enable_debug_mode()

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    data_dir = ds_root
    output_dir = ''
    working_dir = 'workingdirs/minimal_processing'

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
    ]), name="infosource")

    reader = niu.CSVReader()
    reader.inputs.header = True
    reader.inputs.in_file = csv_file
    out = reader.run()
    subject_list = out.outputs.subject
    session_list = out.outputs.session
    infosource.iterables = [
        ('session_id', session_list),
        ('subject_id', subject_list),
    ]
    if 'run' in out.outputs.traits().keys():
        print('Ignoring the "run" field of %s.' % csv_file)

    infosource.synchronize = True

    process_images = True

    if process_images:
        datatype_list = types.split(',')

        imgsource = Node(IdentityInterface(fields=[
            'subject_id', 'session_id', 'datatype',
        ]), name="imgsource")
        imgsource.iterables = [
            ('session_id', session_list), ('subject_id', subject_list),
            ('datatype', datatype_list),
        ]

        # SelectFiles
        imgfiles = Node(
            nio.SelectFiles({
                'images':
                'sourcedata/%s' % bt.templates['images'],
            }, base_directory=data_dir), name="img_files")

    evsource = Node(IdentityInterface(fields=[
        'subject_id', 'session_id',
    ]), name="evsource")
    evsource.iterables = [
        ('session_id', session_list), ('subject_id', subject_list),
    ]
    
    if not ignore_events:
        evfiles = Node(
            nio.SelectFiles({
                'csv_eventlogs':
                'sourcedata/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*events/Log_*_eventlog.csv',
                'stim_dir':
                'sourcedata/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*events/',
            }, base_directory=data_dir), name="evfiles")

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
        ('/minimal_processing/', '/'),
        ('_out_reoriented.nii.gz', '.nii.gz')
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        (r'_datatype_([a-z]*)_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'sub-\3/ses-\2/\1'),
        (r'/_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'/sub-\2/ses-\1/'),
        (r'/_ro[0-9]+/', r'/'),
        (r'/_csv2tsv[0-9]+/', r'/func/'),
    ]

    # -------------------------------------------- Create Pipeline
    workflow = Workflow(
        name='wrapper',
        base_dir=os.path.join(ds_root, working_dir))

    if process_images:
        workflow.connect([(imgsource, imgfiles,
                          [('subject_id', 'subject_id'),
                           ('session_id', 'session_id'),
                           ('datatype', 'datatype'),
                           ])])

    workflow.connect([(evsource, evfiles,
                       [('subject_id', 'subject_id'),
                        ('session_id', 'session_id'),
                        ]),
                      ])

    if process_images:
        minproc = create_images_workflow()
        workflow.connect(imgfiles, 'images',
                         minproc, 'in.images')
        workflow.connect(minproc, 'out.images',
                         outputfiles, 'minimal_processing.@images')

    if not ignore_events:
        csv2tsv = MapNode(
            ConvertCSVEventLog(),
            iterfield=['in_file', 'stim_dir'],
            name='csv2tsv')
        workflow.connect(evfiles, 'csv_eventlogs',
                         csv2tsv, 'in_file')
        workflow.connect(evfiles, 'stim_dir',
                         csv2tsv, 'stim_dir')
        workflow.connect(csv2tsv, 'out_file',
                         outputfiles, 'minimal_processing.@eventlogs')

    workflow.stop_on_first_crash = stop_on_first_crash
    workflow.keep_inputs = True
    workflow.remove_unnecessary_outputs = False
    workflow.write_graph()
    #workflow.run(plugin='MultiProc', plugin_args={'n_procs' : 10})
    workflow.run()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Perform isotropic resampling for NHP fMRI. Run bids_minimal_processing first.')
    parser.add_argument('-s', '--session', type=str, default=None,
            help='Session ID, e.g. 20170511.')
    parser.add_argument('--types', type=str, default='func,anat,fmap,dwi',
                        help='Image datatypes, e.g. func,anat,fmap.')
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, and runs.')
    parser.add_argument('--pbs', dest='use_pbs', action='store_true',
            help='Whether to use pbs plugin.')
    parser.add_argument('--stop_on_first_crash', dest='stop_on_first_crash', action='store_true',
            help='Whether to stop on first crash.')
    parser.add_argument('--ignore_events', dest='ignore_events', action='store_true',
            help='Whether to ignore the csv event files')

    args = parser.parse_args()

    run_workflow(**vars(args))
