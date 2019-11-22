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

# ==== the module environment on LISA changes on 1 October 2019 ====
# more info: https://userinfo.surfsara.nl/documentation/new-module-environment-lisa-cartesius
# module load 2019 # use the new environment and modules
# module load pre2019 # use old environment 
# >> only use pre2019 if you need software modules that aren't present in 2019
# >> currently, none of the neuroimaging modules have been ported
# >> stick with pre2019 for now
# ============================================================================

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

SUB=MONKEY
DATE=YYYYMMDD

echo ${SUB}-${DATE}

cd ~/NHP-BIDS

# tasks to be executed 1
wait
# tasks to be executed 2
wait
# tasks to be executed 3
wait


## EXAMPLE ==================================================================

# minimal processing
./code/bids_minimal_processing.py \
    --csv ./csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./logs/minproc/sub-${SUB,}/log-minproc-${SUB,}-${DATE}.txt
wait

# resample iso
./code/bids_resample_isotropic_workflow.py \
    --csv ./csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./logs/resample/sub-${SUB}/log-resample_iso-${SUB}-${DATE}.txt
./code/bids_resample_hires_isotropic_workflow.py \
    --csv ./csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./logs/resample/sub-${SUB,}/log-resample_iso-hires-${SUB,}-${DATE}.txt
wait

# preprocessing
./code/bids_preprocessing_workflow.py \
    --csv ./csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./logs/preproc/sub-${SUB,}/log-preproc-${SUB,}-${DATE}.txt

# modelfit
# etc

## EXAMPLE ==================================================================


echo 'Reached the end of the job-file'
