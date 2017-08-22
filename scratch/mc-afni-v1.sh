#!/bin/bash

set -e

# Output to the same name as the script, but without ".sh" extension
DEST=${0:0:(-3)}
echo ${DEST}
SRC='src'

mkdir -p ${DEST}

i=3
3dvolreg \
    -prefix "$DEST/brain_volreg-${i}_base2.nii.gz" \
    -weight "$SRC/manmask_weights$i.nii.gz[0]" \
    -base "$SRC/manmask_reference.nii.gz" \
    -zpad 4 \
    "$SRC/full_func.nii.gz"

exit

# Apply Brain Mask
# fslmaths src/full_func.nii.gz -mas 'src/manmask.nii.gz' "$DEST/func_brain0.nii.gz"
if true
then
  i=1
  3dvolreg \
      -1Dfile "$DEST/brain-$i.1D" \
      -1Dmatrix_save "$DEST/brain-1.aff12.1D" \
      -prefix "$DEST/brain_volreg-${i}.nii.gz" \
      -maxdisp1D $DEST/brain_md-${i}.1D \
      -weight "$SRC/manmask_weights.nii.gz[0]" \
      -zpad 2 \
      "$SRC/full_func.nii.gz" &

  i=2 # ---------------------------------------------- the best so far
  3dvolreg \
      -1Dfile "$DEST/brain-$i.1D" \
      -1Dmatrix_save "$DEST/brain-$i.aff12.1D" \
      -prefix "$DEST/brain_volreg-${i}.nii.gz" \
      -maxdisp1D $DEST/brain_md-${i}.1D \
      -weight "$SRC/manmask_weights$i.nii.gz[0]" \
      -zpad 2 \
      "$SRC/full_func.nii.gz" &

fi
i=2 # ---------------------------------------------- the best so far
3dvolreg \
    -prefix "$DEST/brain_volreg-${i}_base.nii.gz" \
    -weight "$SRC/manmask_weights$i.nii.gz[0]" \
    -base "$SRC/manmask_reference.nii.gz[0]" \
    -zpad 4 \
    "$SRC/full_func.nii.gz" &

3dvolreg \
    -prefix "$DEST/brain_volreg-${i}_base2.nii.gz" \
    -weight "$SRC/manmask_weights$i.nii.gz[0]" \
    -base "$SRC/manmask_reference.nii.gz" \
    -zpad 4 \
    "$SRC/full_func.nii.gz" &

two_passes_mc() {
  local i=$1
  local twoblur=$2
  3dvolreg \
      -twopass \
      -1Dfile "$DEST/brain-$i.1D" \
      -1Dmatrix_save "$DEST/brain-$i.aff12.1D" \
      -prefix "$DEST/brain_volreg-${i}_blur$twoblur.nii.gz" \
      -maxdisp1D $DEST/brain_md-${i}.1D \
      -weight "$SRC/manmask_weights$i.nii.gz[0]" \
      -zpad 2 \
      -twoblur $twoblur \
      "$SRC/full_func.nii.gz"

  fslmaths \
      "$DEST/brain_volreg-${i}_blur$twoblur.nii.gz" \
      -edge \
      "$DEST/brain_volreg-${i}_blur${twoblur}_edge.nii.gz"

  fslmaths \
      "$DEST/brain_volreg-${i}_blur${twoblur}_edge.nii.gz" \
      -edge \
      "$DEST/brain_volreg-${i}_blur${twoblur}_edge_sd.nii.gz"
}

for i in 2 3; do
  for twoblur in 2; do 
    two_passes_mc "$i" "$twoblur" &
  done
done

wait
echo "Done!"
