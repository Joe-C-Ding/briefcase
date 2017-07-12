# -*- codeing: utf-8 -*-
"""
simulate Microsoft's briefcase
"""
import os
import re
from os.path import isfile, join, isdir, getmtime, relpath, dirname
from pprint import pprint
from shutil import copy2

describe_file = 'briefcase.dsc'


def recursive_listdir(where, result=None, initial=True):
    """
    recursive list all files in the directory `where`, the result will extend to `result`
    """
    if result is None:
        result = []

    local_list = [join(where, f) for f in os.listdir(where)]
    result.extend(filter(isfile, local_list))

    for d in filter(isdir, local_list):
        recursive_listdir(d, result, False)

    if initial:
        result = map(lambda p: relpath(p, where), result)
        return filter(lambda s: not re.search(describe_file + '$', s), result)


def find_briefcase():
    return [d for d in os.listdir(os.getcwd())
            if isdir(d) and isfile(join(d, describe_file))]


def extract_location(where):
    try:
        with open(join(where, describe_file)) as f:
            dirs = [d.strip() for d in f]
    except OSError:
        return []

    return list(filter(isdir, dirs))


def update(where):
    orig_dir = extract_location(where)
    if not orig_dir:
        return
    orig_dir = orig_dir[0]
    orig = set(recursive_listdir(orig_dir))
    dest = set(recursive_listdir(where))

    up = dest - orig
    down = orig - dest

    check = dest & orig
    up |= {f for f in check if getmtime(join(orig_dir, f)) < getmtime(join(where, f))}
    down |= {f for f in check if getmtime(join(orig_dir, f)) > getmtime(join(where, f))}

    if up:
        print("uploading:")
        pprint(up, indent=4)

        do = input("perform([y]/n)? ")
        if do == '' or do.lower() == 'y':
            copy_files(where, orig_dir, up)
    if down:
        print("downloading:")
        pprint(down, indent=4)

        do = input("perform([y]/n)? ")
        if do == '' or do.lower() == 'y':
            copy_files(orig_dir, where, down)


def copy_files(orig, where, files):
    """
    copy `files` from `orig` to `where`
    """
    total = len(files)
    for i, f in enumerate(files):
        print('copying {} / {}'.format(i + 1, total))
        folder = join(where, dirname(f))
        os.makedirs(folder, exist_ok=True)
        copy2(join(orig, f), folder)


if __name__ == '__main__':
    briefcase = find_briefcase()
    for b in briefcase:
        update(b)
