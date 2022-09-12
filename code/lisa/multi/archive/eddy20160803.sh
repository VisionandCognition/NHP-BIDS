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

module load surf-devel
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
#./code/bids_minimal_processing.py --csv ./csv/multi/Eddy_20160803.csv --ignore_events |& \
#    tee ./logs/minproc/log-minproc-eddy-20160803.txt
#wait

# resample iso
#./code/bids_resample_isotropic_workflow.py --csv ./csv/multi/Eddy_20160803.csv  |& \
#    tee ./logs/resample/sub-eddy/log-resample_iso-eddy-20160803.txt
#./code/bids_resample_hires_isotropic_workflow.py --csv ./csv/multi/Eddy_20160803.csv  |& \
#    tee ./logs/resample/sub-eddy/log-resample_iso-hires-eddy-20160803.txt
#wait

# preprocessing
./code/bids_preprocessing_workflow.py --csv ./csv/multi/Eddy_20160803.csv  |& \
    tee ./logs/preproc/sub-eddy/log-preproc-eddy-20160803.txt

# modelfit

