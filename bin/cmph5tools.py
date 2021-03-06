#!/usr/bin/env python
#################################################################################
# Copyright (c) 2011-2013, Pacific Biosciences of California, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of Pacific Biosciences nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE.  THIS SOFTWARE IS PROVIDED BY PACIFIC BIOSCIENCES AND ITS
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL PACIFIC BIOSCIENCES OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#################################################################################

import os
import sys
import argparse
import logging
import tempfile
import shutil
import pkg_resources

from pbcore.util.ToolRunner import PBMultiToolRunner
from pbh5tools.PBH5ToolsException import PBH5ToolsException

from pbh5tools.CmpH5Select import cmpH5Select
from pbh5tools.CmpH5Merge import cmpH5Merge
from pbh5tools.CmpH5Sort import cmpH5Sort
from pbh5tools.CmpH5Stats import cmpH5Stats
from pbh5tools.CmpH5Compare import cmpH5Equal, cmpH5Summarize, cmpH5Validate
from pbh5tools.Metrics import DocumentedMetric,DocumentedStatistic
from pbh5tools._version import __version__

class CmpH5ToolsRunner(PBMultiToolRunner):
    def __init__(self):
        desc = ['Toolkit for command-line tools associated with cmp.h5 file processing.',
                'Notes: For all command-line arguments, default values are listed in [].']
        super(CmpH5ToolsRunner, self).__init__('\n'.join(desc))
        subparsers = self.subParsers

        # select
        desc = ['Create a new cmp.h5 file by selecting alignments.',
                'Users can specify indices using the idx argument to select',
                'particular alignments.',
                'Alternatively, users can specify a where expression which chooses',
                'the alignments which the predicate is true.',
                'If a groupBy expression is specified then mulitple cmp.h5 files are',
                'generated according to the expression. For instance, if a user wanted'
                'to generate a cmp.h5 file for each reference sequence then --groupBy=Reference']

        parser = subparsers.add_parser('select', help = 'Create new cmp.h5 files from selections of input.cmp.h5',
                                       description = '\n'.join(desc))


        parser.add_argument('inCmp', metavar='input.cmp.h5')
        parser.add_argument('--outFile',
                            default = "out.cmp.h5",
                            dest='outCmp', metavar='out.cmp.h5',
                            help = "Either a pattern string or a filename")
        parser.add_argument('--idxs', metavar='N', type=int, nargs='+',
                            help='indices to select')
        parser.add_argument('--groupBy', metavar='groupBy-expression',
                            type = str, help='groupBy expression, e.g., Movie*Barcode')
        parser.add_argument('--groupByCsv', metavar='groupByCsv',
                            type = str, help='groupByCsv file, e.g. Group,Movie,Barcode\\ngroupname,movie,barcode')
        parser.add_argument('--where', metavar='where-expression',
                            type = str, help='where expression, e.g., ReadLength > 500')
        parser.add_argument('--outDir', metavar='outputDir',
                            type = str, default = ".")

        # merge
        desc = ['Merge two or more cmp.h5 files. The input.cmp.h5 files must have',
                'been aligned to the same reference sequences']
        parser = subparsers.add_parser('merge',
                                       help = 'Merge input.cmp.h5 files into out.cmp.h5',
                                       description='\n'.join(desc))
        parser.add_argument('--outFile',
                            dest='outCmp', default='out.cmp.h5',
                            help='output filename [%(default)s]')
        parser.add_argument('inCmps', metavar='input.cmp.h5', nargs='+',
                            help='input filenames')

        # sort
        desc = ['Sort cmp.h5 files. If output-file is unspecified the input-file is',
                'overwritten']
        parser= subparsers.add_parser('sort',
                                         help='Sort input.cmp.h5 file',
                                         description='\n'.join(desc))
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
                                         help='Compare two cmp.h5 files for equivalence',
                                         description='\n'.join(desc))
        parser.add_argument('inCmp1', metavar='cmp.h5.1', help='filename 1')
        parser.add_argument('inCmp2', metavar='cmp.h5.2', help='filename 2')

        # summarize
        desc = ['Summarize cmp.h5 files.']
        parser = subparsers.add_parser('summarize',
                                         help='Summarize contents of cmp.h5 files',
                                         description='\n'.join(desc))
        parser.add_argument('inCmps', metavar='input.cmp.h5', nargs='+',
                            help='cmp.h5 files to summarize')

        # stats
        desc = ['Emit statistics from a cmp.h5 file.']
        parser = subparsers.add_parser('stats',
                                       help='Compute statistics from input.cmp.h5',
                                       description='\n'.join(desc))
        parser.add_argument('--outFile', dest='outCsv',
                            help='output csv filename', default = None)
        parser.add_argument('--what', metavar = 'what-expression',
                            default = None)
        parser.add_argument('--where', metavar = 'where-expression',
                            default = None)
        parser.add_argument('--groupBy', metavar='groupBy-expression',
                            default = None)
        parser.add_argument('--sortBy', metavar='sortBy-expression',
                            default = None)
        parser.add_argument('--limit', metavar='maximum-records', type=int,
                            default = None)
        parser.add_argument('inCmp', metavar='input.cmp.h5', help='input filename')

        # listMetrics
        desc = ["List available metrics and statistics for selection and stats."]
        parser = subparsers.add_parser('listMetrics',
                                       help = "List available metrics",
                                       description = '\n'.join(desc))
        parser.add_argument('--json', default = False, action = 'store_true',
                            help = 'Should output be in JSON format')

        # validate
        desc = ['Validate a cmp.h5 file']
        parser = subparsers.add_parser('validate',
                                       help = 'Validate input.cmp.h5',
                                       description = '\n'.join(desc))
        parser.add_argument('inCmp', metavar = 'input.cmp.h5',
                            help = 'input filename')


    def getVersion(self):
        return __version__

    def run(self):
        cmd = self.args.subCommand
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
                            groupByCsv = self.args.groupByCsv,
                            outDir = self.args.outDir)

            elif cmd == 'stats':
                cmpH5Stats(self.args.inCmp, 
                           whatStr = self.args.what, 
                           whereStr = self.args.where,
                           groupByStr = self.args.groupBy, 
                           sortByStr = self.args.sortBy,
                           limit     = self.args.limit,
                           outFile =  self.args.outCsv)

            elif cmd == 'listMetrics':
                print '--- Metrics:'
                print "\t\n".join(DocumentedMetric.list())
                print '\n--- Statistics:'
                print "\t\n".join(DocumentedStatistic.list())

            elif cmd == 'equal':
                ret = cmpH5Equal(self.args.inCmp1, self.args.inCmp2)
                if not ret[0]:
                    print >> sys.stderr, ret[1]
                    return 1
                else:
                    return 0

            elif cmd == 'summarize':
                for inCmp in self.args.inCmps:
                    print "".join(["-"] * 40)
                    print cmpH5Summarize(inCmp)

            elif cmd == 'validate':
                if cmpH5Validate(self.args.inCmp):
                    return 0
                else:
                    return 1
            else:
                raise PBH5ToolsException("", "Unkown command passed to cmph5tools.py:" +
                                         self.args.subName)
            return 0

        except PBH5ToolsException as pbe:
            logging.exception(pbe)
            return 1

if __name__ == '__main__':
    sys.exit(CmpH5ToolsRunner().start())

