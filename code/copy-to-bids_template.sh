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
declare -a anat=( \
  NHP_20170607_EDDY_701_T1_NoSENSE_NHP_20170607140954.nii.gz \
  NHP_20170607_EDDY_1301_T1_NoSENSE_NHP_20170607140954.nii.gz \
  NHP_20170607_EDDY_1701_T1_NoSENSE_NHP_20170607140954.nii.gz \
  )
declare -a scn=( 07 13 17 ) 

mkdir -p "$BIDS_UNPROC_DEST/anat"

for i in "${!anat[@]}"; do
   cp -n MRI/NII/${anat[$i]}  "$BIDS_UNPROC_DEST/anat/${bsub}${bses}acq-nosense_scan-${scn[$i]}_T1w.nii.gz"
done

cp -n MRI/NII/NHP_20170607_EDDY_2001_T2_TRA_20170607140954.nii.gz "$BIDS_UNPROC_DEST/anat/${bsub}${bses}acq-nosense_scan-20_T2w.nii.gz"

# ==========================================================================
#    ___ _     _    _                 
#   | __(_)___| |__| |_ __  __ _ _ __ 
#   | _|| / -_) / _` | '  \/ _` | '_ \
#   |_| |_\___|_\__,_|_|_|_\__,_| .__/
#                               |_|   
# ==========================================================================
echo "Copying fieldmaps"
fmap_mag01=NHP_20170607_EDDY_401_B0_EPI_20170607140954a.nii.gz
fmap_phase01=NHP_20170607_EDDY_401_B0_EPI_20170607140954.nii.gz
scannr01=04

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
#echo "Copying dwi"
# No extensions here!
#dti01=xx
#scn01=xx

#mkdir -p "$BIDS_UNPROC_DEST/dwi/"

#cp -n MRI/NII/${dti01}.nii.gz  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn01}_dwi.nii.gz"
#cp -n MRI/NII/${dti01}.bval  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn01}_dwi.bval"
#cp -n MRI/NII/${dti01}.bvec  "$BIDS_UNPROC_DEST/dwi/${bsub}${bses}scan-${scn01}_dwi.bvec"


# ==========================================================================
#    ___             _   _               _    
#   | __|  _ _ _  __| |_(_)___ _ _  __ _| |___
#   | _| || | ' \/ _|  _| / _ \ ' \/ _` | (_-<
#   |_| \_,_|_||_\__|\__|_\___/_||_\__,_|_/__/
#                                             
# ==========================================================================
echo "Copying functionals"
declare -a funcs=( \
    NHP_20170607_EDDY_601_run002_pRF_TR2.5s_20170607140954.nii.gz \
    NHP_20170607_EDDY_801_run003_pRF_TR2.5s_20170607140954.nii.gz \
    NHP_20170607_EDDY_1001_run005_pRF_TR2.5s_20170607140954.nii.gz \
    NHP_20170607_EDDY_1401_run008_pRF_TR2.5s_20170607140954.nii.gz \
    NHP_20170607_EDDY_1501_run009_pRF_TR2.5s_20170607140954.nii.gz \
    NHP_20170607_EDDY_1601_run010_pRF_TR2.5s_20170607140954.nii.gz \
    )
declare -a runnr=( 02 03 05 08 09 10 )
declare -a task=( prf curvetraving ctcheckerboard)
mkdir -p "$BIDS_UNPROC_DEST/func"

## now loop through the above array
for i in "${!funcs[@]}"; do
   cp -n  MRI/NII/${funcs[$i]} "$BIDS_UNPROC_DEST/func/${bsub}${bses}task-${task[$i]}_run-${runnr[$i]}_bold.nii.gz"
done

# Copy top-up [not present for Danny's prf scans]
# cp -n MRI/NII/NHP_20180125_EDDY_20180125_601_run002_CurveTrace_TR2.5s_Topup_20180125101154.nii.gz "$BIDS_UNPROC_DEST/fmap/${bsub}${bses}_run-02_epi.nii.gz"
# cp -n MRI/NII/NHP_20180125_EDDY_20180125_901_run004_CurveTrace_TR2.5s_Topup_20180125101154.nii.gz "$BIDS_UNPROC_DEST/fmap/${bsub}${bses}_run-04_epi.nii.gz"

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
    Eddy_StimSettings_pRF_8bars_3T_TR2500ms_20170607T1445 \
    Eddy_StimSettings_pRF_8bars_3T_TR2500ms_20170607T1503 \
    Eddy_StimSettings_pRF_8bars_3T_TR2500ms_20170607T1519 \
    Eddy_StimSettings_pRF_8bars_3T_TR2500ms_20170607T1542 \
    Eddy_StimSettings_pRF_8bars_3T_TR2500ms_20170607T1552 \
    Eddy_StimSettings_pRF_8bars_3T_TR2500ms_20170607T1601 \
    )

mkdir -p "$BIDS_UNPROC_DEST/func"

for i in "${!behs[@]}"; do
   cp -r -n Behavior/${behs[$i]}/ "$BIDS_UNPROC_DEST/func/${bsub}${bses}task-${task[$i]}_run-${runnr[$i]}_events"
done

# also copy run000 is if exists
cp -r -n Behavior/Eddy_Curve_Tracing_StimSettings_CurveMapping_Spinoza_3T_20170607T1425-T1444.24/ "$BIDS_UNPROC_DEST/func/${bsub}${bses}task-prf_run-00_events"

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
    Eddy_20170607T1445.tda \
    Eddy_20170607T1503.tda \
    Eddy_20170607T1519.tda \
    Eddy_20170607T1542.tda \
    Eddy_20170607T1552.tda \
    Eddy_20170607T1601.tda \
    )

mkdir -p "$BIDS_DEST/func"

for i in "${!eyes[@]}" ; do
   cp -n Eye/${eyes[$i]} "$BIDS_DEST/func/${bsub}${bses}task-${task[$i]}_run-${runnr[$i]}_recording-eyetrace_physio.tda"
done

