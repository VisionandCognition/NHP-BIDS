In order to add data downloaded from SCNAT, create a file that copies data
from the Data_raw directory to this directory, create a file like this:
Data_raw/EDDY/20180222/copy-to-bids.sh

Actually, that file is probably out of date by the time you read this. You should find the latest version of `copy-to-bids.sh`. I usually use: `find -maxdepth 3 -name "copy-to-bids.sh" -exec ls -lt {} +` (from the Data_raw/EDDY directory) although the timestamps can get messed up with synchronization tools.

This pipeline uses NiPype to create the data that tries to adhere to [BIDS](http://bids.neuroimaging.io).

There is documentation in the python scripts and at:
https://github.com/VisionandCognition/Process-NHP-MRI/blob/master/docs/BIDS_processing.md
