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

# this works as of 20210528
module load 2020
module load FreeSurfer/7.1.1-centos6_x86_64
# module load FSL # causes python conflicts, use local version 
# recent afni binaries need to be manually installed in home folder for now

source ~/.bash_profile 
source ~/.bashrc
umask u+rwx,g+rwx

export FSLOUTPUTTYPE=NIFTI_GZ

SUB=MONKEY
DATE=YYYYMMDD
PROJECT=CurveTracing

echo ${SUB}-${DATE} ${PROJECT}

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
    --proj ${PROJECT} \
    --csv ./code/csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./projects/$PROJECT/logs/minproc/sub-${SUB,}/log-minproc-${SUB,}-${DATE}.txt
wait

# resample iso
./code/bids_resample_isotropic_workflow.py \
    --proj ${PROJECT} \
    --csv ./code/csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./projects/$PROJECT/logs/resample/sub-${SUB}/log-resample_iso-${SUB}-${DATE}.txt
./code/bids_resample_hires_isotropic_workflow.py \
    --proj CurveTracing \
    --csv ./code/csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./projects/$PROJECT/logs/resample/sub-${SUB,}/log-resample_iso-hires-${SUB,}-${DATE}.txt
wait


# There are 2 ways of doing preprocessing & warping: 
# 1) semi parallel (parallel slices, serial runs)
# 2) fully parallel (parallel slices and parallel runs) 
# The second method is faster but requires extra nodes on the cluster

# METHOD 1 =====
# preprocessing
./code/bids_preprocessing_workflow.py \
    --proj ${PROJECT} \
    --csv ./code/csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./projects/$PROJECT/logs/preproc/sub-${SUB,}/log-preproc-${SUB,}-${DATE}.txt

# warp to NMT
./code/bids_warp2nmt_workflow.py --csv ./code/csv/multi/${SUB}_${DATE}.csv \
    --proj ${PROJECT} \ |& \
    tee ./projects/$PROJECT/logs/warp2nmt/log-warp2nmt-${SUB}-${DATE}.txt

# METHOD 2 ====
./code/subcode/bids_preproc_parallel_runs \
    --proj ${PROJECT} \
    --csv ./code/csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv \
    --subses ${SUB}${DATE} \
 #   --no-warp 


# modelfit
# etc

## EXAMPLE ==================================================================


echo 'Reached the end of the job-file'
