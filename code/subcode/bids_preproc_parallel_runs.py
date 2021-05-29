#!/usr/bin/env python3

import os                                    # system functions
import argparse
import pandas as pd
import csv

def run_splitpreproc(csv_file, subses, no_warp):
    
    # define log and job folders =========================================
    job_path = './code/lisa/preproc'
    logpp_path = './logs/preproc/' + subses
    logwarp_path = './logs/warp2nmt/' + subses

    # read csv files =====================================================
    if csv_file is not None:
        df = pd.read_csv(csv_file)
        sub=[]; ses=[]; run=[]; ref=[];
        
        for index, row in df.iterrows():
            for r in row.run.strip("[]").split(" "):
                sub.append(row.subject)
                ses.append(row.session)
                run.append(r)
                if 'refsubject' in df.columns:
                    if row.refsubject == 'nan':
                        # empty field
                        ref.append(row.subject)
                    else:
                        # non-empty field
                        ref.append(row.refsubject) 
                else:
                     ref.append(row.subject)
    else:
        print("No csv-file specified. Don't know what data to process.")


    # create basefolder for csv files ====================================
    csv_path = csv_file[0:-4]
    os.makedirs(csv_path,exist_ok = True)

    # create csv files ===================================================
    for idx, subj in enumerate(sub):
        with open(csv_path + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.csv',
                    'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["subject","session","run","datatype","refsubject"])
            writer.writerow(
                [sub[idx],ses[idx],"[" + run[idx] + "]","[func]",ref[idx]])

    # create job files ===================================================
    for idx, subj in enumerate(sub):
        job_path_ses = job_path + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx])
        os.makedirs(job_path_ses,exist_ok = True)
        
        f = open(job_path_ses + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.sh' ,'w', newline='') 
        
        f.write('#!/bin/bash\n')
        f.write('#SBATCH -N 1 --ntasks-per-node=16\n')
        f.write('#SBATCH -t 10:00:00\n') # make sure this enough time!
        f.write('#SBATCH --mail-type=END\n')
        f.write('#SBATCH --mail-user=p.c.klink@gmail.com\n\n')
        f.write('echo job id $SLURM_JOBID\n')
        f.write('echo job name $SLURM_JOB_NAME\n')
        f.write('echo submitted by $SLURM_JOB_ACCOUNT\n')
        f.write('echo from $SLURM_SUBMIT_DIR\n')
        f.write('echo the allocated nodes are: $SLURM_JOB_NODELIST\n\n')
        
        #f.write('module load 2019\n')
        #f.write('module load eb\n')
        #f.write('module load FreeSurfer\n')
        #f.write('module load fsl/5.08\n')
        #f.write('module load afni\n\n')

        f.write('module load 2019\n')
        #f.write('module load FSL\n') # causes python conflicts, use local version
        f.write('module load FreeSurfer\n\n')
        
        f.write('source ~/.bash_profile\n')
        f.write('source ~/.bashrc\n')
        f.write('umask u+rwx,g+rwx\n')
        f.write('umask u+rwx,g+rwx\n\n')
        f.write('export FSLOUTPUTTYPE=NIFTI_GZ\n\n') 
        f.write('echo sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '\n')
        f.write('cd ~/NHP-BIDS\n\n')
        csv_run = csv_path + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.csv'
        logpp_run = logpp_path + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.txt'
        f.write('./code/bids_preprocessing_workflow.py ' + 
                '--csv ' + csv_run + ' |& \\\n' + '     tee ' + logpp_run + '\n')
        
        if no_warp is True:
            print('Not doing the warping to NMT')
        else:
            f.write('wait\n\n')
            logwarp_run = logwarp_path + '/run' + run[idx] + '.txt'
            f.write('./code/bids_warp2nmt_workflow.py ' + 
                    '--csv ' + csv_run + ' |& \\\n' + '     tee ' + logwarp_run + '\n\n')
            f.write('echo Reached the end of the job-file')
        
        f.close()
        
        mkexec_str = 'chmod +x ' + job_path_ses + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.sh'
        os.system(mkexec_str)
        
        submit_str = 'sbatch ' + job_path_ses + '/sub-' + sub[idx] + '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.sh'
        os.system(submit_str)
        # print(submit_str) # here for debugging



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Split pre-processing in multiple cluster-jobs')
    parser.add_argument('--csv',
                        dest='csv_file', default=None,
                        help='CSV file with subjects, sessions, runs, and refsubject.')
    parser.add_argument('--subses',
                        dest='subses', default=None,
                        help='string identifying subject and session')
    parser.add_argument('--no-warp',
                        dest='no_warp',  action='store_true',
                        help='add this flag if you do not want to warp to NMT')

    args = parser.parse_args()

    run_splitpreproc(**vars(args))