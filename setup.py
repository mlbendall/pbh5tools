from setuptools import setup, Extension, find_packages

import os
import sys

#if os.system("make -C src/C all"):
#    sys.exit(1)

setup(
    name = 'pbtools.pbh5tools',
    version='0.4.0',
    author='Pacific Biosciences',
    author_email='devnet@pacificbiosciences.com',
    license='LICENSE.txt',
    scripts = ['src/python/bash5tools.py', 
               'src/python/cmph5tools.py'],
    packages = find_packages('src/python'),  
    package_dir = {'':'src/python'},
    namespace_packages = ['pbtools'],
    #data_files = [('pbtools/pbh5tools', ['src/C/build/ci.so'])],
    ext_modules=[Extension('pbtools/pbh5tools/ci', ['src/C/ci.c'], extra_compile_args=["-O3","-shared"])], 
    zip_safe = False,
    install_requires=[
        'pbcore >= 0.1',
        'numpy >= 1.6.0',
        'matplotlib >= 1.0.1',
        'h5py >= 1.3.0'
        ]
    )
