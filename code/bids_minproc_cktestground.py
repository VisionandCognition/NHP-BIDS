#%%
import glob
import os
import sys
import platform
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

#%% Define the images workflows ===============================================
def create_images_workflow():
    iso_voxsize = (1.0, 1.0, 1.0)
    
    workflow = Workflow(name='minimal_proc')

    inputs = Node(IdentityInterface(fields=['images']), name="mp_in")
    outputs_minproc = Node(IdentityInterface(fields=['images']), name="mp_out")
    outputs_iso = Node(IdentityInterface(fields=['images']), name="out_iso")
    
    # correct for sphinx position
    sphinx = MapNode(fs.MRIConvert(sphinx=True),
        iterfield=['in_file'], name='sphinx')
    workflow.connect(inputs, 'images', sphinx, 'in_file')
    
    # reorient to standard fsl orientation
    ro = MapNode(fsl.Reorient2Std(), iterfield=['in_file'], name='ro')
    workflow.connect(sphinx, 'out_file', ro, 'in_file')
    workflow.connect(ro, 'out_file', outputs_minproc, 'images')
    
    # isotropic resampling
    iso = MapNode(fs.MRIConvert(vox_size=iso_voxsize),
        iterfield=['in_file'], name='iso')
    workflow.connect(ro, 'out_file', iso, 'in_file')
    workflow.connect(iso, 'out_file', outputs_iso, 'images')


    return workflow

def create_hires_workflow():
    iso_voxsize = (1.0, 1.0, 1.0)
    iso_voxsize_hires = (0.6, 0.6, 0.6)
    
    # the meain workflow
    workflow = Workflow(name='minimal_proc_hires')
    
    inputs_hires = Node(IdentityInterface(fields=['images']), name="mphr_in")
    outputs_minproc_hires = Node(IdentityInterface(fields=['images']), name="mphr_out")
    outputs_iso = Node(IdentityInterface(fields=['images']), name="out_iso")
    outputs_iso_hires = Node(IdentityInterface(fields=['images']), name="out_iso_hires")
    
    # correct for sphinx position
    sphinx = MapNode(fs.MRIConvert(sphinx=True),
        iterfield=['in_file'], name='sphinx')
    workflow.connect(inputs_hires, 'images', sphinx, 'in_file')
    
    # reorient to standard fsl orientation
    ro = MapNode(fsl.Reorient2Std(), iterfield=['in_file'], name='ro')
    workflow.connect(sphinx, 'out_file', ro, 'in_file')
    workflow.connect(ro, 'out_file', outputs_minproc_hires, 'images')
    
    # isotropic resampling
    iso = MapNode(fs.MRIConvert(vox_size=iso_voxsize),
        iterfield=['in_file'], name='iso')
    workflow.connect(ro, 'out_file', iso, 'in_file')
    workflow.connect(iso, 'out_file', outputs_iso, 'images')

    # isotropic resampling high resolution
    hires = MapNode(fs.MRIConvert(vox_size=iso_voxsize_hires),
        iterfield=['in_file'], name='hires')
    workflow.connect(ro, 'out_file', hires, 'in_file')
    workflow.connect(hires, 'out_file', outputs_iso_hires, 'images')

    return workflow


# Define the run_workflow routine =====================================
#def run_workflow(csv_file, use_pbs, stop_on_first_crash,
#                 ignore_events, types):

from nipype import config
config.enable_debug_mode()

#%% Get some path information ---------------------------
#ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if platform.system() == 'Darwin':
    ds_root = '/Users/chris/Documents/MRI_ANALYSIS/NHP-BIDS'
else:
    ds_root = '/home/chris/Documents/MRI_ANALYSIS/NHP-BIDS'
data_dir = ds_root
output_dir = ''
working_dir = 'workingdirs/minimal_processing'

# temporarily here. should be function argument.
csv_file = '%s/csv/Eddy_20181010_minproc_CK.csv' % data_dir
# ###############################################

# Get info from csv -----------------------------------
reader = niu.CSVReader()
reader.inputs.header = True
reader.inputs.in_file = csv_file
out = reader.run()
csv = out.outputs  # assign the columns of the csv-file to 'csv'

#%% create empty lists to facilitate accessing to-be-processed files
in_file = {
    'func': {'subject_id': [], 'session_id': [], 'run_id': []},
    'anat': {'subject_id': [], 'session_id': [], 'type_id': []},
    'other': {'subject_id': [], 'session_id': [], 'type_id': []},
    'ev': {'subject_id': [], 'session_id': [], 'run_id': []}
}

# func : functional scans only, run # matters
# anat : this will also take fmap and dwi scans, ignore run
# hires : only T1/T2 scans, ignore runs
# ev : only event files, run # matters

listind = 0  # keep track of list content
for entry in csv.type:
    if entry == 'func':  # 1 mm iso and check events
        # add to func list
        in_file['func']['subject_id'].append(csv.subject[listind])
        in_file['func']['session_id'].append(csv.session[listind])
        in_file['func']['run_id'].append(csv.run[listind])
        if csv.ev[listind] == 1:
            # add to ev list
            in_file['ev']['subject_id'].append(csv.subject[listind])
            in_file['ev']['session_id'].append(csv.session[listind])
            in_file['ev']['run_id'].append(csv.run[listind])
    elif entry == 'anat':
        # add to anat list
        in_file['anat']['subject_id'].append(csv.subject[listind])
        in_file['anat']['session_id'].append(csv.session[listind])
        in_file['anat']['type_id'].append(entry)
    else:
        # add to anat list
        in_file['other']['subject_id'].append(csv.subject[listind])
        in_file['other']['session_id'].append(csv.session[listind])
        in_file['other']['type_id'].append(entry)
    listind = listind + 1

