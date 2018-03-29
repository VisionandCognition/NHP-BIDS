#!/bin/bash
rm -R -f ~/NHP-BIDS
git clone https://github.com/VisionandCognition/NHP-BIDS.git
ln -s /nfs/cortalg/NHP-BIDS/derivatives ~/NHP-BIDS/derivatives
ln -s /nfs/cortalg/NHP-BIDS/sourcedata ~/NHP-BIDS/sourcedata
ln -s /nfs/cortalg/NHP-BIDS/sub-danny ~/NHP-BIDS/sub-danny
ln -s /nfs/cortalg/NHP-BIDS/sub-eddy ~/NHP-BIDS/sub-eddy
ln -s /nfs/cortalg/NHP-BIDS/workingdirs ~/NHP-BIDS/workingdirs
mkdir ~/NHP-BIDS/job-logs
chmod -R 777 ~/NHP-BIDS # this appears necessary to avoid permission errors
