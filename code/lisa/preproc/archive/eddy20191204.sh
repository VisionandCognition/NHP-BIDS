#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 32:00:00
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

SUB=Eddy
DATE=20191204

echo ${SUB}-${DATE}

cd ~/NHP-BIDS

# preprocessing
./code/bids_preprocessing_workflow.py --csv ./csv/preproc/${SUB}_${DATE}.csv  |& \
    tee ./logs/preproc/sub-${SUB}/log-preproc-${SUB}-${DATE}.txt

# modelfit

echo 'Reached the end of the job-file'