#%% Grab the actual file-pointers
# create input nodes for the different filetypes    
if in_file['anat']:
    #ds_anat = nio.DataGrabber(infields=['subject_id', 'session_id', 'type_id'])
    ds_anat = Node(interface=nio.DataGrabber(
            infields=['subject_id', 'session_id', 'type_id'],
            outfields=['anat_files']),
            name='ds_anat')
    ds_anat.inputs.base_directory = data_dir
    ds_anat.inputs.template = 'sourcedata/sub-%s/ses-%s/%s/*.nii.gz'
    ds_anat.inputs.subject_id = in_file['anat']['subject_id']
    ds_anat.inputs.session_id = in_file['anat']['session_id']
    ds_anat.inputs.type_id = in_file['anat']['type_id']
    #anat_files = ds_anat.run()

if in_file['func']:
    ds_func = Node(interface=nio.DataGrabber(
            infields=['subject_id', 'session_id', 'run_id'],
            outfields=['func_files']),
            name='ds_func')
    ds_func.inputs.base_directory = data_dir
    ds_func.inputs.template = 'sourcedata/sub-%s/ses-%s/func/*run-%s*.nii.gz'
    ds_func.inputs.subject_id = in_file['func']['subject_id']
    ds_func.inputs.session_id = in_file['func']['session_id']
    ds_func.inputs.run_id = in_file['func']['run_id']
    #func_files = ds_func.run()

if in_file['other']:
    ds_other = Node(interface=nio.DataGrabber(
            infields=['subject_id', 'session_id', 'type_id'],
            outfields=['other_files']),
            name='ds_other')
    ds_anat.inputs.base_directory = data_dir
    ds_anat.inputs.template = 'sourcedata/sub-%s/ses-%s/%s/*.nii.gz'
    ds_anat.inputs.subject_id = in_file['other']['subject_id']
    ds_anat.inputs.session_id = in_file['other']['session_id']
    ds_anat.inputs.type_id = in_file['other']['type_id']
    #anat_files = ds_other.run()

""" for ev_files use JW old approach & remove this section if it works
if in_file['ev']:
    ds_ev = Node(interface=nio.DataGrabber(
            infields=['subject_id', 'session_id','run_id'],
            outfields=['ev_files']),
            name='ds_ev')
    ds_ev.inputs.base_directory = data_dir
    ds_ev.inputs.template = \
        'sourcedata/sub-%s/ses-%s/func/*events/Log_*_eventlog.csv'
    ds_ev.inputs.subject_id = in_file['func']['subject_id']
    ds_ev.inputs.session_id = in_file['func']['session_id']
    ds_ev.inputs.run_id = in_file['func']['run_id']
    #ev_files = ds_ev.run() 
"""
  
if in_file['ev']:
    evsource = Node(IdentityInterface(fields=['subject_id', 'session_id' ]), 
                    name="evsource")
    evsource.iterables = [('session_id', in_file['ev']['session_id']), 
                          ('subject_id', in_file['ev']['subject_id']),
                          ('run_id', in_file['ev']['subject_id'])]
    evfiles = Node(nio.SelectFiles({
                'csv_eventlogs':
                'sourcedata/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*run-{run_id}_'
                '*events/Log_*_eventlog.csv',
                'stim_dir':
                'sourcedata/sub-{subject_id}/ses-{session_id}/func/'
                'sub-{subject_id}_ses-{session_id}_*run-{run_id}_'
                '*events/',
             }, base_directory=data_dir), name="evfiles")


#%% Output files

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
    
    
#%% Build pipeline
workflow = Workflow(name='wrapper',
                      base_dir=os.path.join(ds_root, working_dir))

if in_file['func'] or in_file['other']:
    minproc_def = create_images_workflow()
    workflow.connect(ds_func, 'images', minimal_proc, 'in.images')
    workflow.connect(ds_other, 'images', mininimal_proc, 'in.@images')
    workflow.connect(minproc, 'out.images',
                         outputfiles, 'minimal_processing.@images')

if in_file['anat']:
    do_hires = True
    minproc_hires = create_images_workflow(do_hires)
    workflow.connect(ds_anat, 'images', minproc_hires, 'in.images')
    workflow.connect(minproc_hires, 'out.images',
                         outputfiles, 'minimal_processing.@images')
    
if in_files['ev']:
    workflow.connect([(evsource, evfiles,
                           [('subject_id', 'subject_id'),
                            ('session_id', 'session_id'),
                            ]),
                          ])
    
    csv2tsv = MapNode(ConvertCSVEventLog(), 
                      iterfield=['in_file', 'stim_dir'], name='csv2tsv')
    workflow.connect(evfiles, 'csv_eventlogs', csv2tsv, 'in_file')
    workflow.connect(evfiles, 'stim_dir', csv2tsv, 'stim_dir')
    workflow.connect(csv2tsv, 'out_file', 
                     outputfiles, 'minimal_processing.@eventlogs')

