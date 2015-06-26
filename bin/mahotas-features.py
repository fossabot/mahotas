#!/usr/bin/env python

import sys
from os import path
import numpy as np
import mahotas as mh
import argparse

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
LIGHT_PURPLE = '\033[94m'
PURPLE = '\033[95m'
END = '\033[0m'

def print_error(text, color=True):
    '''Prints error message

    Arguments
    ---------
    text : str
        Error message
    color : bool, optional
        Whether to print in colour.
    '''
    if color and sys.stderr.isatty():
        sys.stderr.write("{}ERROR: {}{}\n".format(RED, text, END))
    else:
        sys.stderr.write("ERROR: {}\n".format(text))


def read_bw(fname, options):
    '''Read image `fname` as greyscale

    Parameters
    ----------
    fname : str, file-name
    options : argparse result

    Returns
    -------
    image : ndarray
        Two dimensional ndarray
    '''
    im = mh.imread(fname)
    if im.ndim == 2:
        return im
    if im.ndim == 3:
        if options.convert_to_bw == 'max' or im.ptp(2).max() == 0:
            # This is a greyscale image, saved as colour
            return im.max(2)
        if options.convert_to_bw == 'yes':
            return mh.colors.rgb2grey(im, dtype=np.uint8)
    print_error("{} is not a greyscale image (and --convert-to-bw was not specified)".format(fname), not options.no_color)
    sys.exit(1)

def main():
    sys.stderr.write(mh.citation(print_out=False, short=True))
    sys.stderr.write('\n\n')
    parser = argparse.ArgumentParser(
            description='Compute features using mahotas')
    parser.add_argument(
                    'fnames', metavar='input_file_name', nargs='+', type=str,
                            help='Image files names')
    parser.add_argument(
                    '--output', default='features.tsv', type=str,
                            help='Output file for feature files')
    parser.add_argument(
                    '--clobber', default=False, action='store_true',
                            help='Overwrite output file (if it exists)')
    parser.add_argument(
                    '--convert-to-bw', default='no',
                    help='Convert color images to greyscale.\nAcceptable values:\n\tno: raises an error (default)' +
                        '\n\tmax: use max projection' +
                        '\n\tyes: use rgb2gray')
    parser.add_argument(
                    '--no-color', default=False, action='store_true',
                            help='Do not print in color (for error and warning messages)')
    parser.add_argument(
                    '--haralick', default=False, action='store_true',
                            help='Compute Haralick features')
    args = parser.parse_args()
    if not args.haralick:
        sys.stderr.write('''\
No features selected. Doing nothing.

For example, use --haralick switch to compute Haralick features\n''')
        sys.exit(1)

    if not args.clobber and path.exists(args.output):
        print_error('Output file ({}) already exists. Refusing to overwrite results without --clobber argument.'.format(args.output))
        sys.exit(2)
    output = open(args.output, 'w')
    colnames = []
    first = True
    for fname in args.fnames:
        cur = []
        im = read_bw(fname, args)
        if args.haralick:
            har = mh.features.haralick(im, return_mean_ptp=True)
            cur.append(har)
            if first:
                hlabels = mh.features.texture.haralick_labels[:-1]
                colnames.extend(["mean:{}".format(ell) for ell in hlabels])
                colnames.extend(["ptp:{}".format(ell) for ell in hlabels])

        if first:
            for cname in colnames:
                output.write("\t")
                output.write(cname)
            output.write("\n")
            first = False
        for fs in cur:
            output.write(fname)
            for f in fs:
                output.write("\t")
                output.write('{:.8}'.format(f))
            output.write('\n')
    output.close()

if __name__ == '__main__':
    main()