#!/usr/bin/env python3

from builtins import range

import nipype.interfaces.io as nio           # Data i/o
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model specification
from nipype.interfaces.base import Bunch
import os                                    # system functions

import nipype.interfaces.fsl as fsl          # fsl

import transform_manualmask
import motioncorrection_workflow
import undistort_workflow
import nipype.interfaces.utility as niu

# Using example: http://nipy.org/nipype/0.10.0/users/examples/fmri_fsl.html#set-up-model-fitting-workflow
modelfit = pe.Workflow(name="modelfit")

ds_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = ds_root

modelfit.base_dir = os.path.join(ds_root, 'workingdirs')

level1design = pe.Node(interface=fsl.Level1Design(), name="level1design")

modelgen = pe.MapNode(interface=fsl.FEATModel(), name='modelgen',
                      iterfield=['fsf_file', 'ev_files'])
modelspec = pe.Node(interface=model.SpecifyModel(), name="modelspec")

modelestimate = pe.MapNode(interface=fsl.FILMGLS(smooth_autocorr=True,
                                                 mask_size=5,
                                                 threshold=1000),
                           name='modelestimate',
                           iterfield=['design_file', 'in_file'])

conestimate = pe.MapNode(interface=fsl.ContrastMgr(), name='conestimate',
                         iterfield=['tcon_file', 'param_estimates',
                                    'sigmasquareds', 'corrections',
                                    'dof_file'])

modelfit.connect([
    (modelspec, level1design, [('session_info', 'session_info')]),
    (level1design, modelgen, [('fsf_files', 'fsf_file'),
                              ('ev_files', 'ev_files')]),
    (modelgen, modelestimate, [('design_file', 'design_file')]),
    (modelgen, conestimate, [('con_file', 'tcon_file')]),
    (modelestimate, conestimate, [('param_estimates', 'param_estimates'),
                                  ('sigmasquareds', 'sigmasquareds'),
                                  ('corrections', 'corrections'),
                                  ('dof_file', 'dof_file')]),
])

"""
Set up fixed-effects workflow
-----------------------------

"""

fixed_fx = pe.Workflow(name='fixedfx')

"""
Use :class:`nipype.interfaces.fsl.Merge` to merge the copes and
varcopes for each condition
"""

copemerge = pe.MapNode(interface=fsl.Merge(dimension='t'),
                       iterfield=['in_files'],
                       name="copemerge")

varcopemerge = pe.MapNode(interface=fsl.Merge(dimension='t'),
                          iterfield=['in_files'],
                          name="varcopemerge")

"""
Use :class:`nipype.interfaces.fsl.L2Model` to generate subject and condition
specific level 2 model design files
"""

level2model = pe.Node(interface=fsl.L2Model(),
                      name='l2model')

"""
Use :class:`nipype.interfaces.fsl.FLAMEO` to estimate a second level model
"""

flameo = pe.MapNode(interface=fsl.FLAMEO(run_mode='fe'), name="flameo",
                    iterfield=['cope_file', 'var_cope_file'])

fixed_fx.connect([(copemerge, flameo, [('merged_file', 'cope_file')]),
                  (varcopemerge, flameo, [('merged_file', 'var_cope_file')]),
                  (level2model, flameo, [('design_mat', 'design_file'),
                                         ('design_con', 't_con_file'),
                                         ('design_grp', 'cov_split_file')]),
                  ])


"""
Set up first-level workflow
---------------------------

"""


def sort_copes(files):
    numelements = len(files[0])
    outfiles = []
    for i in range(numelements):
        outfiles.insert(i, [])
        for j, elements in enumerate(files):
            outfiles[i].append(elements[i])
    return outfiles


def num_copes(files):
    return len(files)

firstlevel = pe.Workflow(name='firstlevel')
firstlevel.connect([(preproc, modelfit, [('highpass.out_file', 'modelspec.functional_runs'),
                                         ('art.outlier_files', 'modelspec.outlier_files'),
                                         ('highpass.out_file', 'modelestimate.in_file')]),
                    (preproc, fixed_fx, [('coregister.out_file', 'flameo.mask_file')]),
                    (modelfit, fixed_fx, [(('conestimate.copes', sort_copes), 'copemerge.in_files'),
                                          (('conestimate.varcopes', sort_copes), 'varcopemerge.in_files'),
                                          (('conestimate.copes', num_copes), 'l2model.num_copes'),
                                          ])
                    ])

