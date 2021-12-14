#!/usr/bin/env python3

import argparse
import os
import os.path as osp
from typing import List

HEADER = 'Copyright (c) OpenMMLab. All rights reserved.\n'

HEADER_KEYWORDS = {'Copyright', 'License'}


def has_copyright(lines: List[str]) -> bool:
    for line in lines:
        if not HEADER_KEYWORDS.isdisjoint(set(line.split(' '))):
            return True
    return False


def parse_args():
    parser = argparse.ArgumentParser(description='Add copyright to files')
    parser.add_argument(
        'include', type=str, nargs='+', help='directory to add copyright')
    parser.add_argument(
        '--exclude', nargs='*', type=str, default=[], help='exclude directory')
    parser.add_argument(
        '--suffix',
        nargs='*',
        type=str,
        default=['.py'],
        help='copyright will be added to files with suffix')
    args = parser.parse_args()
    return args


def check_args(args) -> int:
    """Check the correctness of args and format them."""

    suffixes = ['.py', '.h', '.cpp', '.cu', '.cuh', '.hpp']

    # remove possible duplication
    args.include = list(set(args.include))
    args.exclude = list(set(args.exclude))
    args.suffix = list(set(args.suffix))

    # check the correctness and format args
    for i, dir in enumerate(args.include):
        if not osp.exists(dir):
            raise FileNotFoundError(f'Include {dir} can not be found')
        else:
            args.include[i] = osp.abspath(dir)
    for i, dir in enumerate(args.exclude):
        if not osp.exists(dir):
            raise FileNotFoundError(f'Exclude {dir} can not be found')
        else:
            args.exclude[i] = osp.abspath(dir)
    for suffix in args.suffix:
        if suffix not in suffixes:
            raise FileNotFoundError(f'Suffix {suffix} can not be found')


def get_filepaths(args) -> List[str]:
    """Get all file paths that match the args."""

    filepaths = []
    for dir in args.include:
        for root, dirs, files in os.walk(dir):
            is_exclude = False
            for dir in args.exclude:
                if root.startswith(dir):
                    is_exclude = True
                    break
            if is_exclude:
                continue
            else:
                for file in files:
                    for suffix in args.suffix:
                        if file.endswith(suffix):
                            filepath = osp.join(root, file)
                            filepaths.append(filepath)
                            break
    return filepaths


def check_copyright(filepaths: List[str]) -> int:
    """Add copyright for those files which lack copyright.

    Args:
       filepaths (list[str]): File paths to be checked.

    returns:
        int: Returns 0 if no file is missing copyright, otherwise returns 1.
    """
    rev = 0
    for filepath in filepaths:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if not has_copyright(lines):
            with open(filepath, 'w', encoding='utf-8') as f:
                prefix = '# ' if osp.splitext(filepath)[1] == '.py' else '// '
                f.writelines([prefix + HEADER] + lines)
                rev = 1
    return rev


def main():
    args = parse_args()
    try:
        check_args(args)
    except FileNotFoundError as e:
        print(repr(e))
        return 1
    filepaths = get_filepaths(args)
    return check_copyright(filepaths)


if __name__ == '__main__':
    raise SystemExit(main())
