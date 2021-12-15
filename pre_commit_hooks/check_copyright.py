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


def check_args(include: List[str], exclude: List[str], suffix: List[str]):
    """Check the correctness of args and format them."""

    suffixes = ['.py', '.h', '.cpp', '.cu', '.cuh', '.hpp']

    # remove possible duplication
    include = list(set(include))
    exclude = list(set(exclude))
    suffix = list(set(suffix))

    # check the correctness and format args
    for i, dir in enumerate(include):
        if not osp.exists(dir):
            raise FileNotFoundError(f'Include {dir} can not be found')
        else:
            include[i] = osp.abspath(dir)
    for i, dir in enumerate(exclude):
        if not osp.exists(dir):
            raise FileNotFoundError(f'Exclude {dir} can not be found')
        else:
            exclude[i] = osp.abspath(dir)
    for suf in suffix:
        if suf not in suffixes:
            raise FileNotFoundError(f'Suffix {suf} can not be found')
    return include, exclude, suffix


def get_filepaths(include: List[str], exclude: List[str],
                  suffix: List[str]) -> List[str]:
    """Get all file paths that match the args."""

    filepaths = []
    for dir in include:
        for root, dirs, files in os.walk(dir):
            is_exclude = False
            for dir in exclude:
                if root.startswith(dir):
                    is_exclude = True
                    break
            if is_exclude:
                continue
            else:
                for file in files:
                    for suf in suffix:
                        if file.endswith(suf):
                            filepath = osp.join(root, file)
                            filepaths.append(filepath)
                            break
    return filepaths


def check_copyright(include: List[str], exclude: List[str],
                    suffix: List[str]) -> int:
    """Add copyright for those files which lack copyright.

    Args:
        include: Directory to add copyright.
        exclude: Exclude directory.
        suffix: Copyright will be added to files with suffix.

    returns:
        Returns 0 if no file is missing copyright, otherwise returns 1.
    """
    rev = 0
    try:
        include, exclude, suffix = check_args(include, exclude, suffix)
    except FileNotFoundError as e:
        print(repr(e))
        return 1
    else:
        filepaths = get_filepaths(include, exclude, suffix)
        for filepath in filepaths:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if not has_copyright(lines):
                with open(filepath, 'w', encoding='utf-8') as f:
                    prefix = '# ' if osp.splitext(
                        filepath)[1] == '.py' else '// '
                    f.writelines([prefix + HEADER] + lines)
                    rev = 1
    return rev


def main():
    args = parse_args()
    return check_copyright(args.include, args.exclude, args.suffix)


if __name__ == '__main__':
    raise SystemExit(main())
