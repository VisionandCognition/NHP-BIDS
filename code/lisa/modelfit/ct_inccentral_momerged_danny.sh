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

module load 2020
module load FreeSurfer

source ~/.bash_profile 
source ~/.bashrc
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

cd ~/NHP-BIDS

# ct-inccentral / merged mo
./code/bids_modelfit_level1_workflow.py \
    --csv ./csv/ct/sub-danny/lev1/ct_lev1_danny.csv  \
    --hrf ./code/hrf/HRF-monkey.txt \
    --MotionOutliers merged \
    --contrasts ct-inccentral \
    --resultfld ctinccentral_nmt_level1_ud_momerged_danny \
    |& tee ./logs/lev1/ctinccentral_nmt_level1_ud_momerged_danny.txt
wait 


# modelfit
echo 'Reached the end of the job-file'
