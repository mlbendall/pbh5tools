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
import numpy as np

from pbcore.io import CmpH5Reader

def getReadLength(cmpH5, idx):
    return cmpH5.rEnd[idx] - cmpH5.rStart[idx]

def getUnrolledReadLength(cmpH5, idx):
    pass

def getAccuracy(cmpH5, idx):
    return (1.0 - ((cmpH5.nMM[idx] + cmpH5.nIns[idx] + cmpH5.nDel[idx])/(0.0 + getReadLength(cmpH5, idx))))

def getNSubreads(cmpH5, idx):
    return len(idx)

def getNMolecules(cmpH5, idx):
    len(set(zip(cmpH5.MovieID[idx], cmpH5.HoleNumber[idx])))

def getPolymerizationRate(cmpH5, idx):
    pass
    
class CmpH5Stats(object):
    def __init__(self, cmpH5Filename, groupBy = None):
        self.groupBy = groupBy
        self.reader  = CmpH5Reader(cmpH5Filename)
        
    def summarizeDataForStrata(self, idx):
        metricsToCache = {'MappedSubreadReadLength' : getReadLength, 
                          'MappedReadLength'        : getUnrolledReadLength, 
                          'SumOfMappedBases'        : getSumOfMappedBases, 
                          'Accuracy'                : getAccuracy, 
                          'PolymerizationRate'      : getPolymerizationRate} 
        dtaCache = {key : metricsToCache[key](self.reader, idx) for key in metricsToCache.keys()}
        
        return ({ 
                "MeanMappedSubreadReadLength" : np.mean(dtaCache["MappedSubreadReadLength"]),
                "MedianMappedSubreadReadLength" : np.median(dtaCache["MappedSubreadReadLength"]),
                
                
                        })

    def run(self):
        ## groupBy becomes a list of index vectors.
        if self.groupBy == 'movie':
            movieNames  = [self.reader.movieInfo(id)[1] for id in self.reader.MovieID]
            uMovieNames = set(movieNames)
            idxs = dict([(elt, np.where([ elt == m for m in mn ])[0]) for elt in umn])
        else:
            idxs = {"" : np.arange(0, len(self.reader))}
          
        dta = { key : summarizeDataForStrata(idxs[key]) for key in idxs.keys() }
            
            

        
