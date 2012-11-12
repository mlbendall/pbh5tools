#################################################################################$$
# Copyright (c) 2011,2012, Pacific Biosciences of California, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this 
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
# * Neither the name of Pacific Biosciences nor the names of its contributors 
#   may be used to endorse or promote products derived from this software 
#   without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY PACIFIC BIOSCIENCES AND ITS CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED 
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL PACIFIC BIOSCIENCES OR ITS 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#################################################################################$$

#!/usr/bin/env python
import os
import sys
import argparse
import logging
import tempfile
import shutil
import pkg_resources

from pbcore.util.ToolRunner import PBMultiToolRunner
import pbcore.util.RecArray as RA

from pbtools.pbh5tools.CmpH5Merge import CmpH5Merger
from pbtools.pbh5tools.CmpH5Compare import CmpH5Compare
from pbtools.pbh5tools.CmpH5Sort import sortCmpH5
from pbtools.pbh5tools.CmpH5Trim import CmpH5Sampler, CmpH5Splitter
from pbtools.pbh5tools.CmpH5Stats import CmpH5Stats
from pbtools.pbh5tools.CmpH5Summary import CmpH5Summary

__version__ = "0.4.1"

class CmpH5ToolsRunner(PBMultiToolRunner):
    def __init__(self):
        desc = ['Toolkit for all command-line tools associated with cmp.h5 file processing.',
                'Notes: For all command-line arguments, default values are listed in [].']
        super(CmpH5ToolsRunner, self).__init__('\n'.join(desc))
        subparsers = self.getSubParsers()

        ########
        # merge
        desc = ['Merge multiple cmp.h5 files. Supports both \'safe\' merging where only cmp.h5',
                'files that contain the same H5Datasets compared to the sedding .cmp.file',
                'will be merged and \'unsafe\' where no such considerations are taken into',
                'account.']
        parser_m = subparsers.add_parser('merge',
                                         help='merge multiple cmp.h5 files',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_m.add_argument('infiles', metavar='input.cmp.h5', nargs='+',
                              help='input filenames')
        parser_m.add_argument('--outFile', dest='outfile', default='out.cmp.h5', 
                              help='output filename [%(default)s]')
        parser_m.add_argument('--forceMerge', dest='forcemerge', action='store_true',
                              help= 'bypass validation of cmp.h5 files before merging and force merge [%(default)s]')
        
        ########
        # sort
        desc = ['Sort cmp.h5 files. If output-file is unspecified the input-file is',
                'overwritten. If there are a number of reference groups then the',
                'indexing processing can occur in parallel.']  
        parser_s = subparsers.add_parser('sort',
                                         help='sort cmp.h5 file',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_s.add_argument('infile', metavar='input.cmp.h5',
                              help='input filename')

        parser_s.add_argument('--outFile', dest='outfile', 
                               help='output filename')
        parser_s.add_argument('--deep', dest='deepsort', action='store_true',
                              help='whether a deep sorting should be conducted, i.e. sort the AlignmentArrays [%(default)s]')
        parser_s.add_argument('--tmpDir', dest='tmpdir', default='/tmp',  
                              help='temporary directory to use when sorting in-place [%(default)s]')
        parser_s.add_argument('--usePythonIndexer', dest='usePythonIndexer', default = False, action='store_true',  
                              help='Whether to use native indexing [%(default)s].')
        parser_s.add_argument('--inPlace', dest='inPlace', default = False, action = 'store_true',
                              help='Whether to make a temporary copy of the original cmp.h5 file before sorting.')

        ########
        # split
        desc = ['Split a cmp.h5 file\'s contents into multiple files.']
        parser_t = subparsers.add_parser('split',
                                         help='split a cmp.h5 file\'s content.',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_t.add_argument('infile', metavar='input.cmp.h5',
                              help='input filename')
        parser_t.add_argument('--outDir', dest='outdir', default='./',  
                              help='output directory to store new cmp.h5 files [%(default)s]')
        parser_t.add_argument('--splitBy', dest='splitby', default='reference',
                              help='reference [%(default)s]') 
        parser_t.add_argument('--fullRefName', dest='fullrefname', action='store_true',
                              help='Use full reference name for naming splits [%(default)s]')

        ########
        # compare
        desc = ['Compare 2 cmp.h5 files for equivalence.']
        parser_c = subparsers.add_parser('compare',
                                         help='compare 2 cmp.h5 files for equivalence',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_c.add_argument('infiles', metavar='input.cmp.h5', nargs=2,
                               help='input filenames')

        ########
        # summarize
        desc = ['Print summary for a cmp.h5 file.']
        parser_z = subparsers.add_parser('summarize',
                                         help='print summary for a cmp.h5 file',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_z.add_argument('infile', metavar='input.cmp.h5',
                               help='input filename')

        ########
        # stats
        desc = ['Print statisics csvs for a cmp.h5 file.']
        parser_stats = subparsers.add_parser('stats',
                                             help='print a csv for a cmp.h5 file',
                                             description='\n'.join(desc),
                                             parents=[self.parser])
        parser_stats.add_argument('--groupBy', metavar='groupBy', 
                                  help='how to group the results, .e.g., movie, reference, subread, molecule', 
                                  default = None)
        parser_stats.add_argument('infile', metavar='input.cmp.h5',
                                  help='input filename')

    def getVersion(self):
        return __version__

    def validateArgs(self):
        if self.args.subName in ['merge', 'compare']:
            t_files = filter(lambda x: not os.path.isfile(x), self.args.infiles)
            if t_files:
                self.parser.error('Input files: [%s], do not exist!' % ','.join(t_files))
        elif self.args.subName in ['summarize', 'tocsv', 'trim', 'sort']:
            if not os.path.isfile(self.args.infile):
                self.parser.error('Input file [%s] does not exist!' % self.args.infile)

    # XXX : These things have different rules about throwing exceptions and returning false
    def run(self):
        if self.args.subName == 'merge':
            CmpH5Merger(self.args.infiles, self.args.outfile, forceMerge=self.args.forcemerge).run()
        elif self.args.subName == 'compare':
            equiv = CmpH5Compare(self.args.infiles[0], self.args.infiles[1]).compare()
            if equiv:
                logging.info('Files contain equivalent content!')
            else:
                logging.info('Files contain NON-equivalent content!')
        elif self.args.subName == 'sort':
            success = sortCmpH5(self.args.infile, self.args.outfile, self.args.tmpdir, 
                                deep=self.args.deepsort, useNative = not self.args.usePythonIndexer,
                                inPlace = self.args.inPlace)
            if not success:
                logging.error('Error during sorting. Exiting! Original file %s has not been modified.' % 
                              self.args.infile)
                raise Exception("Sorting failed")
        elif self.args.subName == 'split':
            CmpH5Splitter(self.args.infile, outDir=self.args.outdir, fullRefName=self.args.fullrefname).run()
        elif self.args.subName == 'summarize':
            CmpH5Summary(self.args.infile).run()
        elif self.args.subName == 'stats':
            CmpH5Stats(self.args.infile, self.args.groupBy).run()
        else:
            raise Exception("Unkown command passed to cmph5tools.py")

if __name__ == '__main__':    
    sys.exit(CmpH5ToolsRunner().start())

        

