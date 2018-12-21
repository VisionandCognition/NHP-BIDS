#SBATCH -S /bin/bash
#SBATCH -N 1 --ntasks-per-node=16
#SBATCH -t 24:00:00

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

cd NHP-BIDS

#SBATCH --mail-type=END
#SBATCH --mail-user=p.c.klink@gmail.com