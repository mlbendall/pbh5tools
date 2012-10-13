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
import sys
import os
import h5py

from pbcore.io import cmph5

MAX_TABLE_ROWS = 10
COLUMN_PADDING = 2
MAX_COLUMN_WIDTH = 30
MAX_LINE_LENGTH = 150
MAX_ATTR_NAME_LENGTH = 30
MAX_ATTR_VALUE_LENGTH = 70

class CmpH5Summary():
    def __init__(self, cmph5FN):
        self.inFN = cmph5FN
    
    def pp(self, indent, msg):
        """Pretty print function."""
        if len(msg) > MAX_LINE_LENGTH:
            for i in range(0,len(msg),MAX_LINE_LENGTH):
                self.pp(indent, msg[i:i+MAX_LINE_LENGTH-3]+"...")
        else:
            print "    "*indent + msg

    def ppTable(self, indent, titles, data):
        """Pretty prints a table"""
        if len(data) == 0:
            return
        maxLengths = [max([max(len(str(row[i])), len(titles[i])) for row in data]) for i in range(len(titles))]
        colLengths = [min(MAX_COLUMN_WIDTH, ml) for ml in maxLengths]
        data = [titles] + list(data)
        for row in data[:MAX_TABLE_ROWS]:
            rowStr = ""
            for col in range(len(titles)):
                txt = str(row[col])[:colLengths[col]]
                if len(txt) < len(str(row[col])):
                    txt = txt[:-3]+"..."
                pad = COLUMN_PADDING + (colLengths[col] - len(txt))
                rowStr += txt + " " * pad        
            self.pp(indent, rowStr.strip())
        if len(data) > MAX_TABLE_ROWS:
            self.pp(indent, "...")
            
    def ppAttrs(self, indent, attrs):
        """Prints a series of attributes as k:v pairs"""
        if len(attrs) == 0:
            return
        attrNameLength = min(MAX_ATTR_NAME_LENGTH, max([len(k) for k in attrs.keys()]))
        for attr in attrs:
            key = attr[:attrNameLength]
            key = key + " " * (attrNameLength - len(key))
            value = str(attrs[attr])
            if len(value) > MAX_ATTR_VALUE_LENGTH:
                value = value[:MAX_ATTR_VALUE_LENGTH-3] + "..."
            self.pp(indent, "%s : %s" % (key, value))
        
    def run(self):
        cmpH5 = cmph5.factory.create(self.inFN, "r")
        self.pp(0, "== %s ==" % os.path.basename(self.inFN))
        self.pp(0, "/")
        attrs = dict(cmpH5.attrs)
        attrs["Total Reads"] = cmpH5.numReads
        attrs["Total Subreads"] = cmpH5.numSubreads
        self.ppAttrs(1, attrs)
        self.pp(0, "")
        
        for table in ["/MovieInfo", "/RefInfo", "/RefGroup", "/AlnGroup", "/FileLog"]:
            tlen = len(cmpH5[table])
            self.pp(0, "%s (%d entries):" % (table, tlen))
            self.ppAttrs(1, cmpH5[table].attrs)
            data = cmpH5[table].asRecArray()
            self.pp(1, "Data: ")
            self.ppTable(2, data.dtype.names, data)
            self.pp(0, "")

        for refGroup in cmpH5:
            self.pp(0, "%s (RefGroup):" % (refGroup.name))
            self.pp(0, "")
            self.ppAttrs(1, refGroup.attrs)
            for readGroup in refGroup:
                self.pp(1, "%s (AlnGroup):" % (readGroup.name))
                attrs  = dict(readGroup.attrs)
                attrs["Aligned Reads"] = len(readGroup)
                attrs["Aligned Bases"] = len(readGroup["AlnArray"])
                attrs["Pulse Metrics"] = ",".join(readGroup.pulseTables)
                self.ppAttrs(2, attrs)
                self.pp(0, "")
        return 0
