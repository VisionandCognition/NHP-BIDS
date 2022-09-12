#!/usr/bin/env python3

""" 
This script resamples MRI image files to isotropic voxels.
It assumes that data is in BIDS format and that the script
bids_minimal_processing_workflow.py has been run. 

After this, you should/could run:
- bids_preprocessing_workflow.py
  >> performs preprocessing steps like normalisation and motion correction
- bids_modelfit_workflow.py
  >> Fits a GLM and outputs statistics

Questions & comments: c.klink@nin.knaw.nl
"""

import os                                    # system functions
import pandas as pd                          # data juggling

import nipype.interfaces.io as nio           # Data i/o
from nipype.interfaces.utility import IdentityInterface
from nipype.pipeline.engine import Workflow, Node, MapNode


def run_workflow(project, session=None, csv_file=None):
    from nipype import config
    #config.enable_debug_mode()

    method = 'fs'  # freesurfer's mri_convert is faster
    if method == 'fs':
        import nipype.interfaces.freesurfer as fs    # freesurfer
    else:
        assert method == 'fsl'
        import nipype.interfaces.fsl as fsl          # fsl

    # ------------------ Specify variables
    # ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # data_dir = ds_root
    # output_dir = 'derivatives/resampled-isotropic-06mm'
    # working_dir = 'workingdirs'

    ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) # NHP-BIDS fld
    data_dir = ds_root + '/projects/' + project
    output_dir = 'projects/' + project + '/derivatives/resampled-isotropic-06mm'
    working_dir = 'projects/' + project + '/workingdirs'

    # ------------------ Input Files
    infosource = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'datatype',
    ]), name="infosource")

    if csv_file is not None:
        # Read csv and use pandas to set-up image and ev-processing
        df = pd.read_csv(csv_file)
        # init lists
        sub_img=[]; ses_img=[]; dt_img=[]

        # fill lists to iterate mapnodes
        for index, row in df.iterrows():
            for dt in row.datatype.strip("[]").split(" "):
                if dt in ['anat']:  # only for anatomicals
                    sub_img.append(row.subject)
                    ses_img.append(row.session)
                    dt_img.append(dt)

        # check if the file definitions are ok
        if len(dt_img) > 0:
            print('There are images to process. Will continue.')
        else:
            print('No images specified. Check your csv-file.')

        infosource.iterables = [
            ('session_id', ses_img), 
            ('subject_id', sub_img), 
            ('datatype', dt_img)
            ]
        infosource.synchronize = True
    else:
        print('No csv-file specified. Cannot continue.')

    # SelectFiles
    templates = {
        'image': 'sub-{subject_id}/ses-{session_id}/{datatype}/'
        'sub-{subject_id}_ses-{session_id}_*.nii.gz',
    }
    inputfiles = Node(
        nio.SelectFiles(templates,
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
        ('_resample.nii.gz', '_res-06x06x06_preproc.nii.gz'),
        # remove subdirectories:
        ('resampled-isotropic-06mm/isoxfm-06mm', 'resampled-isotropic-06mm'),
        ('resampled-isotropic-06mm/mriconv-06mm', 'resampled-isotropic-06mm'),
    ]
    # Put result into a BIDS-like format
    outputfiles.inputs.regexp_substitutions = [
        # this works only if datatype is specified in input
        (r'_datatype_([a-z]*)_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
         r'sub-\3/ses-\2/\1'),
        (r'_fs_iso06mm[0-9]*/', r''),
        (r'/_ses-([a-zA-Z0-9]*)_sub-([a-zA-Z0-9]*)',
         r'/sub-\2/ses-\1/'),
        # stupid hacks for when datatype is not specified
        (r'//(sub-[^/]*_bold_res-.*)', r'/func/\1'),
        (r'//(sub-[^/]*_phasediff_res-.*.nii.gz)', r'/fmap/\1'),
        (r'//(sub-[^/]*_magnitude1_res-.*.nii.gz)', r'/fmap/\1'),
        (r'//(sub-[^/]*_epi_res-.*.nii.gz)', r'/fmap/\1'),
        (r'//(sub-[^/]*_T1w_res-.*.nii.gz)', r'/anat/\1'),
        (r'//(sub-[^/]*_T2w_res-.*.nii.gz)', r'/anat/\1'),
        (r'//(sub-[^/]*_dwi_res-.*.nii.gz)', r'/dwi/\1'),
    ]

    # -------------------------------------------- Create Pipeline
    isotropic_flow = Workflow(
        name='resample_isotropic06mm',
        base_dir=os.path.join(ds_root, working_dir))

    isotropic_flow.connect([
        (infosource, inputfiles,
         [('subject_id', 'subject_id'),
          ('session_id', 'session_id'),
          ('datatype', 'datatype'),
          ])])

    # --- Convert to 1m isotropic voxels

    if method == 'fs':
        fs_iso06mm = MapNode(
            fs.Resample(
                voxel_size=(0.6, 0.6, 0.6),
                # suffix is not accepted by fs.Resample
                # suffix='_res-1x1x1_preproc',
                # BIDS Extension Proposal: BEP003
            ),
            name='fs_iso06mm',
            iterfield=['in_file'],
        )

        isotropic_flow.connect(inputfiles, 'image',
                               fs_iso06mm, 'in_file')
        isotropic_flow.connect(fs_iso06mm, 'resampled_file',
                               outputfiles, 'mriconv-06mm')
    elif method == 'fsl':
        # in_file --> out_file
        isoxfm = Node(fsl.FLIRT(
            apply_isoxfm=0.6,
        ),
            name='isoxfm')

        isotropic_flow.connect(inputfiles, 'image',
                               isoxfm, 'in_file')
        isotropic_flow.connect(inputfiles, 'image',
                               isoxfm, 'reference')
        isotropic_flow.connect(isoxfm, 'out_file',
                               outputfiles, 'isoxfm-06mm')

    isotropic_flow.stop_on_first_crash = False  # True
    isotropic_flow.keep_inputs = True
    isotropic_flow.remove_unnecessary_outputs = False
    isotropic_flow.write_graph()
    outgraph = isotropic_flow.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
            description='Perform isotropic resampling for NHP fMRI.'
            ' Run bids_minimal_processing first.')
    parser.add_argument('--proj', dest='project', required=True,
                        help='project label for subfolder.' )
    parser.add_argument('-s', '--session', type=str,
                        help='Session ID, e.g. 20170511.')
    parser.add_argument('--csv', dest='csv_file', default=None,
                        help='CSV file with subjects, sessions, and runs.')

    args = parser.parse_args()

    run_workflow(**vars(args))
