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
from pbtools.pbh5tools.CmpH5Compare import cmpH5Compare

__p4revision__ = "$Revision$"
__p4change__ = "$Change$"
revNum = int(__p4revision__.strip("$").split(" ")[1].strip("#"))
changeNum = int(__p4change__.strip("$").split(":")[-1])
__version__ = "%s-r%d-c%d" % ( pkg_resources.require("pbtools.pbh5tools")[0].version, revNum, changeNum )


class CmpH5ToolsRunner(PBMultiToolRunner):
    def __init__(self):
        desc = ['Toolkit for all command-line tools associated with cmp.h5 file processing.',
                'Notes: For all command-line arguments, default values are listed in [].']
        super(CmpH5ToolsRunner, self).__init__('\n'.join(desc))
        subparsers = self.getSubParsers()
      
        # select
        desc = ['Create a new cmp.h5 file by selecting alignments.']
        parser_m = subparsers.add_parser('select', help = 'select', 
                                         description = '\n'.join(desc),
                                         parents = [self.parser])
        parser_m.add_argument('inCmp', metavar='input.cmp.h5')
        parser_m.add_argument('outCmp', metavar='output.cmp.h5')
        parser_m.add_argument('idxs', metavar='N', type=int, nargs='+',
                              help='indices to select')
     
        # merge
        desc = ['Merge two or more cmp.h5 files.']
        parser_m = subparsers.add_parser('merge', 
                                         help = 'merge',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_m.add_argument('--outFile', 
                              dest='outCmp', default='out.cmp.h5', 
                              help='output filename [%(default)s]')
        parser_m.add_argument('inCmps', metavar='input.cmp.h5', nargs='+',
                              help='input filenames')

        # sort
        desc = ['Sort cmp.h5 files. If output-file is unspecified the input-file is',
                'overwritten']
        parser_s = subparsers.add_parser('sort',
                                         help='sort cmp.h5 file',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_s.add_argument('inCmp', metavar='input.cmp.h5',
                              help='input filename')
        parser_s.add_argument('--outFile', dest='outCmp', 
                               help='output filename')
        parser_s.add_argument('--deep', dest='deepsort', action='store_true',
                              help='whether a deep sorting should be conducted, i.e. sort the' + 
                              'AlignmentArrays [%(default)s]')
        parser_s.add_argument('--tmpDir', dest='tmpdir', default='/tmp',  
                              help='temporary directory to use when sorting in-place [%(default)s]')
        parser_s.add_argument('--usePythonIndexer', dest='usePythonIndexer', default = False, 
                              action = 'store_true',  
                              help='Whether to use native indexing [%(default)s].')
        parser_s.add_argument('--inPlace', dest='inPlace', default = False, action = 'store_true',
                              help = 'Whether to make a temporary copy of the original cmp.h5 file before sorting.')

        # compare
        desc = ['Compare two cmp.h5 files for equivalence.']
        parser_c = subparsers.add_parser('compare',
                                         help='compare two cmp.h5 files for equivalence',
                                         description='\n'.join(desc),
                                         parents=[self.parser])
        parser_c.add_argument('inCmps', metavar='input.cmp.h5', 
                              nargs=2, help='input filenames')

        # stats
        desc = ['Emit statistics from a cmp.h5 file.']
        parser_stats = subparsers.add_parser('stats',
                                             help='print a csv for a cmp.h5 file',
                                             description='\n'.join(desc),
                                             parents=[self.parser])
        parser_stats.add_argument('--groupBy', metavar='groupBy', 
                                  help = 'how to group the results, .e.g., movie, reference,' + 
                                  'subread, molecule', 
                                  default = None)
        parser_stats.add_argument('inCmp', metavar='input.cmp.h5',
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
                          deep = self.args.deepsort, useNative = not self.args.usePythonIndexer,
                          inPlace = self.args.inPlace)
            elif cmd == 'select':
                cmpH5Select(self.args.inCmp, self.args.outCmp, self.args.idxs)
            elif cmd == 'stats':
                cmpH5Stats(self.args.inCmp, self.args.groupBy).run()
            elif cmd == 'compare':
                cmpH5Compare(self.args.inCmps[0], self.args.inCmps[1])
            else:
                raise PBH5ToolsException("NA", "Unkown command passed to cmph5tools.py:" + 
                                         self.args.subName)
        except PBH5ToolsException as pbe:
            logging.exception(pbe) 
            sys.exit(1) 

if __name__ == '__main__':    
    sys.exit(CmpH5ToolsRunner().start())
