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

import numpy as NP
import sys

from mlab import rec2csv, rec2txt
from pbh5tools.Metrics import *

def prettyPrint(res):
    print rec2txt(res, padding = 20, precision = 2)

def makeTblFromInput(exprStr, defaultValue):
    if not exprStr:
        return defaultValue
    else:
        tbl = eval(exprStr)
        if not isinstance(tbl, Tbl):
          if hasEval(tbl): 
              ## just a naked expression, wrap it. 
              ntbl = Tbl()
              ntbl.cols[exprStr] = tbl
              tbl = ntbl  
          elif isinstance(tbl, tuple):
              ## table the tuple. 
              ntbl = Tbl()
              for i,e in enumerate(tbl):
                  ntbl.cols[str(e)] = e
              tbl = ntbl
          else:
              raise PBH5ToolsException("stats", "Invalid expression specified: must be" +
                                       " a table, expression, or tuple.")
        return tbl
            
def cmpH5Stats(cmpH5Filename, whatStr = None, whereStr = None,
               groupByStr = None, sortByStr = None, limit = None, outFile = None):

    reader     = CmpH5Reader(cmpH5Filename)
    where      = DefaultWhere if whereStr is None else eval(whereStr)
    groupBy    = DefaultGroupBy if groupByStr is None else eval(groupByStr)
    groupByCsv = None
    what       = makeTblFromInput(whatStr, DefaultWhat)
    sortBy     = makeTblFromInput(sortByStr, DefaultSortBy)

    res = query(reader, what, where, groupBy, groupByCsv, sortBy, limit)
    res = toRecArray(res)
    if not outFile:
        prettyPrint(res)
    else:
        rec2csv(res, outFile)


