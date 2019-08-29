#!/bin/bash

SCRIPT_PATH="`dirname \"$0\"`"              # relative
SCRIPT_PATH="`( cd \"$SCRIPT_PATH\" && pwd )`"  # absolutized and normalized
if [ -z "$SCRIPT_PATH" ] ; then
  # error; for some reason, the path is not accessible
  # to the script (e.g. permissions re-evaled after suid)
  exit 1  # fail
fi

# First copy raw files into the BIDS "sourcedata" directory. Files will
# then be minimally processed for conversion to BIDS.

# This is just some script-fu to automatically create name of destination,
# so that the same base script can be used for multiple directories.
BIDS_DEST=$SCRIPT_PATH
BIDS_DEST="${BIDS_DEST/Data_raw/NHP-BIDS}"
BIDS_DEST="${BIDS_DEST/EDDY/sub-eddy}"
BIDS_DEST="${BIDS_DEST/DANNY/sub-danny}"
BIDS_DEST="${BIDS_DEST/SPIKE/sub-spike}"
BIDS_DEST="${BIDS_DEST/2016/ses-2016}"
BIDS_DEST="${BIDS_DEST/2017/ses-2017}"
BIDS_DEST="${BIDS_DEST/2018/ses-2018}"
BIDS_DEST="${BIDS_DEST/2019/ses-2019}"

BIDS_UNPROC_DEST="${BIDS_DEST/NHP-BIDS/NHP-BIDS/sourcedata}"

echo "Copying BIDS data to $BIDS_DEST and $BIDS_UNPROC_DEST..."

date=$(basename $(pwd))
SUBJ=$(basename $(dirname $(pwd)))
subj=$(echo $SUBJ | tr '[:upper:]' '[:lower:]')

bsub="sub-${subj}_"
bses="ses-${date}_"

# ==========================================================================
#      _             _             _         _ 
#     /_\  _ _  __ _| |_ ___ _ __ (_)__ __ _| |
#    / _ \| ' \/ _` |  _/ _ \ '  \| / _/ _` | |
#   /_/ \_\_||_\__,_|\__\___/_|_|_|_\__\__,_|_|
#                                              
# ==========================================================================
echo "Copying anatomicals"

mkdir -p "$BIDS_UNPROC_DEST/anat"

cp -n MRI/NII/T1_NoSENSE_NHP_20190213141308_501.nii.gz \
    "$BIDS_UNPROC_DEST/anat/${bsub}${bses}acq-nosense_scan-05_T1w.nii.gz"
cp -n MRI/NII/WIP_T2_TRA_20190213141308_1301.nii.gz \
    "$BIDS_UNPROC_DEST/anat/${bsub}${bses}acq-nosense_scan-13_T2w.nii.gz"
cp -n MRI/NII/WIP_T2_TRA_20190213141308_2901.nii.gz \
    "$BIDS_UNPROC_DEST/anat/${bsub}${bses}acq-nosense_scan-29_T2w.nii.gz"
cp -n MRI/NII/WIP_T2_TRA_20190213141308_3001.nii.gz \
    "$BIDS_UNPROC_DEST/anat/${bsub}${bses}acq-nosense_scan-30_T2w.nii.gz"

# ==========================================================================
#    ___ _     _    _                 
#   | __(_)___| |__| |_ __  __ _ _ __ 
#   | _|| / -_) / _` | '  \/ _` | '_ \
#   |_| |_\___|_\__,_|_|_|_\__,_| .__/
#                               |_|   
# ==========================================================================
echo "Copying fieldmaps"
fmap_mag01=B0_EPI_20190213141308_2801_e1a.nii.gz
fmap_phase01=B0_EPI_20190213141308_2801_e1.nii.gz
scannr01=28

mkdir -p "$BIDS_UNPROC_DEST/fmap/"
cp -n MRI/NII/$fmap_mag01 "$BIDS_UNPROC_DEST/fmap/${bsub}${bses}magnitude1.nii.gz"
cp -n MRI/NII/$fmap_phase01 "$BIDS_UNPROC_DEST/fmap/${bsub}${bses}phasediff.nii.gz"


# ==========================================================================
#    ___ _____ ___ 
#   |   \_   _|_ _|
#   | |) || |  | | 
#   |___/ |_| |___|
#                
# ==========================================================================
echo "Copying dwi"
# No extensions here!
dti01=DTI64_20190213141308_2301
scn01=23
dti02=DTI64_20190213141308_3101
scn02=31

mkdir -p "$BIDS_UNPROC_DEST/dwi/"

cp -n MRI/NII/${dti01}.nii.gz  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn01}_dwi.nii.gz"
cp -n MRI/NII/${dti01}.bval  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn01}_dwi.bval"
cp -n MRI/NII/${dti01}.bvec  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn01}_dwi.bvec"

cp -n MRI/NII/${dti02}.nii.gz  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn02}_dwi.nii.gz"
cp -n MRI/NII/${dti02}.bval  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn02}_dwi.bval"
cp -n MRI/NII/${dti02}.bvec  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn02}_dwi.bvec"

