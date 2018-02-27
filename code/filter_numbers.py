#!/usr/bin/env python3
import nipype.interfaces.base as nib
# import (
#     TraitedSpec,
#     CommandLineInputSpec,
#     CommandLine,
#     File
# )
import os

class FilterNumsInputSpec(nib.CommandLineInputSpec):
    in_file = nib.File(desc="File", exists=True, mandatory=True, argstr="%s", position=1)
    max_number = nib.traits.Int(desc="Max number", mandatory=True, argstr="'($1<%d)'", position=0)
    out_file = nib.File(
        desc="Filtered file",
        name_source=['in_file'],
        name_template='%s_filtered',
        hash_files=False,
        argstr="> %s"
    )

class FilterNumsOutputSpec(nib.TraitedSpec):
    out_file = nib.File(desc = "Filtered file", exists=True)

class FilterNumsTask(nib.CommandLine):
    """ Filter out the numbers that are greater than max_number.
    """
    input_spec = FilterNumsInputSpec
    output_spec = FilterNumsOutputSpec
    _cmd = 'awk'

if __name__ == '__main__':

    filtnum = FilterNumsTask(in_file='an_existing_file')
    print(filtnum.cmdline)
    filtnum.run()
