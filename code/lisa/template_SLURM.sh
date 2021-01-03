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
# module load 2019 # use the new environment and modules (default, so not explicitly necessary)
# module load pre2019 # use old environment 
# >> only use pre2019 if you need software modules that aren't present in 2019
# >> [2019] currently, none of the neuroimaging modules have been ported
# >> stick with pre2019 for now

# >> [20200715] The 2019 environment now has FSL and FreeSurfer
# >> I applied for afni and ANTS to get installed as well.
# >> We can run 2019 but need to run afni from home folder for now
# ============================================================================

##  This is the pre2019 setup
# module load surf-devel
# module load pre2019
# module load eb
# module load freesurfer
# module load fsl/5.08
# module load afni

## This is the 2019/default setup
module load 2019
module load FreeSurfer
module load FSL
module load AFNI
# recent afni binaries need to be manually installed in home folder for now

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


# There are 2 ways of doing preprocessing & warping: 
# 1) semi parallel (parallel slices, serial runs)
# 2) fully parallel (parallel slices and parallel runs) 
# The second method is faster but requires extra nodes on the cluster

# METHOD 1 =====
# preprocessing
./code/bids_preprocessing_workflow.py \
    --csv ./csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv  |& \
    tee ./logs/preproc/sub-${SUB,}/log-preproc-${SUB,}-${DATE}.txt

# warp to NMT
./code/bids_warp2nmt_workflow.py --csv ./csv/multi/${SUB}_${DATE}.csv  |& \
    tee ./logs/warp2nmt/log-warp2nmt-${SUB}-${DATE}.txt

# METHOD 2
./code/subcode/bids_preproc_parallel_runs \
    --csv ./csv/multi/sub-${SUB,}/${SUB,}_${DATE}.csv \
    --subses ${SUB}${DATE} \
 #   --no-warp 


# modelfit
# etc

## EXAMPLE ==================================================================


echo 'Reached the end of the job-file'
