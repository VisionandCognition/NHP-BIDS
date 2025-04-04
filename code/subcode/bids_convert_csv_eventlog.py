#!/usr/bin/env python3

""" Nipype wrapper for bids_convert_csv_eventlog.

    The code is run by bids_minimal_processing.py.
"""
import os
import re


from nipype.interfaces.base import (
    TraitedSpec,
    CommandLineInputSpec,
    CommandLine,
    File,
    isdefined,
)


class ConvertCSVInputSpec(CommandLineInputSpec):
    """ The inputspec specifies all the parameters of the command.
    """
    in_file = File(desc="CSV eventlog", exists=True, mandatory=True,
                   argstr="-i %s")
    stim_dir = File(desc="Stimulus CSV directory",  # exists=True,
                    argstr="--stim-dir %s")
    # out_file = File(desc="TSV eventlog", argstr="-o %s", genfile=True,
    #                 hash_files=False)
    out_file = File(argstr='-o %s',
                    hash_files=False,
                    genfile=True,
                    )


class ConvertCSVOutputSpec(TraitedSpec):
    out_file = File(desc="TSV eventlog",
                    exists=True,
                    # genfile=True
                    )


class ConvertCSVEventLog(CommandLine):
    """ Nipype wrapper for bids_convert_csv_eventlog
    """
    input_spec = ConvertCSVInputSpec
    output_spec = ConvertCSVOutputSpec
    _cmd = 'bids_convert_csv_eventlog'

    def __init__(self, **inputs):
        super(ConvertCSVEventLog, self).__init__(**inputs)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs

    def _gen_filename(self, name):
        if name == 'out_file':
            return self._gen_outfilename()
        return None

    def _gen_outfilename(self):
        out_file = self.inputs.out_file
        if not isdefined(out_file) and isdefined(self.inputs.in_file):
            out_file = self.inputs.in_file.split('/')[-2] + '.tsv'
        return os.path.abspath(out_file)


# test
if __name__ == '__main__':
    test = ConvertCSVEventLog(
        in_file='/NHP_MRI/NHP-BIDS/'
        'data_collection/sub-eddy/ses-20180117/func/'
        'sub-eddy_ses-20180117_task-ctcheckerboard_run-12_events/'
        'Log_Spinoza_3T_Eddy_StimSettings_CTShapedCheckerboard_20180117T1241_eventlog.csv',
        stim_dir='/NHP_MRI/NHP-BIDS/'
        'data_collection/sub-eddy/ses-20180117/func/'
        'sub-eddy_ses-20180117_task-ctcheckerboard_run-12_events',
    )
    print(test.cmdline)
    test.run()
