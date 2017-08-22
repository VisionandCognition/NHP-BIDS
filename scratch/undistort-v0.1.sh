#!/bin/bash

set -e

DEST=undistort-v0.1
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
fslmaths ${DEST}/fmaprads_unwrapped -abs -bin -mul src/fmap_mask.nii.gz \
  -kernel box 3x3x3 -ero \
  ${DEST}/fmaprads_mask
$FSLDIR/bin/fugue --loadfmap=${DEST}/fmaprads_unwrapped --mask=${DEST}/fmaprads_mask --unmaskfmap \
  --savefmap=${DEST}/fmaprads_unmasked --unwarpdir=${fdir} 

fugue --asym=0.0200000000 --dwell=0.0005585000 --loadfmap=${DEST}/fmaprads_unmasked \
  --in=src/func.nii.gz --mask=src/fmap_mask.nii.gz --unwarpdir=y --unwarp=${DEST}/unwarped_func.nii.gz

ls ${DEST}

fslview src/t1.nii.gz src/func.nii.gz ${DEST}/unwarped_func.nii.gz &

fslview ${DEST}/fmaprads_unmasked &
