#!/bin/bash
# This is the OLD copy-to-bids approach from before we adapted it for the NIN/BIDS file structure
# Use the new copy-to-bids instead


# copy this script to <SERVER>/DATA_RAW/Data_collection/Data_raw/<SUBJECT>/<SESSION>
# then run it from there

# =======================
# PARAMETERS
# =======================
SUBJECT='monkey' # no caps
SESSION='yyyymmdd'
PROJECT='Project'
# Existing projects:
# CurveTracing / PRF / FigureGround / NaturalMovie /
# HRF / Stimulation / RestingState / Tractography
# >> set to 'default' to have everything together like it used to be
# >> split up the archive manually

# =======================
# PATHS
# =======================
SERVER_ROOT=/media/NETDISKS/VS03/VS03_NHP-MRI
RAW_ROOT=${SERVER_ROOT}/DATA_RAW/Data_collection/Data_raw
BIDS_ROOT=${SERVER_ROOT}/NHP-BIDS

# =======================
# FILES
# =======================
# leave array empty if there are no such files

# STRUCTURAL ==========
# T1 ----
declare -a T1s=(\
    T1.nii.gz
    )

# T2 ----
declare -a T2s=(\
    T2.nii.gz
    )

# Fieldmap ----
declare -a fmap_mag=(\
    B0_e1a.nii.gz
    )

declare -a fmap_phase=(\
    B0_e1.nii.gz
    )

# DWI ----
declare -a DWI=(\
    DTI64.nii.gz
    )

# FUNCTIONAL ==========
# leave array empty if there are no such files

# MRI-data functional runs
declare -a funcs=( \
    xxx
    xxx
    xxx
    )

# NB corresponding array-positions (index) should correspond to files
declare -a func_runnr=( 01 02 03 ) #

# tasks: 
# curvetracing / curvetracinginccentral / ctcheckerboard 
# prf / rest / figgnd / figgndloc / checkerHRF / naturalmovie
declare -a task=( \
    xxx 
    xxx 
    xxx
    )

# Corresponding topup-scans
# when these exist there should be the same number of entries as the functional runs
# if this is not the case, duplicate rows
declare -a topup=( \
    xxx
    xxx
    xxx
    )

# behavioral log folders
declare -a behs=( \
    xxx
    xxx
    xxx
    )

# eye tracking files
declare -a eyes=( \
    xxx
    xxx 
    xxx
    )

# =======================
# FOLDER SETUP
# =======================
BIDS_srcdata=${BIDS_ROOT}/projects/${PROJECT}/data_collection
BIDS_subdata=${BIDS_ROOT}/projects/${PROJECT}/sub-${SUBJECT}/ses-${SESSION}

bsub="sub-${SUBJECT}"
bses="ses-${SESSION}"

# =======================
# COPY THE DATA
# =======================
# ANATOMICAL ===
echo "Copying anatomicals (if they exist) ---"

