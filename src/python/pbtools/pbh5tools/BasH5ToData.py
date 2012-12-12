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
import numpy as n

from pbcore.io.BasH5IO import BasH5

class BASH5Data(BasH5):
    
    # {'ReadScore': 0, 'ReadLength': 0, 'MeanQV':0, 'CCSCov': 0}
    def __init__(self, filename, readType='Raw', filters={}):
        super(BASH5Data, self).__init__(filename, readType)
        self.filters = self._cleanFilters(filters)
        self._filtDict = {'ReadScore': lambda hn,v: self.baseCallsDG.getReadScoreForZMW(hn) >= v,
                          'ReadLength': lambda hn,v: self.baseCallsDG.getBaseCallLenForZMW(hn) >= v,
                          'MeanQV': lambda hn,v: n.mean(self.baseCallsDG.getQVForZMW(hn,'QualityValue')) >= v,
                          'CCSCov': lambda hn,v: self.baseCallsDG.getNumberOfPassesForZMW(hn) >= v}

    def _cleanFilters(self, filters):
        if self.baseCallsDG.baseCallType == 'Raw' and filters.has_key('CCSCov'):
            filters.pop('CCSCov')
        if self.baseCallsDG.baseCallType == 'CCS' and filters.has_key('ReadScore'):
            filters.pop('ReadScore')
        return filters
        
    def getReads(self):
        for hn in self.getZMWs():
            if self.baseCallsDG.getBaseCallLenForZMW(hn):
                if self.filters:
                    if not (self.baseCallsDG.getStatusForZMW(hn) and 
                            n.all([self._filtDict[k](hn,v) for k,v in self.filters.items()])):                        
                        yield (hn, self.baseCallsDG.getBaseCallForZMW(hn))
                else:
                    yield (hn, self.baseCallsDG.getBaseCallForZMW(hn))

    def toFastx(self, outFNPref='', fileType='fasta', subreadsplit=False):
        movieName = os.path.basename(self._h5f.filename.split('.')[0])
        outFN = '%s.%s' % (movieName, fileType)
        if outFNPref:
            outFN = '%s.%s' % (outFNPref, fileType)
        outFN = os.path.abspath(outFN)

        fout = open(outFN, 'w')
        if fileType == 'fasta':
            for hn,read in self.getReads():
                if subreadsplit:
                    subreads = self.rgnTable.getInsertRegionForZMW(hn)
                    if self.baseCallsDG.baseCallType == 'CCS':
                        read = self.rbaseCallsDG.getBaseCallForZMW(hn)
                        subreads = self.baseCallsDG.getCCSSubreadsRegionsForZMW(hn)
                    for i,subread in enumerate(subreads):
                        if subread[1] <= subread[0]: continue 
                        fout.write('>%s/%d/%d_%d\n' % (movieName, hn, subread[0], subread[1]))                
                        fout.write('%s\n' % read[subread[0]:subread[1]])        
                else:
                    fout.write('>%s/%d\n' % (movieName, hn))                
                    fout.write('%s\n' % read)        
        elif fileType == 'fastq':
            qvs = None
            for hn,read in self.getReads():
                qvs = self.baseCallsDG.getQVForZMW(hn, 'QualityValue')
                if subreadsplit:
                    subreads = self.rgnTable.getInsertRegionForZMW(hn)
                    if self.baseCallsDG.baseCallType == 'CCS':
                        read = self.rbaseCallsDG.getBaseCallForZMW(hn)
                        subreads = self.baseCallsDG.getCCSSubreadsRegionsForZMW(hn)
                    for i,subread in enumerate(subreads):
                        if subread[1] <= subread[0]: continue 
                        fout.write('>%s/%d/%d_%d\n' % (movieName, hn, subread[0], subread[1]))                
                        fout.write('%s\n+\n%s\n' % (read[subread[0]:subread[1]], 
                                                    ''.join(map(chr, qvs[subread[0]:subread[1]]))))                        
                else:
                    fout.write('@%s/%d\n' % (movieName, hn))                    
                    fout.write('%s\n+\n%s\n' % (read, ''.join(map(chr, qvs))))
        fout.close()

    def toCSV(self, outFNPref=''):
        movieName = os.path.basename(self._h5f.filename.split('.')[0])
        outFN = '%s.csv' % movieName
        if outFNPref:
            outFN = '%s.csv' % outFNPref
        outFN = os.path.abspath(outFN)

        fout = open(outFN, 'w')
        if self.baseCallsDG.baseCallType == 'CCS':
            fout.write('ReadID,ZMWStatus,CCSReadLength,NumberOfPasses,MinQV,MaxQV,MeanQV\n')
            for hn,read in self.getReads():
                qvs = self.baseCallsDG.getQVForZMW(hn, 'QualityValue')
                fout.write('%s\n' % ','.join(map(str,['%s/%d' % (movieName,hn),
                                                      self.baseCallsDG.getStatusStringForZMW(hn),                                                      
                                                      len(read),
                                                      self.baseCallsDG.getNumberOfPassesForZMW(hn),
                                                      n.min(qvs),
                                                      n.max(qvs),
                                                      n.mean(qvs)])))
        elif self.baseCallsDG.baseCallType == 'Raw':
            fout.write('ReadID,ZMWStatus,ReadScore,ReadLength,NumberOfSubreads,NumberOfAdapters,MinQV,MaxQV,MeanQV\n')
            for hn,read in self.getReads():
                qvs = self.baseCallsDG.getQVForZMW(hn, 'QualityValue')
                fout.write('%s\n' % ','.join(map(str,['%s/%d' % (movieName,hn),
                                                      self.baseCallsDG.getStatusStringForZMW(hn),
                                                      self.baseCallsDG.getReadScoreForZMW(hn),
                                                      len(read),
                                                      len(self.rgnTable.getInsertRegionForZMW(hn)),
                                                      len(self.rgnTable.getAdapterRegionForZMW(hn)),
                                                      n.min(qvs),
                                                      n.max(qvs),
                                                      n.mean(qvs)])))

        fout.close()

    def toDetail(self, outFNPref=''):
        movieName = os.path.basename(self._h5f.filename.split('.')[0])
        outFN = '%s.dat' % movieName
        if outFNPref:
            outFN = '%s.dat' % outFNPref
        outFN = os.path.abspath(outFN)
        fout = open(outFN, 'w')

        if self.baseCallsDG.baseCallType == 'CCS':
            for hn in self.getZMWs():
                if self.baseCallsDG.getBaseCallLenForZMW(hn) > 0:
                    QVs = self.baseCallsDG.getQVForZMW(hn, 'QualityValue')
                    print >> fout, 'CCS ZMW:', hn
                    print >> fout, 'Basecalls:', self.baseCallsDG.getBaseCallForZMW(hn)
                    print >> fout, 'QV:', ''.join([chr(x) for x in QVs])
                    print >> fout, 'Number of passes:', self.baseCallsDG.getNumberOfPassesForZMW(hn)
                    print >> fout, 'Subread region:', ' '.join(['(%d, %d)' % (x[0], x[1]) for x in self.baseCallsDG.getCCSSubreadsRegionsForZMW(hn)])

        elif self.baseCallsDG.baseCallType == 'Raw':
            for hn in self.getZMWs():
                if self.baseCallsDG.getBaseCallLenForZMW(hn) > 0:
                    HQR, HQS = list(self.rgnTable.getHQRegionForZMW(hn))
                    QVs = self.baseCallsDG.getQVForZMW(hn, 'QualityValue')
                    print >> fout, 'Raw ZMW:', hn
                    print >> fout, 'Status:', self.baseCallsDG.getStatusForZMW(hn)
                    print >> fout, 'HQ Regions:',  '(%d, %d) %f' % (HQR[0], HQR[1], HQS)
                    print >> fout, 'Insert Regions:',' '.join (['(%d, %d)' % (x[0], x[1])  for x in self.rgnTable.getInsertRegionForZMW(hn)])
                    print >> fout, 'Adapter Regions:', ' '.join (['(%d, %d)' % (x[0], x[1])  for x in self.rgnTable.getAdapterRegionForZMW(hn)])
                    print >> fout, 'Basecalls:', self.baseCallsDG.getBaseCallForZMW(hn)
                    print >> fout, 'QV:', ''.join([chr(x) for x in QVs]) 
                    print >> fout, ''
                    
        fout.close()



