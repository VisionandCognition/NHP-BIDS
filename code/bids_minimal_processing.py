#!/usr/bin/env python3

""" 
This is the first script to run after copying the source files to NHP-BIDS.
It performs some minimal processing:
- Image files are corrected for sphinx orientation
- FSL orientation is corrected
- Eventlog csv files are converted to tsv where possible
- Files are moved to the correct folders

Questions & comments: c.klink@nin.knaw.nl
"""

#import glob                                # paths & filenames
import os                                   # system functions
import pandas as pd                         # data juggling

# nipype
import nipype.interfaces.io as nio          # data i/o
import nipype.interfaces.fsl as fsl         # fsl
import nipype.interfaces.freesurfer as fs   # freesurfer
from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Workflow, Node, MapNode

# custom library
from subcode.bids_convert_csv_eventlog import ConvertCSVEventLog


def create_images_workflow():
    # Correct for the sphinx position and use reorient to standard.
    workflow = Workflow(name='minimal_proc')

    inputs = Node(IdentityInterface(fields=['images']), name="in")
    outputs = Node(IdentityInterface(fields=['images']), name="out")

    sphinx = MapNode(fs.MRIConvert(sphinx=True), iterfield=['in_file'], name='sphinx')
    workflow.connect(inputs, 'images', sphinx, 'in_file')

    ro = MapNode(fsl.Reorient2Std(), iterfield=['in_file'], name='ro')

    workflow.connect(sphinx, 'out_file', ro, 'in_file')
    workflow.connect(ro, 'out_file', outputs, 'images')

    return workflow


def run_workflow(csv_file, project, stop_on_first_crash, ignore_events):
    
    from nipype import config
    #config.enable_debug_mode()

    # ------------------ Specify variables
    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) # NHP-BIDS fld
    data_dir = ds_root + '/projects/' + project
    output_dir = 'projects/' + project
    working_dir = 'projects/' + project + '/workingdirs/minimal_processing'

    # ------------------ Input Files
    # Read csv and use pandas to set-up image and ev-processing
    df = pd.read_csv(csv_file)
    # init lists
    sub_img=[]; ses_img=[]; dt_img=[]
    sub_ev=[]; ses_ev=[]; run_ev=[]

    # fill lists to iterate mapnodes
    for index, row in df.iterrows():
        for dt in row.datatype.strip("[]").split(" "):
            sub_img.append(row.subject)
            ses_img.append(row.session)
            dt_img.append(dt)
        for r in row.run.strip("[]").split(" "):
            sub_ev.append(row.subject)
            ses_ev.append(row.session)
            run_ev.append(r)

    # check if the file definitions are ok
    if len(dt_img) > 0:
        process_images = True
    else:
        process_images = False
        print('NB! No data-types specified. Not processing any images.')
        print('Check the csv-file if this is unexpected.')

    if len(run_ev) > 0:
        process_ev = True
    else:
        process_ev = False
        print('NB! No runs spcfied. Not processing eventlog files.'
            ' Images will still be processed.')
        print('Check the csv-file if this is unexpected.')

    if process_images:
        imgsource = Node(IdentityInterface(fields=[
            'subject_id',
            'session_id', 
            'datatype',
            ]), name="imgsource")
        imgsource.iterables = [
            ('session_id', ses_img), 
            ('subject_id', sub_img), 
            ('datatype', dt_img)
            ]
        imgsource.synchronize = True

        # SelectFiles
        imgfiles = Node(
            nio.SelectFiles({
                'images':
                'data_collection/sub-{subject_id}/ses-{session_id}/{datatype}/'
                'sub-{subject_id}_ses-{session_id}_*.nii.gz' 
                }, base_directory=data_dir), name="img_files")

    if not ignore_events and process_ev:  # only create an event node when handling events
        evsource = Node(IdentityInterface(fields=[
            'subject_id', 
            'session_id',
            'run_id',
            ]), name="evsource")
        evsource.iterables = [
            ('subject_id', sub_ev),
            ('session_id', ses_ev), 
            ('run_id', run_ev),
            ]
        evsource.synchronize = True
        evfiles = Node(
            nio.SelectFiles({
                'csv_eventlogs':
                'data_collection/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*_run-{run_id}_events/Log_*_eventlog.csv',
                'stim_dir':
                'data_collection/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*_run-{run_id}_events/',
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
        (r'_run_id_([a-zA-Z0-9]*)_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
            r'/sub-\3/ses-\2/'),
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

    if not ignore_events and process_ev:
        workflow.connect([(evsource, evfiles,
                           [('subject_id', 'subject_id'),
                            ('session_id', 'session_id'),
                            ('run_id', 'run_id'),
                            ]),
                          ])

    if process_images:
        minproc = create_images_workflow()
        workflow.connect(imgfiles, 'images',
                         minproc, 'in.images')
        workflow.connect(minproc, 'out.images',
                         outputfiles, 'minimal_processing.@images')

    if not ignore_events and process_ev:
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
    workflow.remove_unnecessary_outputs = True
    workflow.write_graph()
    workflow.run()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Perform minimal_processing for NHP fMRI.'
        )
    parser.add_argument('--proj', dest='project', required=True,
                        help='project label for subfolder.'
                        )
    parser.add_argument('--csv', dest='csv_file', required=True,
                        help='CSV file with subjects, sessions, and runs.'
                        )
    parser.add_argument('--stop_on_first_crash', dest='stop_on_first_crash',
                        action='store_true', help='Whether to stop on first crash.'
                        )
    parser.add_argument('--ignore_events', dest='ignore_events',
                        action='store_true', help='Whether to ignore all csv event files. '
                        'By default csv event files are processed for specified runs '
                        '(while imaging files are processed for all runs)'
                        )

    args = parser.parse_args()

    run_workflow(**vars(args))
