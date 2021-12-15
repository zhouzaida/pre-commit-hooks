import os
import os.path as osp

from pre_commit_hooks.check_copyright import check_copyright


def test_copyright():
    include = ['./tests/data']
    exclude = ['./tests/data/exclude']
    suffix = ['.py', '.cpp', '.h', '.cu', '.cuh', '.hpp']
    assert check_copyright(include, exclude, suffix) == 1

    for dir in include:
        for root, dirs, files in os.walk(dir):
            for file in files:
                filepath = osp.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if root not in exclude:
                        assert lines[0].split(' ').count('Copyright') > 0
                    else:
                        assert lines[0].split(' ').count('Copyright') == 0
                with open(filepath, 'w', encoding='utf-8') as f:
                    if root not in exclude:
                        f.writelines(lines[1:])
                    else:
                        f.writelines(lines)
