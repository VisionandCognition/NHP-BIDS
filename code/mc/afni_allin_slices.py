#!/usr/bin/env python3

# Based on mc-afni-v4.2.2.sh.

import subprocess as sp
import argparse
import os
import pdb

from collections import deque

from nipype.interfaces.base import (
    TraitedSpec,
    CommandLineInputSpec,
    CommandLine,
    Directory,
    File,
    isdefined,
)

import traits.api as traits


def defined_in(key, d):
    return key in d.keys() and d[key] is not None


def print_run(cmd, args=None):
    print('cmd=' + cmd)
    if args is not None:
        print('args=' + str(args))
        cmd = cmd % args
    sp.check_call(cmd, shell=True)


def nii_val(nii_file, var):
    val = sp.check_output(
        ['fslval', nii_file, var]).decode('UTF-8').strip()
    return val


def register(**kwargs):
    if not defined_in('tmpdir', kwargs):
        # defined for NiPype
        kwargs['tmpdir'] = os.getcwd()
        print(kwargs['tmpdir'])

    if not defined_in('out_init_mc', kwargs):
        kwargs['out_init_mc'] = os.path.join(
            "%(tmpdir)s" % kwargs,
            'func_3dAllineate.nii.gz')

    if not defined_in('TR', kwargs):
        kwargs['TR'] = nii_val(kwargs['func'], 'pixdim4')
        print('TR = %(TR)s' % kwargs)

    if not defined_in('1Dparam_save', kwargs):
        kwargs['1Dparam_save'] = 'reg'

    if not defined_in('1Dmatrix_save', kwargs):
        kwargs['1Dmatrix_save'] = 'reg'

    if not defined_in('ref', kwargs):
        kwargs['ref'] = '%(tmpdir)s/func_median.nii.gz' % kwargs

    if not os.path.isfile(kwargs['ref']):
        print_run('fslmaths %(func)s -Tmedian %(ref)s' % kwargs)

    if not os.path.isfile(kwargs['out_init_mc']):
        print("\nIn: %s" % os.getcwd())
        print("Did not find %(out_init_mc)s." % kwargs)
        print_run(
            '3dAllineate -weight "%(weights)s" '
            '-base %(ref)s '
            '-source "%(func)s" '
            '-prefix "%(out_init_mc)s" '
            '-1Dparam_save %(1Dparam_save)s '
            '-1Dmatrix_save %(1Dmatrix_save)s ',
            kwargs)

    sp.check_call('fslslice "%(ref)s" "%(tmpdir)s/ref"' % kwargs, shell=True)
    sp.check_call(
        'fslslice "%(weights)s" "%(tmpdir)s/weights"' %
        kwargs, shell=True)

    sp.check_call(
        'fslsplit "%(out_init_mc)s" "%(tmpdir)s/func_time_"' % kwargs,
        shell=True)

    processes = deque()
    for t in range(1000):
        print('vol=%d' % t)
        t_args = kwargs.copy()
        t_args['t'] = t
        t_args['func_time'] = "%(tmpdir)s/func_time_%(t)04d" % (t_args)

        t_args['dest_prefix'] = "%(tmpdir)s/reg_time_%(t)04d" % t_args
        if os.path.isfile('%(dest_prefix)s+orig.BRIK' % t_args):
            continue

        if not os.path.isfile('%(func_time)s.nii.gz' % t_args):
            print('image %(func_time)s.nii.gz does not exist!' % t_args)
            break

        sp.check_call(
            'fslslice "%(func_time)s" "%(func_time)s"' %
            t_args, shell=True)

        for i in range(1000):
            i_args = t_args.copy()
            i_args['i'] = i
            # input files
            i_args['func'] = "%(func_time)s_slice_%(i)04d.nii.gz" % i_args
            i_args['w'] = "%(tmpdir)s/weights_slice_%(i)04d.nii.gz" % i_args
            i_args['ref'] = "%(tmpdir)s/ref_slice_%(i)04d.nii.gz" % i_args

            # output files
            i_args['destti'] = (
                "%(tmpdir)s/reg_time_%(t)04d_slice_%(i)04d.nii.gz" % i_args)

            if not os.path.isfile(i_args['func']):
                print('func %(func)s does not exist' % i_args)
                break
            if not os.path.isfile(i_args['w']):
                print('w %(w)s does not exist' % i_args)
                break
            if not os.path.isfile(i_args['ref']):
                print('ref %(ref)s does not exist' % i_args)
                break

            # print('Running 3dAllineate for slice %(i)d ' % i_args)
            if not os.path.isfile(i_args['destti']):
                cmd = [
                    '3dAllineate',
                    '-onepass',
                    '-nwarp', i_args['nwarp'],
                    '-fineblur', '%0.2f' % i_args['fineblur'],
                    '-weight', i_args['w'],
                    '-base', i_args['ref'],
                    '-source', i_args['func'],
                    '-prefix', i_args['destti']]
                print(' '.join(cmd))
                processes.append(
                    sp.Popen(cmd))

            if len(processes) > 10:  # limit parallelism
                processes.popleft().wait()

        while len(processes) > 0:
            processes.popleft().wait()

        # Delete temporary files
        # rm ${func_time}_slice_????.nii.gz

        #if not os.path.isfile('%(dest_prefix)s+orig.BRIK' % t_args):
        print_run(
            "3dZcat -prefix %(dest_prefix)s "
            "%(dest_prefix)s_slice_????.nii.gz",
            t_args)
        # rm ${dest_prefix}_slice_????.nii.gz
        print_run("rm %(dest_prefix)s_slice_????.nii.gz" % t_args)


    print_run("rm %(tmpdir)s/ref_slice_????.nii.gz", kwargs)
    print_run("rm %(tmpdir)s/func_time_????.nii.gz", kwargs)
    print_run("rm %(tmpdir)s/weights_slice_????.nii.gz", kwargs)

    kwargs['dest_prefix'] = "%(tmpdir)s/reg" % kwargs
    if not os.path.isfile("%(dest_prefix)s.nii" % kwargs):
        # print_run("3dZcat -prefix %(dest_prefix)s %(dest_prefix)s_"
        #           "slice_????.nii.gz", kwargs)
        print_run("3dTcat -tr %(TR)s -prefix %(dest_prefix)s "
                  "%(dest_prefix)s_time_????+orig.BRIK", kwargs)
        print_run("3dAFNItoNIFTI -prefix %(dest_prefix)s %(dest_prefix)s+orig",
                  kwargs)

    if not os.path.isfile("%(out)s"):
        print_run("fslmaths %(dest_prefix)s.nii %(out)s", kwargs)

