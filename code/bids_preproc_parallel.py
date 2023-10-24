#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import csv
from multiprocessing import Pool


def run_command(command):
    os.system(command)


def run_splitpreproc(project,
                     csv_file,
                     subses,
                     no_warp,
                     maxproc):
    # define log and job folders =========================================
    logpp_path = './projects/' + project + '/logs/preproc/' + subses
    logwarp_path = './projects/' + project + '/logs/warp2nmt/' + subses

    # read csv files =====================================================
    if csv_file is not None:
        df = pd.read_csv(csv_file)
        sub = []
        ses = []
        run = []
        ref = []

        for index, row in df.iterrows():
            for r in row.run.strip("[]").split(" "):
                sub.append(row.subject)
                ses.append(row.session)
                run.append(r)
                if 'refsubject' in df.columns:
                    if row.refsubject == 'nan':
                        # empty field
                        ref.append(row.subject)
                    else:
                        # non-empty field
                        ref.append(row.refsubject)
                else:
                    ref.append(row.subject)
    else:
        print("No csv-file specified. Don't know what data to process.")
        exit()

    # create base folder for csv files ====================================
    csv_path = csv_file[0:-4]
    os.makedirs(csv_path, exist_ok=True)

    # create csv files ===================================================
    subcmd_preproc = []  # commands for preprocessing
    subcmd_warp = []  # commands for warp to nmt
    for idx, subj in enumerate(sub):
        csv_run = (csv_path + '/sub-' + sub[idx] + '_ses-' +
                   str(ses[idx]) + '_run-' + str(run[idx]) + '.csv')
        with open(csv_run, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["subject", "session", "run", "datatype", "refsubject"])
            writer.writerow(
                [sub[idx], ses[idx], "[" + run[idx] + "]", "[func]", ref[idx]])

        logpp_run = (logpp_path + '/sub-' + sub[idx] +
                     '_ses-' + str(ses[idx]) + '_run-' + str(run[idx]) + '.txt')
        logwarp_run = logwarp_path + '/run' + run[idx] + '.txt'
        runcmd1 = ('./code/bids_preprocessing_workflow.py' +
                   ' --csv ' + csv_run + ' |& ' + ' tee ' + logpp_run)
        runcmd2 = ('./code/bids_warp2nmt_workflow.py' + ' --proj ' + project +
                   ' --csv ' + csv_run + ' |& ' + ' tee ' + logwarp_run)
        subcmd_preproc.append(runcmd1)
        subcmd_warp.append(runcmd2)

    # process list of run commands in parallel ===================
    with Pool(processes=maxproc) as pool:
        pool.map(run_command, subcmd_preproc)

    # do the nmt warp if required (also parallel) ================
    if no_warp is True:
        print('Not doing the warping to NMT')
    else:
        with Pool(processes=maxproc) as pool:
            pool.map(run_command, subcmd_warp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Split pre-processing in multiple cluster-jobs')
    parser.add_argument('--proj', dest='project', required=True,
                        help='project label for subfolder.')
    parser.add_argument('--csv',
                        dest='csv_file', default=None,
                        help='CSV file with subjects, sessions, runs, and refsubject.')
    parser.add_argument('--subses',
                        dest='subses', default=None,
                        help='string identifying subject and session')
    parser.add_argument('--no-warp',
                        dest='no_warp', action='store_true',
                        help='add this flag if you do not want to warp to NMT')
    parser.add_argument('--maxproc', default=1,
                        dest='maxproc', action='store_true',
                        help='maximum number of parallel processes')

    args = parser.parse_args()
    run_splitpreproc(**vars(args))