# ==========================================================================
#    ___             _   _               _    
#   | __|  _ _ _  __| |_(_)___ _ _  __ _| |___
#   | _| || | ' \/ _|  _| / _ \ ' \/ _` | (_-<
#   |_| \_,_|_||_\__|\__|_\___/_||_\__,_|_/__/
#                                             
# ==========================================================================
echo "Copying functionals"
declare -a funcs=( \
    run001_CurveTrace_TR2.5s_20190213141308_301.nii.gz \
    run002_CurveTrace_TR2.5s_20190213141308_601.nii.gz \
    run003_CurveTrace_TR2.5s_20190213141308_801.nii.gz \
    run004_CurveTrace_TR2.5s_20190213141308_1001.nii.gz \
    run005_CurveTrace_TR2.5s_20190213141308_1101.nii.gz \
    run006_CurveTrace_TR2.5s_20190213141308_1401.nii.gz \
    run007_CurveTrace_TR2.5s_20190213141308_1601.nii.gz \
    run008_CurveTrace_TR2.5s_20190213141308_1801.nii.gz \
    run009_CurveTrace_TR2.5s_20190213141308_2101.nii.gz \
    run010_CurveTrace_TR2.5s_20190213141308_2401.nii.gz \
    run011_CurveTrace_TR2.5s_20190213141308_2601.nii.gz \
    )
declare -a runnr=( 01 02 03 04 05 06 07 08 09 10 11 )
declare -a task=( \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    curvetracing \
    )

mkdir -p "$BIDS_UNPROC_DEST/func"

## now loop through the above array
for i in "${!funcs[@]}"; do
   cp -n  MRI/NII/${funcs[$i]} "$BIDS_UNPROC_DEST/func/${bsub}${bses}task-${task[$i]}run-${runnr[$i]}_bold.nii.gz"
done

echo "Copying topups"
# Copy top-up [not present for Danny's prf scans]
declare -a topup=( \
    run001_topup_20190213141308_401.json \
    run002_topup_20190213141308_701.nii.gz \
    run003_topup_20190213141308_901.nii.gz \
    run005_topup_20190213141308_1201.nii.gz \
    run006_topup_20190213141308_1501.nii.gz \
    run007_topup_20190213141308_1701.nii.gz \
    run008_topup_20190213141308_1901.nii.gz \
    run009_topup_20190213141308_2201.nii.gz \
    run010_topup_20190213141308_2501.nii.gz \
    run011_topup_20190213141308_2701.nii.gz \
    )

## now loop through the above array
for i in "${!topup[@]}"; do
  cp -n  MRI/NII/${topup[$i]} "$BIDS_UNPROC_DEST/fmap/${bsub}${bses}_run-${runnr[$i]}_epi.nii.gz"
done


# ==========================================================================
#   ___      _             _           _              
#  | _ ) ___| |_  __ ___ _(_)___ _ _  | |___  __ _ ___
#  | _ \/ -_) ' \/ _` \ V / / _ \ '_| | / _ \/ _` (_-<
#  |___/\___|_||_\__,_|\_/|_\___/_|   |_\___/\__, /__/
#                                            |___/ 
# Copy behavior logs
# ls -1 Behavior
# ==========================================================================
echo "Copying behavioral logs"
declare -a behs=( \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1432-T1442.50 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1450-T1501.48 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1503-T1512.55 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1514-T1515.53 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1516-T1526.29 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1532-T1542.27 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1543-T1554.36 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1555-T1606.36 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1607-T1619.00 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1630-T1641.06 \
    Danny_Curve_Tracing_StimSettings_3T_Spinoza_3T_20190213T1642-T1653.46 \
    )

mkdir -p "$BIDS_UNPROC_DEST/func"

for i in "${!behs[@]}"; do
   cp -r -n Behavior/${behs[$i]}/ "$BIDS_UNPROC_DEST/func/${bsub}${bses}task-${task[$i]}_run-${runnr[$i]}_events"
done

# also copy run000 is if exists
# cp -r -n Behavior/Eddy_Curve_Tracing_StimSettings_CurveMapping_Spinoza_3T_20170607T1425-T1444.24/ "$BIDS_UNPROC_DEST/func/${bsub}${bses}task-prf_run-00_events"

# ==========================================================================
#   ___           _                      
#  | __|  _ ___  | |_ _ _ __ _ __ ___ ___
#  | _| || / -_) |  _| '_/ _` / _/ -_|_-<
#  |___\_, \___|  \__|_| \__,_\__\___/__/
#      |__/    
# ls -1 Eye
# ==========================================================================
echo "Copying eye data"
declare -a eyes=( \
    Danny_20190213T1432.tda \
    Danny_20190213T1450.tda \
    Danny_20190213T1503.tda \
    Danny_20190213T1514.tda \
    Danny_20190213T1516.tda \
    Danny_20190213T1532.tda \
    Danny_20190213T1543.tda \
    Danny_20190213T1555.tda \
    Danny_20190213T1607.tda \
    Danny_20190213T1630.tda \
    Danny_20190213T1642.tda \
    )

mkdir -p "$BIDS_DEST/func"

for i in "${!eyes[@]}" ; do
   cp -n Eye/${eyes[$i]} "$BIDS_DEST/func/${bsub}${bses}task-${task[$i]}_run-${runnr[$i]}_recording-eyetrace_physio.tda"
done

