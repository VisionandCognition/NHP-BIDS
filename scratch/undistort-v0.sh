#!/bin/bash

DEST=undistort-v0.0
echo ${DEST}
mkdir -p ${DEST}
fslmaths src/fmap_phasediff.nii.gz -mul 3.141592653589793116 -div 100 ${DEST}/fmap_phasediff_radians.nii.gz -odt float

prelude --abs=src/fmap_magnitude.nii.gz --mask=src/fmap_mask.nii.gz --phase=${DEST}/fmap_phasediff_radians.nii.gz --unwrap=${DEST}/phasediff_unwrapped.nii.gz


fslmaths ${DEST}/phasediff_unwrapped.nii.gz -mul 200 ${DEST}/phasediff_unwrapped_scaled.nii.gz

fugue --asym=0.0200000000 --dwell=0.0005585000 --loadfmap=${DEST}/phasediff_unwrapped_scaled.nii.gz --in=src/func.nii.gz --mask=src/fmap_mask.nii.gz --unwarpdir=y --unwarp=${DEST}/unwarped_func.nii.gz

fslview src/t1.nii.gz src/func.nii.gz ${DEST}/unwarped_func.nii.gz &

fslview ${DEST}/phasediff_unwrapped_scaled.nii.gz &
