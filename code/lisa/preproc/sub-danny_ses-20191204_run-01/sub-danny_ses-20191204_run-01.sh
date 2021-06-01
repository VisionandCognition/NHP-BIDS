#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 10:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=p.c.klink@gmail.com

echo job id $SLURM_JOBID
echo job name $SLURM_JOB_NAME
echo submitted by $SLURM_JOB_ACCOUNT
echo from $SLURM_SUBMIT_DIR
echo the allocated nodes are: $SLURM_JOB_NODELIST

module load 2019
module load FreeSurfer

source ~/.bash_profile
source ~/.bashrc
umask u+rwx,g+rwx
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

echo sub-danny_ses-20191204_run-01
cd ~/NHP-BIDS

./code/bids_preprocessing_workflow.py --csv ./csv/ct_2021_nmt2_danny/sub-danny_ses-20191204_run-01.csv |& \
     tee ./logs/preproc/ct_2021_nmt2_danny/sub-danny_ses-20191204_run-01.txt
wait

./code/bids_warp2nmt_workflow.py --csv ./csv/ct_2021_nmt2_danny/sub-danny_ses-20191204_run-01.csv |& \
     tee ./logs/warp2nmt/ct_2021_nmt2_danny/run01.txt

echo Reached the end of the job-file