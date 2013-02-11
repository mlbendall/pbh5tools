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
from pbtools.pbh5tools.PBH5ToolsException import PBH5ToolsException

from pbtools.pbh5tools.CmpH5Select import cmpH5Select
from pbtools.pbh5tools.CmpH5Merge import cmpH5Merge
from pbtools.pbh5tools.CmpH5Sort import cmpH5Sort
from pbtools.pbh5tools.CmpH5Stats import cmpH5Stats
from pbtools.pbh5tools.CmpH5Compare import cmpH5Equal, cmpH5Summarize

__p4revision__ = "$Revision$"
__p4change__ = "$Change$"
revNum = int(__p4revision__.strip("$").split(" ")[1].strip("#"))
changeNum = int(__p4change__.strip("$").split(":")[-1])
__version__ = "%s-r%d-c%d" % ( pkg_resources.require("pbtools.pbh5tools")[0].version, 
                               revNum, changeNum )

class CmpH5ToolsRunner(PBMultiToolRunner):
    def __init__(self):
        desc = ['Toolkit for command-line tools associated with cmp.h5 file processing.',
                'Notes: For all command-line arguments, default values are listed in [].']
        super(CmpH5ToolsRunner, self).__init__('\n'.join(desc))
        subparsers = self.getSubParsers()
        
        # select
        desc = ['Create a new cmp.h5 file by selecting alignments.',
                'Users can specify indices using the idx argument to select',
                'particular alignments.',
                'Alternatively, users can specify a where expression which chooses',
                'the alignments which the predicate is true.',
                'If a groupBy expression is specified then mulitple cmp.h5 files are',
                'generated according to the expression. For instance, if a user wanted'
                'to generate a cmp.h5 file for each reference sequence then --groupBy=Reference']
        parser = subparsers.add_parser('select', help = 'select', 
                                       description = '\n'.join(desc),
                                       parents = [self.parser])
        parser.add_argument('inCmp', metavar='input.cmp.h5')
        parser.add_argument('--outFile',
                            default = "out.cmp.h5",
                            dest='outCmp', metavar='out.cmp.h5',
                            help = "Either a pattern string or a filename")
        parser.add_argument('--idxs', metavar='N', type=int, nargs='+',
                            help='indices to select')
        parser.add_argument('--groupBy', metavar='groupBy-expression',
                            type = str, help='groupBy expression, e.g., Movie*Barcode')
        parser.add_argument('--where', metavar='where-expression',
                            type = str, help='where expression, e.g., ReadLength > 500')
        parser.add_argument('--outDir', metavar='outputDir',
                            type = str, default = ".")

        # merge
        desc = ['Merge two or more cmp.h5 files.']
        parser = subparsers.add_parser('merge', 
                                       help = 'merge',
                                       description='\n'.join(desc),
                                       parents=[self.parser])
        parser.add_argument('--outFile', 
                            dest='outCmp', default='out.cmp.h5', 
                            help='output filename [%(default)s]')
        parser.add_argument('inCmps', metavar='input.cmp.h5', nargs='+',
                            help='input filenames')

        # sort
        desc = ['Sort cmp.h5 files. If output-file is unspecified the input-file is',
                'overwritten']
        parser= subparsers.add_parser('sort',
                                         help='sort cmp.h5 file',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser.add_argument('inCmp', metavar='input.cmp.h5',
                              help='input filename')
        parser.add_argument('--outFile', dest='outCmp', 
                               help='output filename')
        parser.add_argument('--deep', dest='deepsort', action='store_true',
                              help='whether a deep sorting should be conducted, i.e. sort the' + 
                              'AlignmentArrays [%(default)s]')
        parser.add_argument('--tmpDir', dest='tmpdir', default='/tmp',  
                              help='temporary directory to use when sorting in-place [%(default)s]')
        parser.add_argument('--usePythonIndexer', dest='usePythonIndexer', default = False, 
                              action = 'store_true',  
                              help='Whether to use native indexing [%(default)s].')
        parser.add_argument('--inPlace', dest='inPlace', default = False, action = 'store_true',
                              help = 'Whether to make a temporary copy of the original cmp.h5' + 
                              ' file before sorting.')
        # equal
        desc = ['Compare two cmp.h5 files for equivalence.']
        parser = subparsers.add_parser('equal',
                                         help='compare two cmp.h5 files for equivalence',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser.add_argument('inCmp1', metavar='cmp.h5.1', help='filename 1')
        parser.add_argument('inCmp2', metavar='cmp.h5.2', help='filename 2')

        # summarize
        desc = ['Summarize cmp.h5 files.']
        parser = subparsers.add_parser('summarize',
                                         help='summarize contents of cmp.h5 files',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser.add_argument('inCmps', metavar='inCmps', nargs='+',
                            help='cmp.h5 files to summarize')
     
        # stats
        desc = ['Emit statistics from a cmp.h5 file.']
        parser = subparsers.add_parser('stats',
                                       help='print a csv for a cmp.h5 file',
                                       description='\n'.join(desc),
                                       parents=[self.parser])
        parser.add_argument('--outFile', dest='outCsv', 
                            help='output csv filename', default = None)
        parser.add_argument('--what', metavar = 'what-expression',
                            default = None)
        parser.add_argument('--where', metavar = 'where-expression',
                            default = None)
        parser.add_argument('--groupBy', metavar='groupBy-expression', 
                            default = None)
        parser.add_argument('inCmp', metavar='input.cmp.h5',
                                  help='input filename')
        
    def getVersion(self):
        return __version__
    
    def run(self):
        cmd = self.args.subName
        try: 
            if cmd == 'merge':
                cmpH5Merge(self.args.inCmps, self.args.outCmp)
            elif cmd == 'sort':
                cmpH5Sort(self.args.inCmp, self.args.outCmp, self.args.tmpdir, 
                          deep = self.args.deepsort, 
                          useNative = not self.args.usePythonIndexer,
                          inPlace = self.args.inPlace)
            elif cmd == 'select':
                cmpH5Select(self.args.inCmp, self.args.outCmp, 
                            idxs = self.args.idxs, whereStr = self.args.where, 
                            groupByStr = self.args.groupBy,
                            outDir = self.args.outDir)
            elif cmd == 'stats':
                cmpH5Stats(self.args.inCmp, self.args.what, self.args.where, 
                           self.args.groupBy, self.args.outCsv)
            elif cmd == 'equal':
                res = cmpH5Equal(self.args.inCmp1, self.args.inCmp2)
            elif cmd == 'summarize':
                # XXX : what should this guy do?
                for inCmp in self.args.inCmps:
                    print "".join(["-"] * 40)
                    print cmpH5Summarize(inCmp)
            else:
                raise PBH5ToolsException("NA", "Unkown command passed to cmph5tools.py:" + 
                                         self.args.subName)
        except PBH5ToolsException as pbe:
            logging.exception(pbe) 
            sys.exit(1) 

if __name__ == '__main__':    
    sys.exit(CmpH5ToolsRunner().start())
