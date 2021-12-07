#!/usr/bin/env python3

import argparse
import os.path as osp
import pprint
import re
from typing import Tuple

import yaml

abstract_start_matcher = r'.*\[ABSTRACT\].*'
abstract_start_pattern = re.compile(abstract_start_matcher)

icon_start_matcher = r'.*\[IMAGE\].*'
icon_start_pattern = re.compile(icon_start_matcher)
src_matcher = r'.*src=.*'
src_line_pattern = re.compile(src_matcher)
src_link_pattern = re.compile(r"\".*?\"")


def extract_readme(readmePath: str) -> Tuple[str, str]:
    abstract = ''
    image = ''

    abstract_start_search = False
    image_start_search = False
    if osp.exists(readmePath):
        with open(readmePath, encoding='utf-8') as file:
            line = file.readline()
            while line:
                # extract abstract
                if abstract_start_search and not abstract:
                    if not line.strip() == '':
                        abstract = line
                if not abstract_start_search:
                    abstract_start_search = abstract_start_pattern.match(line)

                # extract image
                if image_start_search and not image:
                    src_group = src_line_pattern.search(line)
                    if src_group:
                        link_group = src_link_pattern.search(src_group.group())
                        if link_group:
                            image = link_group.group()[1:-1]
                if not image_start_search:
                    image_start_search = icon_start_pattern.match(line)
                line = file.readline()

    return abstract, image


def handle_collection_name(name: str) -> str:
    # handler for mmpose
    display_name_pattern = re.compile(r'\[(.*?)\]')
    display_name = re.findall(display_name_pattern, name)
    if display_name:
        name = display_name[0]

    return name


def full_filepath(path: str, cur_filepath: str = None):
    if cur_filepath is not None:
        dirname = osp.dirname(cur_filepath)
        if dirname:
            path = osp.join(dirname, path)

    return path


def load_any_file(path: str):

    if not osp.exists(path):
        raise FileNotFoundError(f"File '{path}' does not exist.")

    with open(path, 'r') as f:
        raw = yaml.load(f, Loader=yaml.SafeLoader)

    return raw


def load_model_zoo(model_index_path: str = 'model-index.yml'):
    """load meta file."""

    model_index_data = load_any_file(model_index_path)

    # make sure the input is a dict
    if not isinstance(model_index_data, dict):
        raise ValueError(
            f"Expected the file '{model_index_path}' to contain a dict, \
                but it doesn't.")

    imp = model_index_data['Import']

    collections = []
    for import_file in imp:
        import_file = full_filepath(import_file, model_index_path)
        meta_file_data = load_any_file(import_file)
        col = meta_file_data['Collections']
        collections.extend(col)

    return collections


def check_algorithm(model_index_path: str = 'model-index.yml',
                    dry_run: bool = False,
                    debug: bool = False) -> int:

    validate_pass = 0
    try:
        collections = load_model_zoo(model_index_path)

        for collection in collections:
            name = collection['Name']
            display_name = handle_collection_name(name)

            readme_path = full_filepath(collection['README'], model_index_path)
            abstract, image = extract_readme(readme_path)

            if not abstract:
                print(f'Abstract is empty, algorithm name: {display_name}, \
                        {readme_path}')
                validate_pass = 1

            if not image:
                print(f'Image is empty, algorithm name: {display_name}, \
                        {readme_path}')
                validate_pass = 1

            if debug:
                pprint.pprint({
                    'name': display_name,
                    'readmePath': readme_path,
                    'introduction': abstract,
                    'image': image,
                })
    except (FileNotFoundError, ValueError) as e:
        if debug:
            print(e.message)
        validate_pass = 1

    if dry_run:
        return 0

    return validate_pass


def main():
    parser = argparse.ArgumentParser(description='Check algorithm readme')
    parser.add_argument(
        '--model-index',
        default='model-index.yml',
        help='model-index file path')
    parser.add_argument('--dry-run', action='store_true', help='Just dry run')
    parser.add_argument(
        '--debug', action='store_true', help='Print debug info')
    args = parser.parse_args()

    return check_algorithm(args.debug, args.model_index, args.dry_run)


if __name__ == '__main__':
    raise SystemExit(main())
