
The file:

    sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold_res-1x1x1_reference.nii.gz

Can be created by (from BIDS root directory):

    fslroi resampled-isotropic-1mm/sub-eddy/ses-20170511/func/sub-eddy_ses-20170511_task-curvetracing_run-01_bold_res-1x1x1_preproc.nii.gz manual-masks/sub-eddy/ses-20170511/func/sub-eddy_ses-20170511_task-curvetracing_run-01_frame-50_bold_res-1x1x1_reference.nii.gz 49 1
