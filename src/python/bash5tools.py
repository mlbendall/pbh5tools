#!/usr/bin/env python

import os, os.path, sys, argparse, logging

from pbcore.util.ToolRunner import PBToolRunner
from pbcore.io import (BasH5Reader,
                       FastaWriter,
                       FastqWriter)

__version__ = "0.5.0"

def _fileType(arg):
    """
    Canonicalize the given filetype argument
    """
    if   arg in ["fa", "fasta", "FASTA"]: return "fasta"
    elif arg in ["fq", "fastq", "FASTQ"]: return "fastq"
    elif arg in ["csv"]:                  return "csv"
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
            "--readType", dest="readType", default="subreads",
            choices=["ccs", "subreads", "unrolled"],
            help="read type (ccs, subreads, or unrolled) [%(default)s]")
        self.parser.add_argument(
            "--outType", dest="outType", default="fasta", type=_fileType,
            help="output file type (fasta, fastq, or csv) [%(default)s]")

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
            self.parser.error("File %s does not exist!" % self.args.infile)
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
        movieName = inBasH5.movieName
        outFilePrefix = self.args.outFilePrefix or movieName
        outFilename = "%s.%s" % (outFilePrefix, self.args.outType)

        if self.args.outType == "fasta":
            sink = FastaEmitter(outFilename)
        elif self.args.outType == "fastq":
            sink = FastqEmitter(outFilename)
        else:
            print "CSV output support not yet implemented!"
            sys.exit(-1)

        readType = self.args.readType
        for zmwRead in self.zmwReads(inBasH5, self.args.readType):
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
