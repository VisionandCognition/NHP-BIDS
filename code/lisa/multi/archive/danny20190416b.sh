#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 72:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=p.c.klink@gmail.com

echo job id $SLURM_JOBID
echo job name $SLURM_JOB_NAME
echo submitted by $SLURM_JOB_ACCOUNT
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

# minimal processing
#./code/bids_minimal_processing.py --csv ./csv/multi/Danny_20190416b.csv --types func --ignore_events |& \
#    tee ./logs/minproc/log-minproc-danny-20190416b.txt
#wait

# resample iso
#./code/resample_isotropic_workflow.py --csv ./csv/multi/Danny_20190416b.csv  |& \
#    tee ./logs/resample/sub-danny/log-resample_iso-danny-20190416b.txt
#wait

# preprocessing
./code/preprocessing_workflow_danny.py --csv ./csv/multi/Danny_20190416b.csv  |& \
    tee ./logs/preproc/sub-danny/log-preproc-danny-20190416b.txt

# modelfit

