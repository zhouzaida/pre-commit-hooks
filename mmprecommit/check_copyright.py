#!/usr/bin/env python3

import argparse
import os
import os.path as osp
from typing import List

HEADER = 'Copyright (c) OpenMMLab. All rights reserved.\n'

HEADER_KEYWORDS = {'Copyright', 'License'}


def is_contain_header(lines: List[str]) -> bool:
    for line in lines:
        if len(HEADER_KEYWORDS.intersection(set(line.split(' ')))):
            return True
    return False


def parse_args():
    parser = argparse.ArgumentParser(description='Add header to files')
    parser.add_argument('src', type=str, help='source files to add header')
    parser.add_argument(
        '--exclude_dirs', nargs='*', type=str, default=[], help='exclude folder')
    parser.add_argument(
        '--include_suffixes',
        nargs='+',
        type=str,
        default=['.py'],
        help='header will be added to files with suffix')
    args = parser.parse_args()
    return args


def format_args(args):
    r"""Check Check the correctness of args and format them.
    """

    suffix_list = ['.py', '.h', '.cpp', '.cu', '.cuh', '.hpp']

    # remove possible duplication
    args.exclude_dirs = list(set(args.exclude_dirs))
    args.include_suffixes = list(set(args.include_suffixes))

    # check the correctness and format args
    if not isinstance(args.src, str) or not osp.exists(args.src):
        raise ValueError(f"src {args.src} is not a right path")
    else:
        args.src = osp.abspath(args.src)
    for i, dir in enumerate(args.exclude_dirs):
        if not isinstance(dir, str) or not osp.exists(dir):
            raise ValueError(f"{dir} in exclude_dirs is not a right path")
        else:
            args.exclude_dirs[i] = osp.abspath(dir)
    for suffix in args.include_suffixes:
        if suffix not in suffix_list:
            raise ValueError(
                f"{suffix} in include_suffixes is not a right suffix")
    return args


def get_filepath_list(args) -> List[str]:
    r"""Get all file paths that match the args.
    """

    filepath_list = []
    for root, dirs, files in os.walk(args.src):
        is_exclude = False
        for dir in args.exclude_dirs:
            if root.startswith(dir):
                is_exclude = True
                break
        if is_exclude:
            continue
        else:
            for file in files:
                for suffix in args.include_suffixes:
                    if file.endswith(suffix):
                        filepath = osp.join(root, file)
                        filepath_list.append(filepath)
                        break
    return filepath_list


def add_copyright(filepath_list: List[str]):
    r"""Add copyright for files which lack copyright
    """
    for filepath in filepath_list:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        if not is_contain_header(lines):
            with open(filepath, 'w') as f:
                prefix = '# ' if osp.splitext(filepath)[1] == '.py' else '// '
                f.writelines([prefix + HEADER] + lines)


def main():
    args = parse_args()
    try:
        args = format_args(args)
    except ValueError as e:
        print(repr(e))
        return 1
    filepath_list = get_filepath_list(args)
    add_copyright(filepath_list)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
