This pipeline uses NiPype to create the data that tries to adhere to [BIDS](http://bids.neuroimaging.io).

Installation
============

The scripts require `python3` (if you use virtual environments: `mkvirtualenv --python=/usr/bin/python3 mri-py3`) and a recent version of nipype (`pip install https://github.com/nipy/nipype/archive/master.zip`, it requires changes shortly after version 1 was released).

You should also add the `code` directory to both the `PYTHONPATH` and `PATH` environment variables.

This documentation used to be located at:
https://github.com/VisionandCognition/Process-NHP-MRI/blob/master/docs/BIDS_processing.md

Running the Pipeline
====================
For processing data using the BIDS format, clone the following repository:

https://github.com/VisionandCognition/NHP-BIDS/


You should change the `curve-tracing-20180125-run02.csv` to a CSV script that actually exists. There should be some available in the NHP-BIDS directory (perhaps they will be moved to some place cleaner, such as code?).

1. Create a `copy-to-bids.sh` script in the `Data_raw/SUBJ/YYYYMMDD` folder, and run it.
   * Base script off of existing script, for example, `Data_raw/EDDY/20180222/copy-to-bids.sh`. This script tends to improve each iteration. To find the most recent one, you can try calling `find -maxdepth 3 -name "copy-to-bids.sh" -exec ls -lt {} +` from the `Data_raw` directory. Your colleague, however, maybe keeping a secret version to themselves.
   * In order to match the runs with the behavioral data, you either need to the notes that relate the run numbers with the behavioral timestamps, or you need to correspond the AcquisitionTime (in the json files, created by dcm2niix) with the behavioral timestamps. For example, the log `Behavior/Eddy_Curve_Tracing_StimSettings_CTShapedCheckerboard_Spinoza_3T_20180117T1207-T1215.49` matches with the run 8, which has an acquisition time of `12:08:54.410000`.
2. Modify `code/bids_templates.py` to add the new session (and subject, if needed).
   * May be replaced completely by csv list in the future.
3. Create or modify csv file that lists the runs to process.
4. Run `./code/bids_minimal_preprocessing.py` from your BIDS root directory (this file also has instructions in the file header).
  * example: `clear && ./code/bids_minimal_processing.py --csv checkerboard-ct-mapping.csv |& tee log-minproc.txt`
  * help: `./code/bids_minimal_processing.py --help`
5. Run `./code/resample_isotropic_workflow.py`
  * example: `clear && ./code/resample_isotropic_workflow.py --csv checkerboard-ct-mapping.csv |& tee log-resample.txt`
6. Run `./code/preprocessing_workflow.py`
  * example: `clear && ./code/preprocessing_workflow.py --csv checkerboard-ct-mapping.csv |& tee log-preproc.txt`
  * pbs: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `qsub code/pbs/preprocess_SESSION.job`, where SESSION defines which session / run to process.
7. Run `./code/modelfit_workflow.py`
  * debug: `clear && python -m pdb ./code/modelfit_workflow.py --csv checkerboard-ct-mapping.csv |& tee log-modelfit.txt`
  * normal: `clear && ./code/modelfit_workflow.py --csv checkerboard-ct-mapping.csv |& tee log-modelfit.txt`
  * pbs: on `lisa.surfsara.nl` go to `NHP-BIDS` directory and run `qsub code/pbs/modelfit.job` (modify file or duplicate thereof as needed).
