#!/usr/bin/env python
import os
import shutil
import sys

ORIGINAL_PACKAGE_NAME = 'org.bouncycastle'
LIBS = ('core', 'jce', 'pkix', 'pg', 'prov')

def copy_and_rename(source, destination, package_name):
    chunks_orig = ORIGINAL_PACKAGE_NAME.split('.')
    chunks_new = package_name.split('.')
    bc_orig = os.path.join(destination, *chunks_orig)
    if os.path.exists(bc_orig):
        stump = chunks_new[:-1]
        stump_dir = os.path.join(destination, *stump)
        if not os.path.exists(stump_dir):
            os.makedirs(stump_dir)
        shutil.move(bc_orig, os.path.join(stump_dir, chunks_new[-1]))
        for i in xrange(len(chunks_orig) - 1):
            rest_dir = os.path.join(destination, *chunks_orig[:-1 - i])
            try:
                os.rmdir(rest_dir)
            except OSError:
                break

    for (dirpath, unused_dirnames, filenames) in os.walk(destination):
        for fn in filenames:
            ext = fn.split('.')[-1]
            if ext not in ['java']:
                continue
            fullpath = os.path.join(dirpath, fn)
            data = file(fullpath).read()
            data = data.replace(ORIGINAL_PACKAGE_NAME, package_name)
            data = data.replace(ORIGINAL_PACKAGE_NAME.replace('.', '/'),
                                package_name.replace('.', '/'))
            file(fullpath, 'w').write(data)

def copy_and_rename_all(package_name):
    for lib in LIBS:
        try:
            shutil.rmtree(os.path.join(lib, 'src/main'))
        except OSError:
            pass

    for lib in LIBS:
        for (dirpath, dirnames, unused_filenames) in os.walk(os.path.join('bc-java', lib)):
            if not dirpath.endswith('src/main'):
                continue

            destination = os.path.join(lib, 'src')
            if not os.path.exists(destination):
                os.makedirs(destination)
            destination = os.path.join(destination, 'main')
            shutil.copytree(dirpath, destination)

            for d in dirnames:
                copy_and_rename(os.path.join(dirpath, d), os.path.join(destination, d), package_name)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        package_name = sys.argv[1]
    else:
        package_name = 'org.bouncycastle2'
    print 'Repacking org.bouncycastle to', package_name
    copy_and_rename_all(package_name)
