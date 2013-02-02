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
import os
import sys
import shutil
import datetime
import logging
import tempfile

import h5py as H5
import numpy as NP

from pbtools.pbh5tools.PBH5ToolsException import PBH5ToolsException
from pbtools.pbh5tools.CmpH5Format import CmpH5Format

## XXX : should this even be a class? sortCmpH5 ain't
class CmpH5Select(object):
    """Take an input cmp.h5 file and a vector of indices into the
    AlnIndex and create a new cmp.h5 file from those alignments."""
    def __init__(self, inCmpFilename, outCmpFilename, idxs):
        inCmp  = H5.File(inCmpFilename, 'r')
        outCmp = H5.File(outCmpFilename, 'w') # fail if it exists. 
        idxs   = NP.array(idxs)

        logging.debug("processing input: %s to output: %s using idxs: %s" %
                      (inCmpFilename, outCmpFilename, idxs))
        try:
            self.select(inCmp, outCmp, idxs) 

        except Exception, E:
            logging.error("Caught Exception: %s", str(E))
            os.remove(outCmpFilename) # remove the busted file
            raise PBH5ToolsException(E)
    
    def copyAttributes(self, inDs, outDs):
        for k in inDs.attrs.keys():
            if inDs.attrs[k].dtype == 'object':
                newDtype = H5.special_dtype(vlen = str)
            else:
                newDtype = inDs.attrs[k].dtype
            outDs.attrs.create(k, inDs.attrs[k], dtype = newDtype)

    def copyDataset(self, absDsName, inCmp, outCmp, selection, fmt):
        dta = inCmp[absDsName]
        if len(dta.shape) <= 1:
            ndta = dta.value[selection]
        else:
            ndta = dta.value[selection,:]
        ## XXX : chunking
        outDs = outCmp.create_dataset(absDsName, data = ndta, dtype = dta.dtype)
        self.copyAttributes(dta, outDs)
      

    def trimDataset(self, groupName, alnIdxID, inCmp, outCmp, fmt, idName = 'ID'):
        ids = outCmp[fmt.ALN_INDEX][:,alnIdxID]
        nds = '/'.join([groupName, idName])
        msk = NP.array([x in ids for x in inCmp[nds].value]) # got to be an NP.array
        for dsName in inCmp[groupName].keys():
            self.copyDataset('/'.join([groupName, dsName]), inCmp, outCmp, 
                             msk, fmt)
    
    def copyGroup(self, groupName, inCmp, outCmp):
        if groupName in inCmp:
            outCmp.copy(inCmp[groupName], groupName)

    def select(self, inCmp, outCmp, idxs):
        fmt = CmpH5Format(inCmp)
        
        if not (NP.max(idxs) < inCmp[fmt.ALN_INDEX].shape[0] and
                NP.min(idxs) >= 0):
            raise PBH5ToolsException("Invalid idxs specified, must be within [0, %d)" % 
                                     inCmp[fmt.ALN_INDEX].shape[0])

        # copy over the AlnIndex and other AlnInfo elements
        # correpsonding to idxs to new file. 
        for dsName in inCmp[fmt.ALN_INFO].keys():
            self.copyDataset('/'.join([fmt.ALN_INFO, dsName]), inCmp, outCmp, idxs, fmt)
                    
        # reset the ALN_ID
        outCmp[fmt.ALN_INDEX][:,fmt.ID] = \
            NP.array(range(1, outCmp[fmt.ALN_INDEX].shape[0] + 1))
        
        # trim the other datasets
        self.trimDataset(fmt.ALN_GROUP, fmt.ALN_ID, inCmp, outCmp, fmt)
        self.trimDataset(fmt.REF_GROUP, fmt.REF_ID, inCmp, outCmp, fmt)
        self.trimDataset(fmt.MOVIE_INFO, fmt.MOVIE_ID, inCmp, outCmp, fmt)

        # other groups will go over whole hog
        self.copyGroup(fmt.FILE_LOG, inCmp, outCmp)
        self.copyGroup(fmt.REF_INFO, inCmp, outCmp)
        self.copyGroup(fmt.BARCODE_INFO, inCmp, outCmp)
        
        # now we copy over the actual data
        for i in xrange(0, outCmp[fmt.ALN_GROUP_ID].shape[0]):
            # figure out what reads are in this group.
            agID = outCmp[fmt.ALN_GROUP_ID][i]
            agPT = outCmp[fmt.ALN_GROUP_PATH][i]
            alnIdx = outCmp[fmt.ALN_INDEX].value
            whReads = NP.where(agID == alnIdx[:,fmt.ALN_ID])[0]
            offBegin = alnIdx[whReads, fmt.OFFSET_BEGIN]
            offEnd = alnIdx[whReads, fmt.OFFSET_END]
            totalSize = NP.sum((offEnd - offBegin) + 1) # 0 in between

            for dsName in inCmp[agPT].keys():
                fullPath = '/'.join([agPT, dsName])
                newDs = outCmp.create_dataset(fullPath, shape = (totalSize,), 
                                              dtype = inCmp[fullPath].dtype)
                origDs = inCmp[fullPath]
                cs = 0
                for j in xrange(0, len(whReads)):
                    newEnd = cs + offEnd[j] - offBegin[j]
                    newDs[cs:newEnd] = origDs[offBegin[j]:offEnd[j]]
                    outCmp[fmt.ALN_INDEX][whReads[j],fmt.OFFSET_BEGIN] = cs
                    outCmp[fmt.ALN_INDEX][whReads[j],fmt.OFFSET_END] = newEnd
                    cs = newEnd
     
        # copy over the top-level attributes
        self.copyAttributes(inCmp, outCmp)
        
        # remove the offset table
        del outCmp[fmt.REF_OFFSET_TABLE]
        
