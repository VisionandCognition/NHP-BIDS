#!/bin/bash

set -e

# Output to the same name as the script, but without ".sh" extension
DEST=${0:0:(-3)}
echo ${DEST}

mkdir -p ${DEST}

# Smooth Brain Mask
fslmaths 'src/manmask.nii.gz' -kernel gauss 2 -fmean "$DEST/smomask.nii.gz"
fslmaths 'src/manmask.nii.gz' -kernel gauss 1 -fmean "$DEST/smomask1.nii.gz"

# Apply Brain Mask
fslmaths src/full_func.nii.gz -mas 'src/manmask.nii.gz' "$DEST/func_brain0.nii.gz"
fslmaths src/full_func.nii.gz -mul "$DEST/smomask1.nii.gz" "$DEST/func_brain1.nii.gz"
fslmaths src/full_func.nii.gz -mul "$DEST/smomask.nii.gz" "$DEST/func_brain2.nii.gz"

for i in 2 1 0; do
  3dvolreg \
    -1Dfile "$DEST/brain-$i.1D" \
    -1Dmatrix_save "$DEST/brain-1.aff12.1D" \
    -prefix "$DEST/brain_volreg-${i}.nii.gz" \
    -maxdisp1D $DEST/brain_md-${i}.1D \
    "$DEST/func_brain${i}.nii.gz"
done
