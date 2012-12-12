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
import logging
import sys
from optparse import OptionParser
import numpy as n
import numpy.lib.recfunctions as rfn
import re

from pbcore.io.cmph5 import factory

class CmpH5Compare():
    def __init__(self, cmph5_1, cmph5_2):
        self.c1 = factory.create(cmph5_1,'r')
        self.c2 = factory.create(cmph5_2,'r')

    def run(self):
        if self.compare():
            print('Files contain equivalent content!')
        else:
            print('Files contain NON-equivalent content!')

    def compare(self):
        c1 = self.c1
        c2 = self.c2

        # COMPARE: Reference info and number of alignments
        logging.info('Comparing RefInfo and number of alignments')
        if sorted(c1['/RefInfo/FullName']._dataset) != sorted(c2['/RefInfo/FullName']._dataset):
            logging.error('DIFF: Ref seqs')
            return False
        elif c1.numAlnHits != c2.numAlnHits:
            logging.error('DIFF: number of alignments')
            return False

        aIdx1 = c1["/AlnInfo"].asRecArray()
        aIdx2 = c2["/AlnInfo"].asRecArray()

        # COMPARE: AlnIndex fields
        logging.info('Comparing AlnIndex content')
        if aIdx1.shape != aIdx2.shape:
            logging.error('DIFF: AIDX size')
            return False
        elif n.mean(aIdx1['tStart']) != n.mean(aIdx2['tStart']):
            logging.error('DIFF: AIDX content')
            return False
        elif len(n.unique(aIdx1['RefGroupID'])) != len(n.unique(aIdx2['RefGroupID'])):
            logging.error('DIFF: # and value of RefSeqIds')
            return False       

        # COMPARE: movie content
        logging.info('Comparing MovieInfo content')
        movieCompare = [str(x[0]) == str(x[1]) for x in zip(n.sort(c1['/MovieInfo/Name']._dataset),
                                                            n.sort(c2['/MovieInfo/Name']._dataset))]
        if False in movieCompare:
            return False
        elif c1['/AlnGroup/Path']._dataset.shape[0] != c2['/AlnGroup/Path']._dataset.shape[0]:
            return False

        # COMPARE: ReadGroup and AlnGroup content
        logging.info('Comparing ReadGroup and AlnGroup content')
        aIdxDict = {1:[aIdx1,c1], 2:[aIdx2,c2]}
        for t_id in aIdxDict:
            aIdx,cmpH5 = aIdxDict[t_id]
            alngrpMap = dict(zip(cmpH5['/AlnGroup/ID'],cmpH5['/AlnGroup/Path']))
            refgrpMap = dict(zip(cmpH5['/RefGroup/ID'],cmpH5['/RefGroup/Path']))
            for row in aIdx:
                if re.findall(refgrpMap[row['RefGroupID']],alngrpMap[row['AlnGroupID']]) == -1:            
                    logging.error('DIFF: Mixed up ReadGroupPath names and RefSeqNames')
                    return False

        # COMPARE: ALL alignments
        logging.info('Comparing ALL alignments and PulseMetrics')
        r1 = rfn.rename_fields(c1['/RefGroup'].asRecArray(), {'ID':'RefGroupID'})
        r2 = rfn.rename_fields(c1['/RefInfo'].asRecArray(),{'ID':'RefInfoID'})
        refMAP1 = rfn.join_by(key='RefInfoID', r1=r1, r2=r2).data

        r1 = rfn.rename_fields(c2['/RefGroup'].asRecArray(), {'ID':'RefGroupID'})
        r2 = rfn.rename_fields(c2['/RefInfo'].asRecArray(),{'ID':'RefInfoID'})
        refMAP2 = rfn.join_by(key='RefInfoID', r1=r1, r2=r2).data

        noMatchCntr = 0
        for ref in sorted(refMAP1['FullName']):
            refPath1 = refMAP1[refMAP1['FullName'] == ref]['Path'][0]
            refPath2 = refMAP2[refMAP2['FullName'] == ref]['Path'][0]
            alngrp1 = sorted([k for k in c1.h5File[refPath1].keys() if 'Consensus' not in k])
            alngrp2 = sorted([k for k in c2.h5File[refPath2].keys() if 'Consensus' not in k])

            sl1 = aIdx1[aIdx1['RefGroupID'] == refMAP1[refMAP1['FullName'] == ref]['RefGroupID'][0]]
            sl2 = aIdx2[aIdx2['RefGroupID'] == refMAP2[refMAP2['FullName'] == ref]['RefGroupID'][0]]
            
            for i,alngrp in enumerate(alngrp1):
                if alngrp == alngrp2[i]:

                    if sorted(c1.h5File[refPath1][alngrp1[i]].keys()) != sorted(c2.h5File[refPath2][alngrp2[i]].keys()):
                        logging.error('DIFF: Not the same Pulse Metrics')                            
                        return False

                    aa1 = c1.h5File[refPath1][alngrp1[i]]['AlnArray'][:]
                    aa2 = c2.h5File[refPath2][alngrp2[i]]['AlnArray'][:]

                    alngrpid1 = (c1['/AlnGroup'].asRecArray()[c1['/AlnGroup'].asRecArray()['Path'] == 
                                                              refPath1+'/'+alngrp1[i]]['ID'][0])
                    alngrpid2 = (c2['/AlnGroup'].asRecArray()[c2['/AlnGroup'].asRecArray()['Path'] == 
                                                             refPath2+'/'+alngrp2[i]]['ID'][0])
                    t_sl1 = n.sort(sl1[sl1['AlnGroupID'] == alngrpid1], order=['HoleNumber','rStart'])
                    t_sl2 = n.sort(sl2[sl2['AlnGroupID'] == alngrpid2], order=['HoleNumber','rStart'])
                    
                    for i,row in enumerate(t_sl1):
                        if row['tStart'] == t_sl2[i]['tStart'] and row['tEnd'] == t_sl2[i]['tEnd']:
                            cmpraa = len(n.nonzero(aa1[row['Offset_begin']:row['Offset_end']] - 
                                                   aa2[t_sl2[i]['Offset_begin']:t_sl2[i]['Offset_end']])[0])
                            if cmpraa:
                                logging.error('DIFF: aligned query and aligned target equality')                            
                                return False
                        else:
                            noMatchCntr += 1

        logging.info('INF: %s%% reads from %s do not match with %s' % (noMatchCntr/float(c1.numAlnHits), 
                                                                       c1.h5File.filename, c2.h5File.filename))
        return True
    
    def getRecArray(self, cmph5, dsetName, skiplist=[]):
        isize = (cmph5[dsetName].attrs['nRow'] if 
                 'nRow' in cmph5[dsetName].attrs else cmph5[dsetName][cmph5[dsetName].keys[0]].shape[0])
        clMAP = {n.object_:n.dtype('S100',1), n.uint32:n.uint32}
        columns = [(k,clMAP[cmph5[dsetName][k].dtype.type]) for k in cmph5[dsetName] if k not in skiplist]
        results = n.recarray((isize,),dtype=columns)
        for k in cmph5[dsetName]:
            if k not in skiplist:
                results[k] = cmph5[dsetName][k].value
        return results
