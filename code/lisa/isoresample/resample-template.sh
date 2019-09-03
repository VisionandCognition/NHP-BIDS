#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 01:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=p.c.klink@gmail.com

echo job id $SLURM_JOBID
echo job name $SLURM_JOB_NAME
echo submitted by $mail-user
echo from $SLURM_SUBMIT_DIR
echo the allocated nodes are: $SLURM_JOB_NODELIST

module load eb
module load freesurfer
module load fsl/5.08
module load afni

source ~/.bash_profile 
source ~/.bashrc
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

cd ~/NHP-BIDS

./code/bids_resample_isotropic_workflow.py \
    --csv ./csv/resample/SUBJECT_resample_YYYYMMDD.csv  \
    |& tee ./logs/resample/log-resample_iso-SUBJECT-YYYYMMDD.txt

./code/bids_resample_hires_isotropic_workflow.py \
    --csv ./csv/resample/SUBJECT_resample_YYYYMMDD.csv  \
    |& tee ./logs/resample/log-resample-hires_iso-SUBJECT-YYYYMMDD.txt


