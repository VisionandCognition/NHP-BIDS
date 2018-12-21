#PBS -lwalltime=6:00:00  
#PBS -lnodes=1:ppn=16
#PBS -S /bin/bash

n=`wc -l < $PBS_NODEFILE`
echo start of job in directory $PBS_O_WORKDIR
echo number of nodes is $n
echo the allocated nodes are:
cat $PBS_NODEFILE

module rm Python/2.7.12-intel-2016b 2> /dev/null # might complain if already removed

module load eb

module load fsl/5.08

module load afni
module load python/3.5.0-intel

VIRTUALENVWRAPPER_PYTHON=$(which python)
source ~/.local/bin/virtualenvwrapper.sh
workon mri-py3

export PYTHONPATH=$PYTHONPATH:~/NHP-BIDS/code
export PATH=$PATH:~/NHP-BIDS/code/mc/
export FSLOUTPUTTYPE=NIFTI_GZ

cd NHP-BIDS
