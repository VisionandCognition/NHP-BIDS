This pipeline uses NiPype to create the data that tries to adhere to [BIDS](http://bids.neuroimaging.io). 
For questions and comments, please contact Chris Klink: c.klink@nin.knaw.nl

Installation
============

The pipeline works with **python3** (we suggest using **(ana)conda** (https://www.anaconda.com/) to set-up a dedicated environment
and requires:
* **nipype** (>=1.0.1dev) (`pip install https://github.com/nipy/nipype/archive/master.zip`)
* **pandas** 
* **FSL** (>=5.0.1)
* **Freesurfer** (>=5.3.0)
* **AFNI** (>=??)
* **ANTS** (>=??)

For the installation, clone [this](https://github.com/VisionandCognition/NHP-BIDS/) repository:

    $ git clone https://github.com/VisionandCognition/NHP-BIDS.git
    
and add these lines to your ``~.bashrc`` :

```
export PATH="/home/<username>/NHP-BIDS/code:$PATH"
export PATH="/home/<username>/NHP-BIDS/code/subcode:$PATH"
export PATH="/home/<username>/NHP-BIDS/code/mc:$PATH"
export PYTHONPATH="/home/<username>/NHP-BIDS/code:$PYTHONPATH"
``` 

**Only on LISA** (`lisa.surfsara.nl`) you also need to create links to the data directories:

    $ ln -s /project/cortalg/NHP-BIDS/sourcedata ~/NHP-BIDS/sourcedata
    $ ln -s /project/cortalg/NHP-BIDS/derivatives/ ~/NHP-BIDS/derivatives
    $ ln -s /project/cortalg/NHP-BIDS/workingdirs ~/NHP-BIDS/
    $ ln -s /project/cortalg/NHP-BIDS/manual-masks ~/NHP-BIDS/
    $ ln -s /project/cortalg/NHP-BIDS/scratch ~/NHP-BIDS/
    $ ln -s /project/cortalg/NHP-BIDS/sub-eddy ~/NHP-BIDS/
    $ ln -s /project/cortalg/NHP-BIDS/sub-danny ~/NHP-BIDS/
    $ ln -s /project/cortalg/NHP-BIDS/sub-<MONKEY> ~/NHP-BIDS/ # add more monkeys when necessary

(We suggest using a bash-script for clean initialization.)    

You should also make new files accessible to all 'cortalg' group members by adding this to ``~.bashrc`` :

```
umask u+rwx g+rwx
```

For a more comprehensive explanation of running analyses on LISA see https://github.com/VisionandCognition/Process-NHP-MRI/blob/master/docs/NHP-BIDS-on-Lisa.md


Running the Pipeline
====================

You specify what data to process with csv-files. See `NHP-BIDS/csv/SubSesRun.csv` for an example. All steps can in principle also be run on the SurfSara LISA cluster. If you want to do that, you should create a job-file to work with the batch scheduler (see https://userinfo.surfsara.nl/systems/lisa/user-guide/creating-and-running-jobs). The precise names and subfolder location of job-files are optional, but it should be a bash script. A template can be found in `NHP-BIDS/code/lisa/template_SLURM.sh`. For all steps below, we specify how you would run each processing step on the cluster, but a single job-file can also contain all these steps together in a sequence so that everything runs serially (make sure you reserve enough computing time in your jobs-script!)     

0. Make sure you have the data in `Data_raw`. If you don't know how to do this, read the instructions here: https://github.com/VisionandCognition/NHP-Process-MRI/blob/master/docs/NHP_fMRI_Pipeline.md    

1. Create a `copy-to-bids.sh` script in the `Data_raw/SUBJ/YYYYMMDD` folder, and run it.
   * Base this script on an already existing script from a previous run or simply use the template `NHP-BIDS\code\copy-to-bids_template.sh`.
   * If you have trouble matching imaging data to log-files (e.g., because something went wrong with the filenames) you can either check your written notes notes, or you need can try matching up the AcquisitionTime (in the json files, created by dcm2niix) with the behavioral timestamps. If there are no json available you can (re)create them with `dcm2niix -b o -o <outputfolder> <location of dicom images>/*`. In addition, the json in the behavioral log folder can tell you under what run number the behavioral session was logged. If you did everything correctly, this should match the run number in the scan's filename.

2. Create or modify a csv file that lists the *subject, session*, *run*, and *datatype* to process (see `SubSesRun.csv` for an example of how to format this). These csv files can be kept in the csv directory.     
**NB** In all workflows except for `bids_minimal_processing`, the *run* column specifies which functional runs will be processed. In `bids_minimal_processing`, all image files are processed and the *run* column specifies which eventlog csv files will be processed.

3. Run `./code/bids_minimal_preprocessing.py` from your BIDS root directory (this file also has instructions in the file header).
   * The `--csv` flag is mandatory and should point to the csv-file that is formatted as explained above.    
   * The `--ignore_events` flag causes the workflow to skip processing the eventlog csv files for all runs. If this flag is not used, the eventlogs will be processed for all runs specified in the csv file.
   * example: `clear && ./code/bids_minimal_processing.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-minproc.txt`
   * help: `./code/bids_minimal_processing.py --help`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/minproc/minproc_SESSION.sh`, where SESSION defines which session or run to process. A command like the above should be part of the job-file. Make sure to load freesurfer, FSL using ``module load freesurfer``, ``module load fsl``.

4. Run `./code/bids_resample_isotropic_workflow.py` to resample all volumes to 1.0 mm isotropic voxels
   * The `--csv` flag is mandatory and should point to the csv-file that is formatted as explained above.  
   * example: `clear && ./code/bids_resample_isotropic_workflow.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-resample.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/isoresample/isoresample_SESSION.sh`, where SESSION defines which session or run to process. Command like the above should be part of the job-file.
   
5. Run `./code/bids_resample_hires_isotropic_workflow.py` if you also want the high-resolution 0.6 mm isotropic anatomical images
   * The `--csv` flag is mandatory and should point to the csv-file that is formatted as explained above.    
   * example: `clear && ./code/bids_resample_hiresanat_isotropic_workflow.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-resample_hiresanat.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/isoresample/isoresample_hires_SESSION.sh`, where SESSION defines which session / run to process. Command like the above should be part of the job-file.

6. Run `./code/bids_preprocessing_workflow.py`
   * Motion correction will be performed slice-by-slice and as a volume. Data is nonlinearly registered to reference volumes that are located in `NHP-BIDS/manual-masks/sub-<subject>/`. NB! If you undistort (fieldmap) the reference images in `manual-masks`, the nonlinear registration will essentially do the undistortion on all the other volumes for you.
   * It is no longer necessary to create separate workflows for subjects (because of different individual references). The generic workflow now looks for references in subject specific folders in `manual-masks`. If you work with a new subject, you should create such a folder. In that case you should follow the filename pattern of the existing references and only replace the subject name. The workflow should then also work for the new subject.
   * The `--csv` flag is mandatory and should point to the csv-file that is formatted as explained above.  
   * In this workflow you can add an `altref` column to the csv file. The workflow will interpret this column as identifier for which reference folder to use (deault is the one named sub-<SUBJECT>). When the column is omitted, the workflow looks for reference files in the default folder. This can be useful if, for some reason, an animal should be registered against another reference later on (e.g., after reimplantation of a head-post). When used, `altref` will have to specified for *each* row of the csv file (but you can simply repeat the `subject` entry if you want to use the default for some runs). NB!
    The `altref` argument specifies which manual-mask *folder* to get references from. The actual files in this folder should still belong to correct subject and be named appropriately. Example, you can preprocess files for subject A with `manual-masks/sub-A/func/sub-A_ref_etc.nii.gz` and `manual-masks/AltRef/func/sub-A_ref_etc.nii.gz`, but not with `manual-masks/AltRef/func/sub-B_ref_etc.nii.gz`. 
   * The `--fwhm` and `--HighPass` flags are optional to specify spatial smoothing (mm) and a high-pass filter (s). If not specified, they will be 2.0 mm and 50 s respectively.  
   * example: `clear && ./code/bids_preprocessing_workflow.py --csv ./csv/<SubSesRun.csv> |& tee ./logs/log-preproc.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/lisa/preproc/preprocess_SESSION.sh`, where SESSION defines which session / run to process. A command like the above should be part of the job-file.
   * NB! It is possible (though rare) that the workflow crashes with a messsage that starts with `RuntimeError: Command: convert_xfm -omat ....` This is an FSL bug in which a flirt operation creates a hexadecimal matrix file instead of a decimal one. You can fix this with the script `./helper_scripts/hex2dec.sh` and re-run the workflow.

7. Run `./code/bids_modelfit_workflow.py`
**NB** All files in the modelfit are expected to be motion corrected and registered to the same reference space!! A better way to do this is to register motion corrected files to a standard space first. This is work-in-progress. 

   * The `--csv` flag is mandatory and should point to the csv-file that is formatted as explained above.  
   * Here you can again specify a *refsubject* column in the csv.
   * This `--contrasts` is mandatory and depends on the experiment. In `code/contrasts/` there are python modules for each set of contrasts. If you want to use the contrasts defined in `ctcheckerboard.py`, for example, pass `ctcheckerboard` as the value for the `--contrasts` parameter. If you create your own contrasts, you just need your function to define the variable named `contrasts`. Since the code assumes that this will be a python module name, you cannot use dashes or spaces in the name.
   * The optional argument `--resultfld` allows you to define the name of the output folder and working directories for this analysis. Re-running something with the same name uses existing intermediate results from working directories and overwrites existing output directories. Using a unique folder name starts the analysis in a new working directory and creates a unique new output folder. If you do not include this argument, it will default to the stem of the specified csv-filename so if you use `checkerboard-ct-mapping.csv` this would put your results in `checkerboard-ct-mapping`. Again, if this folder exists the workflow will re-use intermediate results and overwriting the final result folder. 
   * The optional argument `--hrf` alows you to specify a custom hrf saved as `./code/hrf/CUSTOM-HRF.txt`. This should be a single column text file with a sample frequency of 0.05s/sample. For more complicated FLOBS-style multi-function HRF's you can also specify multiple columns. If this argument is omitted, FSL's default double-gamma canonical HRF is used. This is often not a bad approximation, but a specific monkey HRF can be a little faster (there is code in Tracker-MRI to run an experiment that allows estimating the HRF on an individual basis).
   * The `--fwhm` and `--HighPass` flags are optional to specify spatial smoothing (mm) and a high-pass filter (s). If not specified, they will be 2.0 mm and 50 s respectively.     
   * example: `clear && ./code/bids_modelfit_workflow.py --csv ./csv/checkerboard-ct-mapping.csv --contrasts ctcheckerboard |& tee ./logs/log-modelfit.txt` or `clear && ./code/bids_modelfit_workflow.py --csv ./csv/checkerboard-ct-mapping.csv  --contrasts ctcheckerboard --hrf ./code/hrf/custom-hrf.txt --resultfld my_unique_output |& tee ./logs/log-modelfit.txt`
   * LISA: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `sbatch ./code/lisa/modelfit/modelfit_SESSION.sh`, where SESSION defines which session / run to process. A command like the above should be part of the job-file.
