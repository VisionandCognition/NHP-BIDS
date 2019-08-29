#!/usr/bin/env python3

import nipype.algorithms.rapidart as ra

art = ra.ArtifactDetect(
    mask_type='file',
    translation_threshold=1.0,  # translation in mm
    rotation_threshold=0.02,  # rotation in radians
    zintensity_threshold=3.0,  # z-score
    use_norm=False,
    parameter_source='AFNI',
    save_plot=True,
    realignment_parameters='empty.file',
    realigned_files='empty.file',
    mask_file='empty.file',
)
art.run()
