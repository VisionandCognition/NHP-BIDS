#PBS -lwalltime=6:00:00  
#PBS -lnodes=1:ppn=16
#PBS -S /bin/bash

n=`wc -l < $PBS_NODEFILE`
echo start of job in directory $PBS_O_WORKDIR
echo number of nodes is $n
echo the allocated nodes are:
cat $PBS_NODEFILE

module load eb
module load freesurfer
module load fsl/5.08
module load afni

source ~/.bash_profile 
source ~/.bashrc

export FSLOUTPUTTYPE=NIFTI_GZ

cd NHP-BIDS

echo "Job $PBS_JOBID ended at `date`." | mail $USER -s "Job $PBS_JOBID ended"
