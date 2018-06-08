#!/bin/bash
SUBJ=eddy
declare -a SESS=( \
    20160721 \
    20160728 \
    20160729 \
    20160803 \
    20160804 \
    20170411 \
    20170420 \
    20170512 \
    20170516 \
    20170517 \
    20170518 \
    20170607 \
    20171116 \
    20171129 \
    )    

echo 'Submitting sessions as separate jobs...'
for session in ${SESS[@]} ; do
    echo ${SUBJ}-${session}
    qsub ~/NHP-BIDS/code/pbs/preprocess-${SUBJ}-${session}    
done 