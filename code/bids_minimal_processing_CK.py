#!/usr/bin/env python3

""" This is the first file to run (after copying the source files from
DATA_raw with a copy-to-bids.sh variant).

In the original version (JW) it did not resample to isotropic voxels
I have added that so no extra step is necessary

After this, you should run:

(no longer required) 1. resample_isotropic_workflow.py (to-do: incorporate with
    preprocessing_workflow.py)
2. preprocessing_workflow.py for motion correction

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






def create_images_workflow():  # The original code
    """ Correct for the sphinx position and use reorient to standard.
    """
    # This workflow takes input images and performs minimal processing
    # - correction for sphinx position
    # - reorientation to fsl standard
    # - resampling to isotropic voxels
    # ====== WORK IN PROGRESS ========
    # It should be cloned and adjusted to handle different file-types
    # ================================
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



# THIS DOES NOT SEEM TO GET USED >>> REPLACED WITH NODES IN WORKFLOW =======
def process_functionals(raw_dir, glob_pat):
    for fn in glob.glob("%s/%s" % (raw_dir, glob_pat)):
        fn = os.path.basename(fn)
        print("Processing %s" % fn)

        print_run("mri_convert -i %s/%s -o /tmp/%s --sphinx" %
                  (raw_dir, fn, fn))
        print_run("fslreorient2std /tmp/%s %s" % (fn, fn))
# OBSOLETE =================================================================




















#def run_workflow(session, csv_file, use_pbs, stop_on_first_crash,
#                 ignore_events, types):
#    import bids_templates as bt
#
#    from nipype import config
#    config.enable_debug_mode()











if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Perform isotropic resampling for NHP fMRI.'
        ' Run bids_minimal_processing first.')
    parser.add_argument('-s', '--session',
                        type=str,
                        default=None,
                        help='Session ID, e.g. 20170511.'
                        )
    parser.add_argument('--types',
                        type=str,
                        default='func,anat,fmap',
                        help='Image datatypes, e.g. func,anat,fmap,dwi.'
                        )
    parser.add_argument('--csv',
                        dest='csv_file',
                        required=True,
                        help='CSV file with subjects, sessions, and runs.'
                        )
    parser.add_argument('--pbs',
                        dest='use_pbs',
                        action='store_true',
                        help='Whether to use pbs plugin.'
                        )
    parser.add_argument('--stop_on_first_crash',
                        dest='stop_on_first_crash',
                        action='store_true',
                        help='Whether to stop on first crash.'
                        )
    parser.add_argument('--ignore_events',
                        dest='ignore_events',
                        action='store_true',
                        help='Whether to ignore the csv event files'
                        )

    args = parser.parse_args()

    run_workflow(**vars(args))
