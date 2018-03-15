#!/bin/bash

## submitting `code/preprocessing_workflow.py` to PBS for multiple sessions, runs

project='NHP-BIDS'
subject='eddy'

# TODO: read this info from ../../*.csv
declare -a SESSIONS=(20180222)
declare -a RUNS=(3 4 5 6)

#log_path='~/logs'
# ------------------------------------ #

# cd ${log_path}
for session in ${SESSIONS[@]} ; do
	for run in ${RUNS[@]} ; do
		
		tmpscript="pbs_preprocessing_workflow_${project}_${subject}_${session}_run_${run}"

		echo "cd ~/dev/NHP-BIDS" > ${tmpscript}
		echo "module load eb" >> ${tmpscript}
		echo "module load FSL/5.0.10-intel-2016b" >> ${tmpscript}
		echo "module load afni" >> ${tmpscript}
		echo "export FSLOUTPUTTYPE=NIFTI_GZ" >> ${tmpscript}
		echo "./code/preprocessing_workflow.py --run $run -s $session" >> ${tmpscript}
		
		# -V declares that all environment variables in the qsub command's environment are to be exported to the batch job.
		qsub -V -l walltime=08:00:00,mem=14gb ${tmpscript}
		rm -f $tmpscript
	done
done