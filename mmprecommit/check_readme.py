#!/usr/bin/env python3

import argparse
import os.path as osp
import modelindex
import logging
import re
import re

from modelindex.models import ModelIndex

abstract_start_matcher = r".*\[ABSTRACT\].*"
abstract_start_pattern = re.compile(abstract_start_matcher)

icon_start_matcher = r".*\[IMAGE\].*"
icon_start_pattern = re.compile(icon_start_matcher)
src_matcher = r".*src=.*"
src_line_pattern = re.compile(src_matcher)
src_link_pattern = re.compile(r"\".*?\"")

def extrace_readme(readmePath: str):
    abstract = ""
    image = ""

    abstract_start_search = False
    image_start_search = False
    if osp.exists(readmePath):
        with open(readmePath, encoding="utf-8") as file:
            line = file.readline()
            while line:
                ## extract abstract
                if abstract_start_search and not abstract:
                    if not line.strip() == "":
                        abstract = line
                if not abstract_start_search:
                    abstract_start_search = abstract_start_pattern.match(line)

                ## extract image
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

def handle_collection_name(name: str):
    # handler for mmpose
    display_name_pattern = re.compile(r'\[(.*?)\]')
    display_name = re.findall(display_name_pattern, name)
    if display_name:
        name = display_name[0]

    return name

def check_algorithm(model_zoo_index: ModelIndex):

    for collection in model_zoo_index.collections:
        name = collection.name
        display_name = handle_collection_name(name)

        readme_path = f"./{collection.readme}"
        abstract, image = extrace_readme(readme_path)

        if not abstract:
            logging.warning(f"Abstract is empty, algorithm name: {display_name}")
            exit(1)

        if not image:
            logging.warning(f"Image is empty, algorithm name: {display_name}")
            exit(1)

        logging.info({
            'name' : display_name,
            'introduction': abstract,
            'image': image,
        })

def load_model_zoo(local_repo_path: str):
    model_index_path = f"{local_repo_path}/model-index.yml"
    mi = modelindex.load(model_index_path)

    return mi

def parse_args():
    parser = argparse.ArgumentParser(description='Check README.md')
    parser.add_argument(
        '--log-level',
        help='set log level',
        default='WARNING')

    return parser.parse_args()

def main():
    args = parse_args()
    log_level = args.log_level
    logging.getLogger().setLevel(log_level)

    model_zoo_index = load_model_zoo(".")
    check_algorithm(model_zoo_index)

if __name__ == '__main__':
    raise SystemExit(main())