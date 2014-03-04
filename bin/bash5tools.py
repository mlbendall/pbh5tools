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
import os, os.path, sys, argparse, logging

from pbcore.util.ToolRunner import PBToolRunner
from pbcore.io import (BasH5Reader,
                       FastaWriter,
                       FastqWriter)

from pbh5tools._version import __version__

def _fileType(arg):
    """
    Canonicalize the given filetype argument
    """
    if   arg in ["fa", "fasta", "FASTA"]: return "fasta"
    elif arg in ["fq", "fastq", "FASTQ"]: return "fastq"
    else: raise ValueError("Unsupported output file format")


class FastaEmitter(object):
    def __init__(self, filename):
        self.writer = FastaWriter(filename)

    def emit(self, zmwRead):
        self.writer.writeRecord(zmwRead.readName,
                                zmwRead.basecalls())

class FastqEmitter(object):
    def __init__(self, filename):
        self.writer = FastqWriter(filename)

    def emit(self, zmwRead):
        self.writer.writeRecord(zmwRead.readName,
                                zmwRead.basecalls(),
                                zmwRead.QualityValue())

class BasH5ToolsRunner(PBToolRunner):

    def __init__(self):
        desc = "Tool for extracting data from .bas.h5 files"
        super(BasH5ToolsRunner, self).__init__(desc)

        self.parser.add_argument(
            "inFile", metavar="input.bas.h5",
            help="input .bas.h5 filename")
        self.parser.add_argument(
            "--outFilePrefix", dest="outFilePrefix", default=None,
            help="output filename prefix [%(default)s]")
        self.parser.add_argument(
            "--readType", dest="readType", default="",
            choices=["ccs", "subreads", "unrolled"],
            help="read type (ccs, subreads, or unrolled) [%(default)s]")
        self.parser.add_argument(
            "--outType", dest="outType", default="fasta", type=_fileType,
            help="output file type (fasta, fastq) [%(default)s]")

        groupFilt = self.parser.add_argument_group("Read filtering arguments")
        groupFilt.add_argument(
            "--minLength", type=int, dest="minLength", default=0,
            help="min read length [%(default)s]")
        groupFilt.add_argument(
            "--minReadScore", type=float, dest="minReadScore", default=0,
            help="min read score, valid only with --readType={unrolled,subreads}  [%(default)s]")
        groupFilt.add_argument(
            "--minPasses", type=int, dest="minPasses", default=0,
            help="min number of CCS passes, valid only with --readType=ccs [%(default)s]")

    def getVersion(self):
        return __version__

    def validateArgs(self):
        if not os.path.isfile(self.args.inFile):
            self.parser.error("File %s does not exist!" % self.args.inFile)
        if self.args.minReadScore > 1.0 or self.args.minReadScore < 0.0:
            self.parser.error("Minimum read score needs to be > 0.0 and < 1.0")

    def zmwReads(self, inBasH5, readType):
        """
        Extract all reads of the appropriate read type
        """
        for zmw in inBasH5:
            if readType == "ccs":
                r = zmw.ccsRead
                if r: yield r
            elif readType == "unrolled":
                yield zmw.read()
            else:
                for r in zmw.subreads:
                    yield r

    def run(self):
        inBasH5 = BasH5Reader(self.args.inFile)
        
        if not inBasH5.hasConsensusBasecalls and self.args.readType == "ccs":
            print "Input file %s contains no CCS reads." % self.args.inFile
            sys.exit(-1)
        
        if not inBasH5.hasRawBasecalls and self.args.readType in ["unrolled", "subreads"]:
            print "Input file %s contains no %s reads" % (self.args.inFile,
                                                          self.args.readType)
            sys.exit(-1)

        movieName = inBasH5.movieName
        outFilePrefix = self.args.outFilePrefix or movieName
        outFilename = "%s.%s" % (outFilePrefix, self.args.outType)

        if self.args.outType == "fasta":
            sink = FastaEmitter(outFilename)
        elif self.args.outType == "fastq":
            sink = FastqEmitter(outFilename)

        if self.args.readType == '':
            # choose based on file.
            if inBasH5.hasRawBasecalls:
                readType = 'subreads' 
            elif inBasH5.hasConsensusBasecalls:
                readType = 'ccs'
            else:
                print "Input bas.h5 file has neither CCS nor subread data"
                sys.exit(-1)
        else:
            readType = self.args.readType

        for zmwRead in self.zmwReads(inBasH5, readType):
            zmw = zmwRead.zmw
            #
            # Emit read if filters pass
            #
            if ((readType != "ccs" or zmw.numPasses >= self.args.minPasses)    and
                (readType == "ccs" or zmw.readScore >= self.args.minReadScore) and
                (len(zmwRead) >= self.args.minLength)):

                sink.emit(zmwRead)


if __name__ == "__main__":
    sys.exit(BasH5ToolsRunner().start())
