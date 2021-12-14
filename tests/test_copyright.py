import os
import os.path as osp


def test_copyright():

    include = './tests/data'
    exclude = './tests/data/exclude'

    for root, dirs, files in os.walk(include):
        for file in files:
            filepath = osp.join(root, file)
            with open(filepath, 'r+', encoding='utf-8') as f:
                lines = f.readlines()
                if root != exclude:
                    assert lines[0].split(' ').count('Copyright') > 0
                    f.seek(0, 0)
                    f.writelines(lines[1:])
                else:
                    assert lines[0].split(' ').count('Copyright') == 0
