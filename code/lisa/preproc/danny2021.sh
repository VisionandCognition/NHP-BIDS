#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 00:30:00
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

export FSLOUTPUTTYPE=NIFTI_GZ

cd ~/NHP-BIDS

# preprocessing << wait with this, we need to fix the issues first
# ./code/bids_preprocessing_workflow.py --csv ./csv/ct_2021_nmt2_danny.csv  |& \
#     tee ./logs/preproc/sub-${SUB}/log-preproc-danny2021.txt

./code/subcode/bids_preproc_parallel_runs.py \
    --csv ./csv/ct_2021_nmt2_danny.csv \
    --subses ct_2021_nmt2_danny 
    
echo 'Reached the end of the job-file'
