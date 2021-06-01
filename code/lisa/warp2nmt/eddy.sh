#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 24:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=p.c.klink@gmail.com

echo job id $SLURM_JOBID
echo job name $SLURM_JOB_NAME
echo submitted by $SLURM_JOB_ACCOUNT
echo from $SLURM_SUBMIT_DIR
echo the allocated nodes are: $SLURM_JOB_NODELIST

module load pre2019

module load eb
module load freesurfer
module load fsl/5.08
module load afni

source ~/.bash_profile 
source ~/.bashrc
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

SUB=eddy

echo ${SUB}-${DATE}

cd ~/NHP-BIDS


# preprocessing << wait with this, we need to fix the issues first
./code/bids_warp2nmt_workflow.py --csv ./csv/warp2nmt/${SUB}.csv  |& \
    tee ./logs/warp2nmt/sub-${SUB}/log-warp2nmt-${SUB}.txt

# modelfit

echo 'Reached the end of the job-file'
