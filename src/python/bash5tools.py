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
import pkg_resources

from pbtools.pbh5tools.BasH5ToData import BASH5Data
from pbcore.util.ToolRunner import PBToolRunner

__version__ = "0.4.0"


class BasH5ToolsRunner(PBToolRunner):
    
    def __init__(self):
        desc = ['Tool for extracting data from .bas.h5',
                'Notes: For all command-line arguments, default values are listed in [].']
        super(BasH5ToolsRunner, self).__init__('\n'.join(desc))

        self.parser.add_argument('infile', metavar='input.bas.h5',
                               help='input .bas.h5 filename')
        self.parser.add_argument('--outFilePref', dest='outfilepref', default='', 
                               help='output filename prefix [%(default)s]')
        self.parser.add_argument('--readType', dest='readtype', default='Raw', 
                               help='read type (CCS or Raw) [%(default)s]')
        self.parser.add_argument('--outType', dest='outtype', default='fasta', 
                               help='output file type (fasta, fastq, csv or detail) [%(default)s]')
        self.parser.add_argument('--subReads', dest='subreads', action='store_true', 
                               help='for fasta/fastq files, generate the subreads and not the raw reads [%(default)s]')

        groupFilt = self.parser.add_argument_group('read filtering arguments')
        groupFilt.add_argument('--minLength', type=int, dest='minlen', default=0,
                               help='min read length [%(default)s]')
        groupFilt.add_argument('--minReadscore', type=float, dest='minrs', default=0,
                               help='min read score, valid only when used with --readType=Raw [%(default)s]')
        groupFilt.add_argument('--minMeanQV', type=int, dest='minmqv', default=0,
                               help='min per read mean Quality Value [%(default)s]')
        groupFilt.add_argument('--minNumberOfPasses', type=int, dest='minnp', default=0,
                               help='min number of CCS passes, valid only when used with --readType=CCS [%(default)s]')
    def getVersion(self):
        return __version__

    def validateArgs(self):
        if not os.path.isfile(self.args.infile):
            self.parser.error('File %s does not exist!' % self.args.infile)
        if self.args.readtype not in ['CCS', 'Raw']:
            self.parser.error('%s is not a valud read type, only CCS and Raw read types are supported!' % self.args.readtype)            
        if self.args.outtype not in ['fasta', 'fastq', 'csv', 'detail']:
            self.parser.error('%s is not a valid file type, only fasta, fastq, csv and detail files are supported!' %
                                 self.args.outtype)                    
        if self.args.minrs > 1.0 or self.args.minrs < 0.0:
            self.parser.error('Minimum readscore needs to be > 0.0 and < 1.0')

    def run(self):
        filters = {'ReadScore': self.args.minrs,
                   'ReadLength': self.args.minlen,
                   'CCSCov': self.args.minnp,
                   'MinQV': self.args.minmqv}
        map(lambda x: filters.pop(x) if not filters[x] else None, filters.keys())

        logging.info('Loading .bas.h5 file from %s' % self.args.infile)                
        bash5 = BASH5Data(self.args.infile, readType=self.args.readtype, filters=filters)

        logging.info('Generating %s file' % self.args.outtype)                
        if self.args.outtype in ['fasta','fastq']:
            bash5.toFastx(outFNPref=self.args.outfilepref, fileType=self.args.outtype, subreadsplit=self.args.subreads)
        elif self.args.outtype == 'csv':
            bash5.toCSV(outFNPref=self.args.outfilepref)
        elif self.args.outtype == 'detail':
            bash5.toDetail(outFNPref=self.args.outfilepref)

if __name__ == '__main__':    
    sys.exit(BasH5ToolsRunner().start())

