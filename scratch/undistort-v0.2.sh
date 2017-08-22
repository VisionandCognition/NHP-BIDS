#!/bin/bash

set -e

DEST=undistort-v0.2
fdir=y
echo ${DEST}
mkdir -p ${DEST}

# Convert phasediff to Radians
fslmaths src/fmap_phasediff.nii.gz -mul 3.141592653589793116 -div 100 ${DEST}/fmaprads -odt float

# http://www.spinozacentre.nl/wiki/index.php/NeuroWiki:Current_developments#B0_correction
# unwrap phasemap
prelude --abs=src/fmap_magnitude --mask=src/fmap_mask.nii.gz --phase=${DEST}/fmaprads --unwrap=${DEST}/fmaprads_unwrapped

# http://www.spinozacentre.nl/wiki/index.php/NeuroWiki:Current_developments#B0_correction
# "Convert to radials-per-second by multiplying with 200 (because time difference between the two scans is 5 msec)."
# Where does the 5 msec come from?
fslmaths ${DEST}/fmaprads_unwrapped -mul 200 ${DEST}/fmaprads_unwrapped

# unmask the fieldmap (necessary to avoid edge effects)
# erosion may not be needed
fslmaths ${DEST}/fmaprads_unwrapped -abs -bin -mul src/fmap_mask.nii.gz \
  -kernel box 3x3x3 -ero \
  ${DEST}/fmaprads_mask
# From epi_reg - this is what Feat does
$FSLDIR/bin/fugue --loadfmap=${DEST}/fmaprads_unwrapped --mask=${DEST}/fmaprads_mask --unmaskfmap \
  --savefmap=${DEST}/fmaprads_unmasked --unwarpdir=${fdir} 

# Poly regularization
# Perhaps the regularization should occur before the isotropic resampling?
#   - Despiking in particular might be more effective?
for n in 1 2 3 4 5
do
# Median doesn't do much when combined with 3d poly fitting
#   fugue --asym=0.0200000000 --dwell=0.0005585000 --loadfmap=${DEST}/fmaprads_unmasked \
#     --in=src/func.nii.gz --mask=src/fmap_mask.nii.gz --unwarpdir=y \
#     -m --poly=$n \
#     --unwarp=${DEST}/unwarped_func_median_poly_$n.nii.gz
  fugue --asym=0.0200000000 --dwell=0.0005585000 --loadfmap=${DEST}/fmaprads_unmasked \
    --in=src/func.nii.gz --mask=src/fmap_mask.nii.gz --unwarpdir=y \
    --poly=$n \
    --unwarp=${DEST}/unwarped_func_poly_$n.nii.gz
done

for sig in 0 1 2
do
  fugue --asym=0.0200000000 --dwell=0.0005585000 --loadfmap=${DEST}/fmaprads_unmasked \
    --in=src/func.nii.gz --mask=src/fmap_mask.nii.gz --unwarpdir=y \
    -m --smooth3=$sig \
    --unwarp=${DEST}/unwarped_func_median_smooth3_$sig.nii.gz
  fugue --asym=0.0200000000 --dwell=0.0005585000 --loadfmap=${DEST}/fmaprads_unmasked \
    --in=src/func.nii.gz --mask=src/fmap_mask.nii.gz --unwarpdir=y \
    --smooth3=$sig \
    --unwarp=${DEST}/unwarped_func_smooth3_$sig.nii.gz
done

ls ${DEST}

# median smooth3 2 seems to be the best?
fslview \
  src/t1.nii.gz \
  ${DEST}/unwarped_func_poly_1.nii.gz \
  ${DEST}/unwarped_func_poly_2.nii.gz \
  ${DEST}/unwarped_func_poly_3.nii.gz \
  ${DEST}/unwarped_func_poly_4.nii.gz \
  ${DEST}/unwarped_func_poly_5.nii.gz \
  ${DEST}/unwarped_func_poly_median_1.nii.gz \
  ${DEST}/unwarped_func_poly_median_2.nii.gz \
  ${DEST}/unwarped_func_poly_median_3.nii.gz \
  ${DEST}/unwarped_func_poly_median_4.nii.gz \
  ${DEST}/unwarped_func_poly_median_5.nii.gz \
  ${DEST}/unwarped_func_smooth3_0.nii.gz \
  ${DEST}/unwarped_func_smooth3_1.nii.gz \
  ${DEST}/unwarped_func_smooth3_2.nii.gz \
  &
