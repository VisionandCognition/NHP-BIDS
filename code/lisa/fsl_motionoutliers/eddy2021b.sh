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

module load 2020
module load FreeSurfer

source ~/.bash_profile 
source ~/.bashrc
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

cd ~/NHP-BIDS

# minimal processing
./code/bids_fslmotionoutliers_workflow.py --csv ./csv/ct_2021_nmt2_eddy2.csv  |& \
    tee ./logs/fslmotionoutliers/log-eddy2021b.txt
wait 


# modelfit
echo 'Reached the end of the job-file'
