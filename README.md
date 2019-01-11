This pipeline uses NiPype to create the data that tries to adhere to [BIDS](http://bids.neuroimaging.io).

Installation
============

The pipeline works with **python3** (if you use virtual environments: `mkvirtualenv --python=/usr/bin/python3 mri-py3`) and requires:
* **nipype** (>=1.0.1dev) (`pip install https://github.com/nipy/nipype/archive/master.zip`)
* **FSL** (>=5.0.1)
* **Freesurfer** (>=5.3.0)
* **AFNI** (>=??)
* **ANTS** (>=??)

For the installation, clone [this](https://github.com/VisionandCognition/NHP-BIDS/) repository:

    $ git clone https://github.com/VisionandCognition/NHP-BIDS.git
    
and add these lines to your ``~.bashrc`` :

```
export PATH="/home/<username>/NHP-BIDS/code:$PATH"
export PATH="/home/<username>/NHP-BIDS/code/mc:$PATH"
export PYTHONPATH="/home/<username>/NHP-BIDS/code:$PYTHONPATH"
``` 

**Only on LISA** (`lisa.surfsara.nl`) you also need to create links to the data directories:

    $ ln -s /nfs/cortalg/NHP-BIDS/sourcedata ~/NHP-BIDS/sourcedata
    $ ln -s /nfs/cortalg/NHP-BIDS/derivatives/ ~/NHP-BIDS/derivatives
    $ ln -s /nfs/cortalg/NHP-BIDS/workingdirs ~/NHP-BIDS/
    $ ln -s /nfs/cortalg/NHP-BIDS/manual-masks ~/NHP-BIDS/
    $ ln -s /nfs/cortalg/NHP-BIDS/scratch ~/NHP-BIDS/
    $ ln -s /nfs/cortalg/NHP-BIDS/sub-eddy ~/NHP-BIDS/
    $ ln -s /nfs/cortalg/NHP-BIDS/sub-danny ~/NHP-BIDS/
    $ ln -s /nfs/cortalg/NHP-BIDS/sub-<MONKEY> ~/NHP-BIDS/ # add more monkeys when necessary
    
and make new files accessible to all 'cortalg' group members by adding this to ``~.bashrc`` :

```
umask u+rwx g+rwx
```

For a more comprehensive explanation of running analyses on LISA see https://github.com/VisionandCognition/Process-NHP-MRI/blob/master/docs/BIDS-NHP-on-Lisa.md


Running the Pipeline
====================

You should change the `SubSesRun.csv` to a CSV script that actually exists. There should be some examples available in the NHP-BIDS/csv directory. All steps can in principle also be run on the SurfSara LISA cluster. If you want to do that you should create a job-file to work with the batch scheduler (see https://userinfo.surfsara.nl/systems/lisa/user-guide/creating-and-running-jobs). The precise names and subfolder location of job-files are optional, but it should be a bash script. A template can be found in `NHP-BIDS/code/lisa/template_SLURM_ck.sh`. For all steps below, we specify how you would run that single step on the cluster, but a single job-file can also contain all these steps in a sequence so that everything runs with the single job (if you this make sure you reserve enough computing time!)

1. Create a `copy-to-bids.sh` script in the `Data_raw/SUBJ/YYYYMMDD` folder, and run it.
   * Base script off of existing script. This script tends to improve each iteration. To find the most recent one, you can try calling `find -maxdepth 3 -name "copy-to-bids.sh" -exec ls -lt {} +` from the `Data_raw` directory. There is also a template version `NHP-BIDS/code/copy-to-bids_template.sh`
   * In order to match the runs with the behavioral data, you either need to the notes that relate the run numbers with the behavioral timestamps, or you need to correspond the AcquisitionTime (in the json files, created by dcm2niix) with the behavioral timestamps. For example, the log `Behavior/Eddy_Curve_Tracing_StimSettings_CTShapedCheckerboard_Spinoza_3T_20180117T1207-T1215.49` matches with the run 8, which has an acquisition time of `12:08:54.410000`. If there are no json available you can (re)create them with `dcm2niix -b o -o <outputfolder> <location of dicom images>/*`. In addition, the json in the behavioral can tell you under what run number the behavioral session was logged. If you did everything correctly, did should match the run number in the scan's filename.

2. Modify `code/bids_templates.py` to add the new session (and subject, if needed).
   * May be replaced completely by csv list in the future. [CK: working on getting rid of this...]

3. Create or modify a csv file that lists the *subject, session* and *runs* to process (see `SubSesRun.csv` for an example). These csv files can be kept in the csv directory. NB! *runs* are not used at this stage, so defining 1 run per session suffices.

4. Run `./code/bids_minimal_preprocessing.py` from your BIDS root directory (this file also has instructions in the file header).
   * NB! All sessions should have the same types of scans (specify which with `--types`, see `help` for details)
   * If you are not processing standard curve-tracing data use the `--ignore_events` flag
   * example: `clear && ./code/bids_minimal_processing.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-minproc.txt`
   * help: `./code/bids_minimal_processing.py --help`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/minproc/minproc_SESSION.sh`, where SESSION defines which session / run to process. A command like the above should be part of the job-file. Make sure to load freesurfer, FSL using ``module load freesurfer``, ``module load fsl``.

5. Run `./code/resample_isotropic_workflow.py` to resample all volumes to 1.0 mm isotropic voxels
   * example: `clear && ./code/resample_isotropic_workflow.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-resample.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/isoresample/isoresample_SESSION.sh`, where SESSION defines which session / run to process. Command like the above should be part of the job-file.
   
   Run `./code/resample_hiresanat_isotropic_workflow.py` if you also want the high-resolution 0.6 mm isotropic anatomical images
   * example: `clear && ./code/resample_hiresanat_isotropic_workflow.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-resample_hiresanat.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/isoresample/isoresample_hires_SESSION.sh`, where SESSION defines which session / run to process. Command like the above should be part of the job-file.

6. Run `./code/preprocessing_workflow.py`
   * Motion correction will be performed slice-by-slice and as a volume. Data is nonlinearly registered to reference volumes that are located in `NHP-BIDS/manual-masks/sub-<subject>`. NB! If you undistort (fieldmap) the reference images in `manual-masks`, the nonlinear registration will essentially do the undistortion on all the other volumes for you. For undistortion instructions check <TO_BE_WRITTEN> 
   * example: `clear && ./code/preprocessing_workflow.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-preproc.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/lisa/preproc/preprocess_SESSION.sh`, where SESSION defines which session / run to process. A command like the above should be part of the job-file.


7. Run `./code/modelfit_workflow.py`
   * This script requires the `--contrasts` parameter. This depends on the experiment. In `code/contrasts/` there are python modules for each set of contrasts. If you want to use the contrasts defined in `ctcheckerboard.py`, for example, pass `ctcheckerboard` as the value for the `--contrasts` parameter. If you create your own contrasts, you just need your function to define the variable named `contrasts`. Since the code assumes a python module name, you cannot use dashes or spaces.
   * debug: `clear && python -m pdb ./code/modelfit_workflow.py --csv ./csv/checkerboard-ct-mapping.csv --contrasts ctcheckerboard |& tee ./logs/log-modelfit.txt`
   * normal: `clear && ./code/modelfit_workflow.py --csv ./csv/checkerboard-ct-mapping.csv  --contrasts ctcheckerboard |& tee ./logs/log-modelfit.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/lisa/modelfit/modelfit_SESSION.sh`, where SESSION defines which session / run to process. A command like the above should be part of the job-file.
