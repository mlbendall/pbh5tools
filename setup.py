from setuptools import setup, Extension, find_packages

import os
import sys

vFile = 'pbh5tools/_version.py'

if os.path.exists(vFile):
    lines = open(vFile, 'r').read().splitlines()
    for line in lines:
        elts = line.split('=')
        elts = [e.strip() for e in elts]
        if len(elts) == 2 and elts[0] == '__version__':
            _ReadVersion = elts[1].replace('\'', '').replace('\"', '')
            break
else:
    _ReadVersion = '0.0.0'

setup(
    name = 'pbh5tools',
    version=_ReadVersion,
    author='Pacific Biosciences',
    author_email='devnet@pacificbiosciences.com',
    license=open('LICENSES.txt').read(),
    scripts = ['bin/bash5tools.py',
               'bin/cmph5tools.py'],
    packages = find_packages("."),
    package_dir = {'':'.'},
    ext_modules=[Extension('pbh5tools/ci', ['pbh5tools/ci.c'],
                           extra_compile_args=["-O3","-shared"])],
    zip_safe = False,
    install_requires=[
        'pbcore >= 0.8.0',
        'numpy >= 1.6.0',
        'h5py >= 1.3.0'
        ]
    )