#    rm $DEST/*.BRIK
#    rm $DEST/*.HEAD
#
    print_run("fslmaths %(dest_prefix)s.nii -sub %(ref)s -abs "
              "-mas %(weights)s %(tmpdir)s/absdiff.nii.gz", kwargs)
    print_run("fslmaths %(tmpdir)s/absdiff.nii.gz -Tmean "
              "%(tmpdir)s/absdiff_mean.nii.gz", kwargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Performs non-linear slice-by-slice registration '
        '(base on mc-afni-v4.2.2.sh).')

    parser.add_argument(
        '--func', '-i', required=True, type=str,
        help='Functional image with motion and field distortions.')
    parser.add_argument(
        '-o', '--out', required=True, type=str,
        help='Motion registered image.')
    parser.add_argument(
        '-r', '--ref', required=True, type=str,
        help='The reference / base functional to register to.')
    parser.add_argument(
        '--weights', required=True, type=str,
        help='The weights or mask used for registering.')

    parser.add_argument(
        '--tmpdir', type=str, help='Temporary directory.')

    parser.add_argument('--1Dparam_save', type=str)
    parser.add_argument('--1Dmatrix_save', type=str)

    parser.add_argument(
        '--out_init_mc', type=str,
        help='Initial motion registration (linear, not slice-by-slice).')

    parser.add_argument('--fineblur', type=float, default=0.5)
    parser.add_argument(
        '--nwarp', type=str, help='Motion registered image.',
        default='heptic',
        choices=['cubic', 'quintic', 'heptic', 'nonic'])

    args = parser.parse_args()

    register(**vars(args))


class AFNIAllinSlicesInputSpec(CommandLineInputSpec):
    """ The inputspec specifies all the parameters of the command.
    """
    in_file = File(desc="Functional without motion correction",
                   exists=True, mandatory=True,
                   argstr="--func %s")
    # ref_file is generated as the median of the functional
    ref_file = File(
        desc="Reference / base image to register to",
        name_source=['in_file'],
        name_template="%s_Tmedian",
        keep_extension=True,
        argstr="--ref %s")
    in_weight_file = File(
        argstr='--weights %s',
        exists=True, mandatory=True,
    )
    working_dir = Directory(argstr='--tmpdir %s')

    fineblur = traits.Float(argstr='--fineblur %f')

    # --------------------------------------- Output / generated files --------
    out_file = File(
        argstr='--out %s',
        hash_files=False,
        name_source=['in_file'],
        name_template="%s_mc",
        keep_extension=True,
    )
    out_init_mc = File(
        argstr='--out_init_mc %s',
        hash_files=False,
        name_source=['in_file'],
        name_template="%s_prelim-mc",
        keep_extension=True,
    )
    oned_file = File(
        argstr='--1Dparam_save %s',
        hash_files=False,
        name_source=['in_file'],
        name_template="%s.param.1D",
    )
    oned_matrix_save = File(
        argstr='--1Dmatrix_save %s',
        hash_files=False,
        name_source=['in_file'],
        name_template="%s.aff12.1D",
    )


class AFNIAllinSlicesOutputSpec(TraitedSpec):
    out_file = File(desc="Motion corrected / registered image", exists=True)
    out_init_mc = File(
        desc="Preliminary whole-brain motion correction",
        exists=True)
    oned_file = File(exists=True)
    oned_matrix_save = File(exists=True)
    ref_file = File(exists=True)


class AFNIAllinSlices(CommandLine):
    """ NiPype wrapper """
    input_spec = AFNIAllinSlicesInputSpec
    output_spec = AFNIAllinSlicesOutputSpec
    _cmd = 'afni_allin_slices.py'

    # def run(self, updatehash=False):
    #     import pdb
    #     pdb.set_trace()
    #     super(self, AFNIAllinSlices).run(updatehash=updatehash)
