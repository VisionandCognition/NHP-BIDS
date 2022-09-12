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
DATE=20191211

echo ${SUB}-${DATE}

cd ~/NHP-BIDS
# minimal processing
./code/bids_minimal_processing.py --csv ./csv/multi/${SUB}_${DATE}.csv  |& \
    tee ./logs/minproc/log-minproc-${SUB}-${DATE}.txt
wait

# resample iso
./code/bids_resample_isotropic_workflow.py --csv ./csv/multi/${SUB}_${DATE}.csv  |& \
    tee ./logs/resample/sub-${SUB}/log-resample_iso-${SUB}-${DATE}.txt
./code/bids_resample_hires_isotropic_workflow.py --csv ./csv/multi/${SUB}_${DATE}.csv  |& \
    tee ./logs/resample/sub-${SUB}/log-resample_iso-hires-${SUB}-${DATE}.txt
wait

# preprocessing << wait with this, we need to fix the issues first
#./code/bids_preprocessing_workflow.py --csv ./csv/multi/${SUB}_${DATE}.csv  |& \
#    tee ./logs/preproc/sub-${SUB}/log-preproc-${SUB}-${DATE}.txt

# modelfit

echo 'Reached the end of the job-file'
