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

module load pre2019
module load eb
module load freesurfer
module load fsl/5.08
module load afni

source ~/.bash_profile
source ~/.bashrc
umask u+rwx,g+rwx
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

echo eddy-20200205 run03
cd ~/NHP-BIDS

./code/bids_preprocessing_workflow.py --csv ./csv/multi/Eddy_20200205/run03.csv |& \
     tee ./logs/preproc/Eddy20200205/run03.txt
wait

./code/bids_warp2nmt_workflow.py --csv ./csv/multi/Eddy_20200205/run03.csv |& \
     tee ./logs/warp2nmt/Eddy20200205/run03.txt

echo Reached the end of the job-file