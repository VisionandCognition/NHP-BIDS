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

csv_file = '%s/csv/Eddy_20181010_minproc_CK.csv' % data_dir

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
    elif entry == 'anat' or entry == 'dwi' or entry == 'fmap':
        # add to anat list
        in_file['anat']['subject_id'].append(csv.subject[listind])
        in_file['anat']['session_id'].append(csv.session[listind])
        in_file['anat']['type_id'].append(entry)
    listind = listind + 1

#%% Grab the actual file-pointers
if in_file['anat']:
    ds_anat = nio.DataGrabber(infields=['subject_id', 'session_id', 'type_id'])
    ds_anat.inputs.base_directory = data_dir
    ds_anat.inputs.template = 'sourcedata/sub-%s/ses-%s/%s/*.nii.gz'
    ds_anat.inputs.sort_filelist = True
    ds_anat.inputs.subject_id = in_file['anat']['subject_id']
    ds_anat.inputs.session_id = in_file['anat']['session_id']
    ds_anat.inputs.type_id = in_file['anat']['type_id']
    anat_files = ds_anat.run()

if in_file['func']:
    ds_func = nio.DataGrabber(infields=['subject_id', 'session_id', 'run_id'])
    ds_func.inputs.base_directory = data_dir
    ds_func.inputs.template = 'sourcedata/sub-%s/ses-%s/func/*run-%s*.nii.gz'
    ds_func.inputs.sort_filelist = True
    ds_func.inputs.subject_id = in_file['func']['subject_id']
    ds_func.inputs.session_id = in_file['func']['session_id']
    ds_func.inputs.run_id = in_file['func']['run_id']
    func_files = ds_func.run()
    
if in_file['ev']:
    ds_ev = nio.DataGrabber(infields=['subject_id', 'session_id','run_id'])
    ds_ev.inputs.base_directory = data_dir
    ds_ev.inputs.template = 'sourcedata/sub-%s/ses-%s/func/*run-%s*.nii.gz'
    ds_ev.inputs.sort_filelist = True
    ds_ev.inputs.subject_id = in_file['func']['subject_id']
    ds_ev.inputs.session_id = in_file['func']['session_id']
    ds_ev.inputs.run_id = in_file['func']['run_id']
    ev_files = ds_ev.run()

#%% 