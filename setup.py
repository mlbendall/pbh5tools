from setuptools import setup, Extension, find_packages

import os
import sys

vFile = 'src/python/pbtools/pbh5tools/_version.py'

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
    name = 'pbtools.pbh5tools',
    version=_ReadVersion,
    author='Pacific Biosciences',
    author_email='devnet@pacificbiosciences.com',
    license='LICENSE.txt',
    scripts = ['src/python/bash5tools.py', 
               'src/python/cmph5tools.py'],
    packages = find_packages('src/python'),  
    package_dir = {'':'src/python'},
    namespace_packages = ['pbtools'],
    ext_modules=[Extension('pbtools/pbh5tools/ci', ['src/C/ci.c'], 
                           extra_compile_args=["-O3","-shared"])], 
    zip_safe = False,
    install_requires=[
        'pbcore >= 0.1',
        'numpy >= 1.6.0',
        'h5py >= 1.3.0'
        ]
    )
