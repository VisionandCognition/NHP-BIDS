#!/bin/bash

set -e

# Output to the same name as the script, but without ".sh" extension
DEST=${0:0:(-3)}
echo ${DEST}
SRC='src'

mkdir -p ${DEST}

# Apply Brain Mask
# fslmaths src/full_func.nii.gz -mas 'src/manmask.nii.gz' "$DEST/func_brain0.nii.gz"0
for i in 2 3; do
(
  fslmaths \
      "$SRC/full_func.nii.gz" \
      -edge \
      "$DEST/full_func_edge.nii.gz"

  3dvolreg \
      -twopass \
      -1Dfile "$DEST/brain-$i_blur${twoblur}.1D" \
      -1Dmatrix_save "$DEST/brain-$i_blur${twoblur}.aff12.1D" \
      -prefix "$DEST/brain_volreg-${i}_blur${twoblur}_edge.nii.gz" \
      -maxdisp1D $DEST/brain_md-${i}.1D \
      -weight "$SRC/manmask_weights$i.nii.gz[0]" \
      -zpad 2 \
      "$DEST/full_func_edge.nii.gz"

  fslmaths \
      "$DEST/brain_volreg-${i}_blur${twoblur}_edge.nii.gz" \
      -edge \
      "$DEST/brain_volreg-${i}_blur${twoblur}_edge_sd.nii.gz"
) &
done


wait
echo "Done!"
