#!/usr/bin/env python3

import glob
import os
import sys
import errno

# Need to re-write for processing new layout! To-do!


def print_run(cmd):
    print('%s\n' % cmd)
    return os.system(cmd)


def process_dir(raw_dir, glob_pat):
    for fn in glob.glob("%s/%s" % (raw_dir, glob_pat)):
        fn = os.path.basename(fn)
        print("Processing %s" % fn)

        print_run("mri_convert -i %s/%s -o /tmp/%s --sphinx" %
                  (raw_dir, fn, fn))
        print_run("fslreorient2std /tmp/%s %s" % (fn, fn))

if __name__ == '__main__':
    assert (
        os.path.basename(os.getcwd()) == "func" or
        os.path.basename(os.getcwd()) == "fmap" or
        os.path.basename(os.getcwd()) == "anat"
    ), (
        "Script must be called from a 'func' directory.")

    if os.path.basename(os.getcwd()) == "func":
        process_dir('unprocessed-bold', '*_bold.nii.gz')
    elif os.path.basename(os.getcwd()) == "fmap":
        process_dir('unprocessed', '*_magnitude1.nii.gz')
        process_dir('unprocessed', '*_phasediff.nii.gz')
    elif os.path.basename(os.getcwd()) == "anat":
        process_dir('unprocessed', '*.nii.gz')
    else:
        raise Exception("Must be in directory such as 'func',"
                        "'fmap', or 'anat'.")