runnr=0
if [ ${#T1s[@]} -eq 0 ]; then
    echo 'No T1s declared'
else
    echo 'T1 scans'
    mkdir -p "${BIDS_srcdata}/anat"
    for i in "${!T1s[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${T1s[$i]} .nii.gz)
        cp -n ./MRI/${base}.nii.gz \
            "${BIDS_srcdata}/anat/${bsub}_${bses}_acq-nosense_run-${runnr}_T1w.nii.gz"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n ./MRI/${base}.json \
                "${BIDS_srcdata}/anat/${bsub}_${bses}_acq-nosense_run-${runnr}_T1w.json"
        fi
    done
fi

runnr=0
if [ ${#T2s[@]} -eq 0 ]; then
    echo 'No T2s declared'
else
    echo 'T2 scans'
    mkdir -p "${BIDS_srcdata}/anat"
    for i in "${!T2s[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${T2s[$i]} .nii.gz)
        cp -n ./MRI/${base}.nii.gz \
            "${BIDS_srcdata}/anat/${bsub}_${bses}_acq-nosense_run-${runnr}_T2w.nii.gz"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n  ./MRI/${base}.json \
                "${BIDS_srcdata}/anat/${bsub}_${bses}_acq-nosense_run-${runnr}_T2w.json"
        fi
    done
fi


# FIELDMAPS ===
echo "Copying fieldmaps (if they exist) ---"
runnr=0
if [ ${#fmap_mag[@]} -eq 0 ]; then
    echo 'No B0 magnitude files declared'
else
    echo 'Magnitude'
    mkdir -p "${BIDS_srcdata}/fmap"
    for i in "${!fmap_mag[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${fmap_mag[$i]} .nii.gz)
        cp -n ./MRI/${base}.nii.gz \
            "${BIDS_srcdata}/fmap/${bsub}_${bses}_magnitude1.nii.gz"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n  ./MRI/${base}.json \
                "${BIDS_srcdata}/fmap/${bsub}_${bses}_magnitude1.json"
        fi
    done
fi

runnr=0
if [ ${#fmap_phase[@]} -eq 0 ]; then
    echo 'No B0 phase files declared'
else
    echo 'Phase'
    mkdir -p "${BIDS_srcdata}/fmap"
    for i in "${!fmap_phase[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${fmap_phase[$i]} .nii.gz)
        cp -n ./MRI/${base}.nii.gz \
            "${BIDS_srcdata}/fmap/${bsub}_${bses}_phasediff.nii.gz"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n  ./MRI/${base}.json \
                "${BIDS_srcdata}/fmap/${bsub}_${bses}_phasediff.json"
        fi
    done
fi


# DTI ===
echo "Copying dwi (if they exist) ---"
runnr=0
if [ ${#DWI[@]} -eq 0 ]; then
    echo 'No DWI files declared'
else
    echo 'DWIs'
    mkdir -p "${BIDS_srcdata}/dwi"
    for i in "${!DWI[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${DWI[$i]} .nii.gz)
        cp -n ./MRI/${base}.nii.gz \
            "${BIDS_srcdata}/dwi/${bsub}_${bses}_run-${runnr}_dwi.nii.gz"
        cp -n ./MRI/${base}.bval \
            "${BIDS_srcdata}/dwi/${bsub}_${bses}_run-${runnr}_dwi.bval"
        cp -n ./MRI/${base}.bvec  \
            "${BIDS_srcdata}/dwi/${bsub}_${bses}_run-${runnr}_dwi.bvec"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n  ./MRI/${base}.json "${BIDS_srcdata}/dwi/${bsub}_${bses}_run-${runnr}_dwi.json"
        fi
    done
fi


# FUNCTIONALS ===
echo "Copying functionals (if they exist) ---"
if [ ${#funcs[@]} -eq 0 ]; then
    echo 'No functionals declared'
else
    echo 'EPIs'
    mkdir -p "${BIDS_srcdata}/func"
    for i in "${!funcs[@]}"; do
        base=$(basename ${funcs[$i]} .nii.gz)
        cp -n  ./MRI/${funcs[$i]} \
            "${BIDS_srcdata}/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_bold.nii.gz"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n  ./MRI/${base}.json  \
                "${BIDS_srcdata}/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_bold.json"
        fi
    done
fi

echo "Copying topups (if they exist) ---"
if [ ${#topup[@]} -eq 0 ]; then
    echo 'No TOPUPS declared'
else
    echo 'TOPUPs'
    mkdir -p "${BIDS_srcdata}/fmap"
    for i in "${!topup[@]}"; do
        base=$(basename ${topup[$i]} .nii.gz)
        cp -n  ./MRI/${topup[$i]} \
            "${BIDS_srcdata}/fmap/${bsub}_${bses}_run-${func_runnr[$i]}_epi.nii.gz"
        # if there are json files copy them too
        if [ -f ./MRI/${base}.json ]; then
            cp -n  ./MRI/${base}.json  \
                "${BIDS_srcdata}/fmap/${bsub}_${bses}_run-${func_runnr[$i]}_epi.json"
        fi
    done
fi


# BEHAVIORAL LOGS ===
echo "Copying behavioral logs (if they exist) ---"
if [ ${#behs[@]} -eq 0 ]; then
    echo 'No behavioral folders declared'
else
    echo 'Behavioral files'
    mkdir -p "${BIDS_srcdata}/func"
    for i in "${!behs[@]}"; do
        cp -n -r ./Behavior/${behs[$i]} \
            "${BIDS_srcdata}/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_events"
    done
fi

# also copy run000 is if exists << This needs to be added manually if needed
# cp -r -n ./Behavior/xxxx "${BIDS_subdata}/func/${bsub}_${bses}_task-xxx_run-00_events"


# EYE TRACES ===
echo "Copying eye data (if they exist) ---"
if [ ${#eyes[@]} -eq 0 ]; then
    echo 'No Eye files declared'
else
    echo 'Eye files'
    mkdir -p "${BIDS_subdata}/func"
    for i in "${!eyes[@]}"; do
        cp -n  Eye/${eyes[$i]} \
            "${BIDS_subdata}/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_recording-eyetrace_physio.tda"
    done
fi

