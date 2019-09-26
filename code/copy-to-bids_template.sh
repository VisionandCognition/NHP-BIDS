#!/bin/bash

# ==========================================================================
#  ___ _ _        
# | __(_) |___ ___
# | _|| | / -_|_-<
# |_| |_|_\___/__/
#                 
# ==========================================================================

# NB! This should be the only area where you need to make changes ----
# files with get run numbers in the order they are in the array
# for functionals (+ beh/eye), run numbers should be explixitly defined

# ==========================================================================
# STRUCTURAL
# ==========================================================================
# leave array empty if there are no such files

# T1 ----
declare -a T1s=(\
    T1_NoSENSE_NHP_20190213141308_501.nii.gz
    )

# T2 ----
declare -a T2s=(\
    T2_TRA_20190213141308_1301.nii.gz
    )

# Fieldmap ----
declare -a fmap_mag=(\
    B0_EPI_20190213141308_2801_e1a.nii.gz
    )

declare -a fmap_phase=(\
    B0_EPI_20190213141308_2801_e1.nii.gz
    )

# DWI ----
declare -a DWI=(\
    DTI64_20190213141308_2301.nii.gz
    )

# ==========================================================================
# FUNCTIONAL
# ==========================================================================
# leave array empty if there are no such files

# NB corresponding array-positions should correspond!
declare -a func_runnr=( 01 02 03 )
# tasks: 
# curvetracing / curvetracinginccentral / ctcheckerboard 
# prf /rest / figgnd / figgndloc / checkerHRF / naturalmovie
declare -a task=( \
    curvetracing \
    curvetracing \
    curvetracing \
    )
# MRI-data functional runs
declare -a funcs=( \
    run001_CurveTrace_TR2.5s_20190213141308_301.nii.gz \
    run002_CurveTrace_TR2.5s_20190213141308_601.nii.gz \
    run003_CurveTrace_TR2.5s_20190213141308_801.nii.gz \
    )
# Corresponding topup-scans
# when these exist there should be the same number of entries as the functional runs
declare -a topup=( \
    run001_topup_20190213141308_401.json \
    run002_topup_20190213141308_701.nii.gz \
    run003_topup_20190213141308_901.nii.gz \
    )
# behavioral log folders
declare -a behs=( \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1432-T1442.50 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1450-T1501.48 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1503-T1512.55 \
    )
# eye tracking files
declare -a eyes=( \
    Danny_20190213T1432.tda \
    Danny_20190213T1450.tda \
    Danny_20190213T1503.tda \
    )


# ==========================================================================
#  ___    _    _                   _             
# | __|__| |__| |___ _ _   ___ ___| |_ _  _ _ __ 
# | _/ _ \ / _` / -_) '_| (_-</ -_)  _| || | '_ \
# |_|\___/_\__,_\___|_|   /__/\___|\__|\_,_| .__/
#                                          |_|   
# ==========================================================================

# check if we have the right permissions ----
SCRIPT_PATH="`dirname \"$0\"`"                  # relative
SCRIPT_PATH="`( cd \"$SCRIPT_PATH\" && pwd )`"  # absolutized and normalized
if [ -z "$SCRIPT_PATH" ] ; then
  exit 1  # fail
fi

# local path ----
BIDS_DEST=$SCRIPT_PATH
# raw to BIDS ----
BIDS_DEST="${BIDS_DEST/Data_raw/NHP-BIDS}"
# subjects ----
BIDS_DEST="${BIDS_DEST/EDDY/sub-eddy}"
BIDS_DEST="${BIDS_DEST/DANNY/sub-danny}"
BIDS_DEST="${BIDS_DEST/SPIKE/sub-spike}"
# sessions ----
BIDS_DEST="${BIDS_DEST/2016/ses-2016}"
BIDS_DEST="${BIDS_DEST/2017/ses-2017}"
BIDS_DEST="${BIDS_DEST/2018/ses-2018}"
BIDS_DEST="${BIDS_DEST/2019/ses-2019}"
BIDS_DEST="${BIDS_DEST/2019/ses-2019}"
# sourcedata ----
BIDS_UNPROC_DEST="${BIDS_DEST/NHP-BIDS/NHP-BIDS/sourcedata}"

