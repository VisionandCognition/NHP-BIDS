#!/bin/bash

set -e

# Output to the same name as the script, but without ".sh" extension
DEST=${0:0:(-3)}
echo ${DEST}
SRC='src'

mkdir -p ${DEST}

# Apply Brain Mask
# fslmaths src/full_func.nii.gz -mas 'src/manmask.nii.gz' "$DEST/func_brain0.nii.gz"

align_epi_anat.py

# shift_rotate_scale is noticeably worse than affine_general
for trans in shift_rotate_scale affine_general; do
  i=1
  3dWarpDrive \
      "-$trans" \
      -twopass \
      -cubic -final quintic \
      -1Dfile "$DEST/brain-$i_$trans.1D" \
      -1Dmatrix_save "$DEST/brain-$i.aff12_$trans.1D" \
      -prefix "$DEST/brain_volreg-${i}_$trans.nii.gz" \
      -weight "$SRC/manmask_weights.nii.gz[0]" \
      -base "$SRC/manmask_reference.nii.gz[0]" \
      "$SRC/full_func.nii.gz"

  i=2
  3dWarpDrive \
      "-$trans" \
      -twopass \
      -cubic -final quintic \
      -1Dfile "$DEST/brain-$i_$trans.1D" \
      -1Dmatrix_save "$DEST/brain-$i.aff12_$trans.1D" \
      -prefix "$DEST/brain_volreg-${i}_$trans.nii.gz" \
      -weight "$SRC/manmask_weights$i.nii.gz[0]" \
      -base "$SRC/manmask_reference.nii.gz[0]" \
      "$SRC/full_func.nii.gz"
done
