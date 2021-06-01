#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 01:00:00
#SBATCH --mail-type=END
#SBATCH --mail-user=p.c.klink@gmail.com

echo job id $SLURM_JOBID
echo job name $SLURM_JOB_NAME
echo submitted by $mail-user
echo from $SLURM_SUBMIT_DIR
echo the allocated nodes are:
cat $SLURM_JOB_NODELIST

module load eb
module load freesurfer
module load fsl/5.08
module load afni

source ~/.bash_profile 
source ~/.bashrc

export FSLOUTPUTTYPE=NIFTI_GZ

cd ~/NHP-BIDS

# minimal processing
#./code/bids_minimal_processing.py --csv ./csv/minproc/Danny_minproc_20181212.csv  |& tee ./logs/minproc/log-minproc-danny-20181212.txt
# resample iso
./code/resample_isotropic_workflow.py --csv ./csv/preproc/Danny_preproc_20181212.csv  |& tee #./logs/resample/sub-danny/log-resample_iso-danny-20181212.txt
./code/resample_hires_isotropic_workflow.py --csv ./csv/preproc/Danny_preproc_20181212.csv  |& tee ./logs/resample/sub-danny/log-resample_iso-hires--danny-20181212.txt
# preprocessing
#./code/preprocessing_workflow_danny.py --csv ./csv/preproc/Danny_preproc_20181212.csv  |& tee ./logs/preproc/sub-danny/log-preproc-danny-20181212_modelfit.txt
# modelfit