# some feedback to terminal ----
echo "Copying BIDS data to $BIDS_DEST and $BIDS_UNPROC_DEST..."

# create some useful variables ----
date=$(basename $(pwd))
SUBJ=$(basename $(dirname $(pwd)))
subj=$(echo $SUBJ | tr '[:upper:]' '[:lower:]')
bsub="sub-${subj}"
bses="ses-${date}"


# ==========================================================================
#      _             _             _         _ 
#     /_\  _ _  __ _| |_ ___ _ __ (_)__ __ _| |
#    / _ \| ' \/ _` |  _/ _ \ '  \| / _/ _` | |
#   /_/ \_\_||_\__,_|\__\___/_|_|_|_\__\__,_|_|
#                                              
# ==========================================================================

echo "Copying anatomicals (if they exist)"
runnr=0
if [ ${#T1s[@]} -eq 0 ]; then
    echo 'T1 scans'
    mkdir -p "$BIDS_UNPROC_DEST/anat"
    for i in "${!T1s[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${T1s[$i]} .nii.gz)
        cp -n MRI/NII/${base}.nii.gz "$BIDS_UNPROC_DEST/anat/${bsub}_${bses}_acq-nosense_run-${runnr[$i]}_T1w.nii.gz"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n MRI/NII/${base}.json "$BIDS_UNPROC_DEST/anat/${bsub}_${bses}_acq-nosense_run-${runnr[$i]}_T1w.json"
        fi
    done
fi

runnr=0
if [ ${#T2s[@]} -eq 0 ]; then
    echo 'T2 scans'
    mkdir -p "$BIDS_UNPROC_DEST/anat"
    for i in "${!T2s[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${T2s[$i]} .nii.gz)
        cp -n MRI/NII/${base}.nii.gz "$BIDS_UNPROC_DEST/anat/${bsub}_${bses}_acq-nosense_run-${runnr[$i]}_T2w.nii.gz"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n  MRI/NII/${base}.json "$BIDS_UNPROC_DEST/anat/${bsub}_${bses}_acq-nosense_run-${runnr[$i]}_T2w.json"
        fi
    done
fi


# ==========================================================================
#    ___ _     _    _                 
#   | __(_)___| |__| |_ __  __ _ _ __ 
#   | _|| / -_) / _` | '  \/ _` | '_ \
#   |_| |_\___|_\__,_|_|_|_\__,_| .__/
#                               |_|   
# ==========================================================================

echo "Copying fieldmaps (if they exist)"
runnr=0
if [ ${#fmap_mag[@]} -eq 0 ]; then
    echo 'Magnitude'
    mkdir -p "$BIDS_UNPROC_DEST/fmap"
    for i in "${!fmap_mag[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${fmap_mag[$i]} .nii.gz)
        cp -n MRI/NII/${base}.nii.gz "$BIDS_UNPROC_DEST/fmap/${bsub}_${bses}_magnitude1.nii.gz"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n  MRI/NII/${base}.json "$BIDS_UNPROC_DEST/fmap/${bsub}_${bses}_magnitude1.json"
        fi
    done
fi

runnr=0
if [ ${#fmap_phase[@]} -eq 0 ]; then
    echo 'Magnitude'
    mkdir -p "$BIDS_UNPROC_DEST/fmap"
    for i in "${!fmap_phase[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${fmap_phase[$i]} .nii.gz)
        cp -n MRI/NII/${base}.nii.gz "$BIDS_UNPROC_DEST/fmap/${bsub}_${bses}_phasediff.nii.gz"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n  MRI/NII/${base}.json "$BIDS_UNPROC_DEST/fmap/${bsub}_${bses}_phasediff.json"
        fi
    done
fi


# ==========================================================================
#    ___ _____ ___ 
#   |   \_   _|_ _|
#   | |) || |  | | 
#   |___/ |_| |___|
#                
# ==========================================================================

echo "Copying dwi (if they exist)"
runnr=0
if [ ${#DWI[@]} -eq 0 ]; then
    mkdir -p "$BIDS_UNPROC_DEST/dwi"
    for i in "${!DWI[@]}"; do
        runnr=$((runnr + 1))
        base=$(basename ${DWI[$i]} .nii.gz)
        cp -n MRI/NII/${base}.nii.gz "$BIDS_UNPROC_DEST/dwi/${bsub}_${bses}_run-${runnr}_dwi.nii.gz"
        cp -n MRI/NII/${base}.bval  "$BIDS_UNPROC_DEST/dwi/${bsub}_${bses}_run-${runnr}_dwi.bval"
        cp -n MRI/NII/${base}.bvec  "$BIDS_UNPROC_DEST/dwi/${bsub}_${bses}_run-${runnr}_dwi.bvec"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n  MRI/NII/${base}.json "$BIDS_UNPROC_DEST/dwi/${bsub}_${bses}_run-${runnr}_dwi.json"
        fi
    done
fi


# ==========================================================================
#    ___             _   _               _    
#   | __|  _ _ _  __| |_(_)___ _ _  __ _| |___
#   | _| || | ' \/ _|  _| / _ \ ' \/ _` | (_-<
#   |_| \_,_|_||_\__|\__|_\___/_||_\__,_|_/__/
#                                             
# ==========================================================================

echo "Copying functionals (if they exist)"
if [ ${#funcs[@]} -eq 0 ]; then
    mkdir -p "$BIDS_UNPROC_DEST/func"
    for i in "${!funcs[@]}"; do
        base=$(basename ${funcs[$i]} .nii.gz)
        cp -n  MRI/NII/${funcs[$i]} \
            "$BIDS_UNPROC_DEST/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_bold.nii.gz"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n  MRI/NII/${base}.json  \
                "$BIDS_UNPROC_DEST/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_bold.json"
        fi
done


echo "Copying topups (if they exist)"
if [ ${#topup[@]} -eq 0 ]; then
    mkdir -p "$BIDS_UNPROC_DEST/fmap"
    for i in "${!topup[@]}"; do
        base=$(basename ${topup[$i]} .nii.gz)
        cp -n  MRI/NII/${topup[$i]} \
            "$BIDS_UNPROC_DEST/fmap/${bsub}_${bses}_run-${func_runnr[$i]}_epi.nii.gz"
        # if there are json files copy them too
        if [ -f MRI/NII/${base}.json]; then
            cp -n  MRI/NII/${base}.json  \
                "$BIDS_UNPROC_DEST/fmap/${bsub}_${bses}_run-${func_runnr[$i]}_epi.json"
        fi
done


# ==========================================================================
#   ___      _             _           _              
#  | _ ) ___| |_  __ ___ _(_)___ _ _  | |___  __ _ ___
#  | _ \/ -_) ' \/ _` \ V / / _ \ '_| | / _ \/ _` (_-<
#  |___/\___|_||_\__,_|\_/|_\___/_|   |_\___/\__, /__/
#                                            |___/ 
# ==========================================================================

echo "Copying behavioral logs (if they exist)"
if [ ${#behs[@]} -eq 0 ]; then
    mkdir -p "$BIDS_UNPROC_DEST/func"
    for i in "${!behs[@]}"; do
        cp -n  Behavior/${behs[$i]} \
            "$BIDS_UNPROC_DEST/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_events"
done

# also copy run000 is if exists << This needs to be added manually if needed
# cp -r -n Behavior/xxxx "$BIDS_UNPROC_DEST/func/${bsub}_${bses}_task-xxx_run-00_events"


# ==========================================================================
#   ___           _                      
#  | __|  _ ___  | |_ _ _ __ _ __ ___ ___
#  | _| || / -_) |  _| '_/ _` / _/ -_|_-<
#  |___\_, \___|  \__|_| \__,_\__\___/__/
#      |__/    
# 
# ==========================================================================

echo "Copying eye data (if they exist)"
if [ ${#eyes[@]} -eq 0 ]; then
    mkdir -p "$BIDS_UNPROC_DEST/func"
    for i in "${!eyes[@]}"; do
        cp -n  Eye/${eyes[$i]} \
            "$BIDS_UNPROC_DEST/func/${bsub}_${bses}_task-${task[$i]}_run-${func_runnr[$i]}_recording-eyetrace_physio.tda"
done