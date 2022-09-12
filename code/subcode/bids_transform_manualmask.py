#!/usr/bin/env python3

# http://nipype.readthedocs.io/en/latest/users/examples/fmri_fsl.html
# http://miykael.github.io/nipype-beginner-s-guide/firstSteps.html#input-output-stream
import os                                    # system functions

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
import nipype.interfaces.fsl as fsl          # fsl
from nipype.interfaces.utility import IdentityInterface

from nipype.pipeline.engine import Workflow, Node, MapNode

from nipype import config
config.enable_debug_mode()

from nipype.interfaces.base import File


class ApplyXFMInputSpecRefName(fsl.preprocess.ApplyXFMInputSpec):
    out_file = File(argstr='-out %s', desc='registered output file',
                    name_source=['reference'], name_template='%s_flirt',
                    position=2, hash_files=False)


class ApplyXFMRefName(fsl.FLIRT):
    """Currently just a light wrapper around FLIRT,
    with no modifications
    ApplyXFMRefName uses the reference for naming the functional mask.
    """
    input_spec = ApplyXFMInputSpecRefName

ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def create_workflow():
    workflow = Workflow(
        name='transform_manual_mask')

    inputs = Node(IdentityInterface(fields=[
        'subject_id',
        'session_id',
        'refsubject_id',
        'ref_funcmask',
        'ref_func',
        'funcs',
    ]), name='in')

    # Find the transformation matrix func_ref -> func

    # first take the median (flirt functionality has changed and no longer automatically takes the first volume when given 4D files)
    median_func = MapNode(
                    interface=fsl.maths.MedianImage(dimension="T"),
                    name='median_func',
                    iterfield=('in_file'),
                    )
    findtrans = MapNode(fsl.FLIRT(),
                        iterfield=['in_file'],
                        name='findtrans'
                        )

    # Invert the matrix transform
    invert = MapNode(fsl.ConvertXFM(invert_xfm=True),
                     name='invert',
                     iterfield=['in_file'],
                     )
    workflow.connect(findtrans, 'out_matrix_file',
                     invert, 'in_file')

    # Transform the manualmask to be aligned with func
    funcreg = MapNode(ApplyXFMRefName(),
                      name='funcreg',
                      iterfield=['in_matrix_file', 'reference'],
                      )


    workflow.connect(inputs, 'funcs',
                     median_func, 'in_file')

    workflow.connect(median_func, 'out_file',
                     findtrans, 'in_file')
    workflow.connect(inputs, 'ref_func',
                     findtrans, 'reference')

    workflow.connect(invert, 'out_file',
                     funcreg, 'in_matrix_file')

    workflow.connect(inputs, 'ref_func',
                     funcreg, 'in_file')
    workflow.connect(inputs, 'funcs',
                     funcreg, 'reference')

    
    return workflow

if __name__ == '__main__':
    run_workflow()
