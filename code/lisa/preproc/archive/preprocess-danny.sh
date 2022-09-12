#!/bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 36:00:00
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
./code/preprocessing_workflow_danny.py \
	--csv ./csv/prf-danny-nodti.csv |& tee ./logs/log-preproc_danny_nodti.txt
./code/preprocessing_workflow_danny.py \
	--csv ./csv/prf-danny-dti.csv |& tee ./logs/log-preproc_danny_dti.txt