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


#!/usr/bin/python
import subprocess
import os
import sys
from h5py import File
import logging
import numpy as n
import tempfile
            
class CmpH5Sampler():

    def __init__(self, cmph5FN, nOut, nSR, outDir='./'):
        self.cmpH5Seed = os.path.abspath(cmph5FN)
        self.outDir = outDir
        self.nOut = nOut
        self.nSR = nSR

    def run(self):            
        for i in range(self.nOut):
            logging.info('Generating %d out of %d output cmp.h5 files' % (i+1,self.nOut))
            coutFN = tempfile.NamedTemporaryFile(suffix='_%d.cmp.h5' % (i+1), dir=self.outDir, delete=False)
            subprocess.call('cp %s %s' % (self.cmpH5Seed, coutFN.name), shell=True)
            cmph5_out = File(coutFN.name, 'r+')
            aIdx = cmph5_out['/AlnInfo/AlnIndex'].value
            del cmph5_out['/AlnInfo/AlnIndex']
            cmph5_out['/AlnInfo/AlnIndex'] = aIdx[n.random.permutation(range(aIdx.shape[0]))[:self.nSR]]
            n.random.permutation(range(aIdx.shape[0]))[:self.nSR]
            cmph5_out.close()
            logging.info('Sorting [%s]...' % coutFN.name)
            subprocess.call('cmph5tools.py sort %s' % coutFN.name, shell=True)

class CmpH5Splitter():

    def __init__(self, filename, outDir='', fullRefName=False):
        self._fullRefName = fullRefName
        self._seedFN = os.path.abspath(filename)
        self._outDir = os.getcwd() if not outDir else outDir
        self.cmph5_in = File(self._seedFN, 'r')
        self.refgrpDict = dict(zip(self.cmph5_in['/RefGroup/Path'],
                                   zip(self.cmph5_in['/RefGroup/ID'],
                                       self.cmph5_in['/RefGroup/RefInfoID'])))
        self.refinfoDict = dict(zip(self.cmph5_in['/RefInfo/ID'], self.cmph5_in['/RefInfo/FullName']))
        self.aIdx = self.cmph5_in['/AlnInfo/AlnIndex'].value
        
        self._IDX = {'AlnGroupID': 1, 'MovieID': 2, 'RefGroupID': 3}
        
    def run(self):
        logging.info('Splitting [%s] into %d files...' % (os.path.basename(self._seedFN),len(self.refgrpDict)))
        outFNs = []
        for refgrp in self.refgrpDict:
            if self._fullRefName:
                outFN = self._outDir+'/%s.cmp.h5' % self.refinfoDict[self.refgrpDict[refgrp][1]]
            else:
                outFN = self._outDir+'/%s.cmp.h5' % refgrp[1:]
            outFNs.append(outFN)

            logging.info('Generating [%s]...' % os.path.basename(outFN))
            cmph5_out = File(outFN, 'w')

            # Copy over all essential HDF5 Groups
            for dset in ['/AlnGroup','/AlnInfo','/MovieInfo','/RefGroup','/RefInfo', '/FileLog']:
                cmph5_out.copy(self.cmph5_in[dset], dset)

            # Copy over root attributes
            map(lambda x: cmph5_out.attrs.create(x[0],x[1]), self.cmph5_in.attrs.items())

            # Trim RefGroup and RefInfo
            self._trimGroup(cmph5_out['/RefGroup'], cmph5_out['/RefGroup/Path'].value == refgrp)
            self._trimGroup(cmph5_out['/RefInfo'], cmph5_out['/RefInfo/ID'].value == self.refgrpDict[refgrp][1])

            # Trim MovieInfo and AlnGroup
            self._trimComplexGroup(cmph5_out['/MovieInfo'], 'MovieID', self.refgrpDict[refgrp][0])
            self._trimComplexGroup(cmph5_out['/AlnGroup'], 'AlnGroupID', self.refgrpDict[refgrp][0])

            # Trim AlnInfo
            self._trimGroup(cmph5_out['/AlnInfo'], self.aIdx[:,self._IDX['RefGroupID']] == self.refgrpDict[refgrp][0])

            # Copy RefGroup
            cmph5_out.copy(self.cmph5_in[refgrp], refgrp)

            # delete the dataset which indicates that the file is
            # sorted. Indeed, the file will be mostly sorted, but the
            # offsets don't appear to be recalculated.
            if 'OffsetTable' in cmph5_out['/RefGroup'].keys():
                logging.info("Removing OffsetTable.")
                del cmph5_out["RefGroup/OffsetTable"]
                
            # close the file. 
            cmph5_out.close()

        return outFNs

    def _trimComplexGroup(self, rgrp, idxName, refgrpID):
        rgrpName = rgrp.name
        ids = n.unique(self.aIdx[self.aIdx[:,self._IDX['RefGroupID']] == refgrpID, self._IDX[idxName]])
        idx = [self.cmph5_in[rgrpName]['ID'].value == t_id for t_id in self.cmph5_in[rgrpName]['ID'] if t_id in ids]
        idx = reduce(lambda x,y: x|y,idx)
        self._trimGroup(rgrp, idx)
    
    def _trimGroup(self, rgrp, idx):
        map(lambda x: self._trimDataSet(rgrp[x],idx), rgrp.keys())
        if 'nRow' in rgrp.attrs.keys():
            rgrp.attrs.modify('nRow', rgrp[rgrp.attrs['MasterDataset']].shape[0])
            
    def _trimDataSet(self, dout, idx):
        if len(dout.shape) == 1:
            newval = dout[idx]
        else:
            if idx.shape[0] == 1: idx = n.nonzero(idx)
            newval = dout[idx,:]
        dout.resize(newval.shape)
        dout.write_direct(newval)
        if 'lastRow' in dout.attrs.keys():
            dout.attrs.modify('lastRow', dout.shape[0])
