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


import logging
import os
import numpy as NP
import h5py as H5

from pbcore.io import CmpH5Reader
from pbh5tools.PBH5ToolsException import PBH5ToolsException
from pbh5tools.Metrics import *
from mlab import rec2csv, rec2txt

def cmpH5Equal(inCmp1, inCmp2):
    """Compare two cmp.h5 files for equality. Here equality means the
    alignments are the same and they are in the same
    order. Additionally, the reference information in the files has to
    be the same."""
    cmp1 = CmpH5Reader(inCmp1)
    cmp2 = CmpH5Reader(inCmp2)

    if not len(cmp1) == len(cmp2):
        return (False, "cmp.h5 files differ in length (%d, %d)" %
                (len(cmp1), len(cmp2)))

    aeq = [ a1 == a2 for a1,a2 in zip(cmp1, cmp2) ]
    if not all(aeq):
        return (False, "%d alignments differ" %  (len(aeq)-sum(aeq)))

    return (True, )

def cmpH5Summarize(inCmp, movieSummary = True, refSummary = True):
    """Summarize a cmp.h5 file"""
    reader = CmpH5Reader(inCmp)
    tstr   = "filename: %s\nversion:  %s\nn reads:  %d\nn refs:   " + \
        "%d\nn movies: %d\nn bases:  %d\navg rl:   %d\navg acc:  %g"
    
    rl  = [ r.readLength for r in reader ]
    acc = [ r.accuracy for r in reader ]
    
    summaryStr = (tstr % (os.path.basename(reader.file.filename), reader.version, len(reader),
                          len(reader.referenceInfoTable), len(reader.movieInfoTable), NP.sum(rl),
                          NP.round(NP.mean(rl)), NP.round(NP.mean(acc), 4)))
    eTbl = Tbl(nBases = Sum(ReadLength), avgReadLength = Mean(ReadLength), 
               avgAccuracy = Mean(Accuracy))
    
    movieSummaryTxt = rec2txt(toRecArray(query(reader, what = eTbl, groupBy = Movie)),
                              padding = 5, precision = 1)
    
    refSummaryTxt = rec2txt(toRecArray(query(reader, what = eTbl, groupBy = Reference)),
                            padding = 5, precision = 1)
   
    return (summaryStr + 
            ("\n\n\t Movie Summary:\n" + (movieSummaryTxt if movieSummary else "\n")) + 
            ("\n\n\t Reference Summary:\n" + (refSummaryTxt if refSummary else "\n")))
    

def cmpH5Validate(inCmp):
    """Validate a cmp.h5 file"""
    try:
        reader = CmpH5Reader(inCmp)
        return True
    except:
        return False



