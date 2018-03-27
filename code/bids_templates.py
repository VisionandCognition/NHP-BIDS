
subject_list = ['danny','eddy']
session_list = [
    # '20170511',
    # '20170525',
    # '20170614',
    # '20170621',
    '20171116',
    '20171129',
    '20171207',
    '20171214',
    '20171220',
    '20180117',
    '20180124',
    '20180125',
    '20180131',
    '20180201'
]
datatype_list = ['func','anat','fmap','dwi']

templates = {
    'images': 'sub-{subject_id}/ses-{session_id}/{datatype}/'
              'sub-{subject_id}_ses-{session_id}_*.nii.gz',
}
