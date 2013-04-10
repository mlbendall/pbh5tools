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
import numpy as NP
import sys

from mlab import rec2csv, rec2txt
from pbtools.pbh5tools.Metrics import *

def prettyPrint(res):
    print rec2txt(res, padding = 10, precision = 2)

def cmpH5Stats(cmpH5Filename, whatStr = None, whereStr = None, 
               groupByStr = None, outFile = None):
    reader  = CmpH5Reader(cmpH5Filename)
    where   = DefaultWhere() if whereStr is None else eval(whereStr)
    groupBy = DefaultGroupBy() if groupByStr is None else eval(groupByStr)
    what    = DefaultWhat if whatStr is None else eval(whatStr)
        
    if not isinstance(what, Tbl):
        if hasEval(what):
            tbl = Tbl()
            tbl.cols[whatStr] = what
        elif isinstance(what, tuple):
            tbl = Tbl()
            for i,e in enumerate(what):
                tbl.cols[i] = e
        else:
            raise PBH5ToolsException("Invalid what specified: must be" + 
                                     " a table or expression.")
    else:
        tbl = what 

    # from IPython import embed; embed()
    res = query(reader, tbl, where, groupBy)
    res = toRecArray(res)
    
    if not outFile:
        prettyPrint(res)
    else:
        rec2csv(res, outFile)

        


