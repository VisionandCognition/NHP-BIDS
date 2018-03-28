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

For a more comprehensive explanation of running analyses on LISA see https://github.com/VisionandCognition/Process-NHP-MRI/blob/master/docs/BIDS-NHP-on-Lisa.md


Running the Pipeline
====================

You should change the `curve-tracing-20180125-run02.csv` to a CSV script that actually exists. There should be some available in the NHP-BIDS directory (perhaps they will be moved to some place cleaner, such as code?).

1. Create a `copy-to-bids.sh` script in the `Data_raw/SUBJ/YYYYMMDD` folder, and run it.
   * Base script off of existing script, for example, `Data_raw/EDDY/20180222/copy-to-bids.sh`. This script tends to improve each iteration. To find the most recent one, you can try calling `find -maxdepth 3 -name "copy-to-bids.sh" -exec ls -lt {} +` from the `Data_raw` directory. Your colleague, however, maybe keeping a secret version to themselves.
   * In order to match the runs with the behavioral data, you either need to the notes that relate the run numbers with the behavioral timestamps, or you need to correspond the AcquisitionTime (in the json files, created by dcm2niix) with the behavioral timestamps. For example, the log `Behavior/Eddy_Curve_Tracing_StimSettings_CTShapedCheckerboard_Spinoza_3T_20180117T1207-T1215.49` matches with the run 8, which has an acquisition time of `12:08:54.410000`.

2. Modify `code/bids_templates.py` to add the new session (and subject, if needed).
   * May be replaced completely by csv list in the future.

3. Create or modify a csv file that lists the *subject, session* and *runs* to process (see `checkerboard-ct-mapping.csv` for an example). These csv files can be kept in the csv directory. 

4. Run `./code/bids_minimal_preprocessing.py` from your BIDS root directory (this file also has instructions in the file header).
   * example: `clear && ./code/bids_minimal_processing.py --csv ./csv/checkerboard-ct-mapping.csv |& tee ./logs/log-minproc.txt`
   * help: `./code/bids_minimal_processing.py --help`
   * LISA: make sure to load freesurfer, FSL ``module load freesurfer``, ``module load fsl``

5. Run `./code/resample_isotropic_workflow.py`
   * example: `clear && ./code/resample_isotropic_workflow.py --csv ./csv/checkerboard-ct-mapping.csv |& tee ./logs/log-resample.txt`

6. Run `./code/preprocessing_workflow.py`
   * example: `clear && ./code/preprocessing_workflow.py --csv ./csv/checkerboard-ct-mapping.csv |& tee ./logs/log-preproc.txt`
   * pbs: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `qsub ./code/pbs/preprocess_SESSION.job`, where SESSION defines which session / run to process.

7. Run `./code/modelfit_workflow.py`
   * This script requires the `--contrasts` parameter. This depends on the experiment. In `code/contrasts/` there are python modules for each set of contrasts. If you want to use the contrasts defined in `ctcheckerboard.py`, for example, pass `ctcheckerboard` as the value for the `--contrasts` parameter. If you create your own contrasts, you just need your function to define the variable named `contrasts`. Since the code assumes a python module name, you cannot use dashes or spaces.
   * debug: `clear && python -m pdb ./code/modelfit_workflow.py --csv ./csv/checkerboard-ct-mapping.csv --contrasts ctcheckerboard |& tee ./logs/log-modelfit.txt`
   * normal: `clear && ./code/modelfit_workflow.py --csv ./csv/checkerboard-ct-mapping.csv  --contrasts ctcheckerboard |& tee ./logs/log-modelfit.txt`
   * pbs: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `qsub code/pbs/modelfit.job` (modify file or duplicate thereof as needed).
