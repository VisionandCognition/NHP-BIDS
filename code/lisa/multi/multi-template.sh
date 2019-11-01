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

# module load surf-devel
module load pre2019

module load eb
module load freesurfer
module load fsl/5.08
module load afni

source ~/.bash_profile 
source ~/.bashrc
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

cd ~/NHP-BIDS


# minimal processing
./code/bids_minimal_processing.py --csv ./csv/multi/SUBJECT_YYYYMMDD.csv |& \
    tee ./logs/minproc/log-minproc-SUBJECT_YYYYMMDD.txt
wait


# resample iso
./code/bids_resample_isotropic_workflow.py --csv ./csv/multi/SUBJECT_YYYYMMDD.csv  |& \
    tee ./logs/resample/sub-danny/log-resample_iso-SUBJECT_YYYYMMDD.txt
./code/bids_resample_hires_isotropic_workflow.py --csv ./csv/multi/SUBJECT_YYYYMMDD.csv  |& \
    tee ./logs/resample/sub-danny/log-resample_iso-hires-SUBJECT_YYYYMMDD.txt
wait


# preprocessing
./code/bids_preprocessing_workflow_danny.py --csv ./csv/multi/SUBJECT_YYYYMMDD.csv  |& \
    tee ./logs/preproc/sub-danny/log-preproc-SUBJECT_YYYYMMDD.txt


# modelfit

