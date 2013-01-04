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
import numpy as n
import os
import sys
import logging
import subprocess
import h5py
import re
import datetime

from pbtools.pbh5tools.PBH5ToolsException import PBH5ToolsException
from pbcore.io.cmph5 import factory

## 
## This tool doesn't handle a number of cases gracefully. Indeed,
## about the only thing it works on is merging two or more distinct
## movies aligned to the same reference. Support has been added to
## deal with deep sorted files as well as cmp.h5 files with different
## pulse information.
##
__VERSION__ = '.2'

class CmpH5Merger():
    """
    Class for merging cmp.h5 of similar specs into one file with or
    without preserving Pulse Feature information. Sorting, Consensus,
    Barcode, etc., are not preserved.
    """
    def __init__(self, filenames, outfile, forceMerge=False):
        self._outfile = outfile
        self._seedFN = filenames[0]
        self._FNs = filenames[1:]
        self._forceMerge = forceMerge
        self._setup()
        self.offsetResets = {} ## XXX: deep-sorting


    def run(self):
        """
        Merge cmp.h5 files in _FNs onto seeding cmp.h5 file _seedFN
        """

        ##
        ## XXX : why here and below with the validation? 
        ##
        
        #Check compatibility before merge
        # if not self._forceMerge:
        #     for fin in self._FNs:
        #         cmph5_in = h5py.File(fin, 'r')
        #         if cmph5_in['/AlnInfo/AlnIndex'].shape[0] == 0:
        #             #If there is no entry in /AlnInfo/AlnIndex,
        #             #ignore this empty cmph5 file
        #             continue

        #         if self._validateCmpH5(cmph5_in, self._forceMerge):
        #             cmph5_in.close()
        #         else:
        #             cmph5_in.close()
        #             msg = "Unable to validate file {0} - incompatible for merge.".format(fin)
        #             raise PBH5ToolsException("merge", msg)

        for fin in self._FNs:
            cmph5_in = h5py.File(fin,'r')

            if cmph5_in['/AlnInfo/AlnIndex'].shape[0] == 0:
                #If there is no entry in /AlnInfo/AlnIndex,
                #ignore this empty cmph5 file
                continue
            else:
                #            if self._validateCmpH5(cmph5_in, self._forceMerge):
                self.extendMovieInfo(cmph5_in)
                self.extendRefGroup(cmph5_in)
                self.extendAlnGroup(cmph5_in)
                self.extendAlnInfo(cmph5_in)
            # else:
            #     msg = "Failed merge on file {0}.".format(fin)
            #     raise PBH5ToolsException("merge", msg)

        #CmpH5Merger may fail to merge AlnGroup/Paths with the same
        #AlnGroup/Path to one AlnGroup/Path. Fix it.
        self.mergeAlnGroupPath()

        # Reset sorting
        if self.cmph5_out['/AlnInfo/AlnIndex'].shape[0] != 0 and 'Index' in self.cmph5_out.attrs:
            self.cmph5_out['/AlnInfo/AlnIndex'][:,self._IDX['nBackRead']] = 0
            self.cmph5_out['/AlnInfo/AlnIndex'][:,self._IDX['nReadOverlap']] = 0
            self.cmph5_out.attrs.__delitem__('Index')

        if 'OffsetTable' in self.cmph5_out['/RefGroup']:
            del self.cmph5_out['/RefGroup/OffsetTable']

        self.cmph5_out.close()

        # Reset MoleculeID and set Log entry
        t_cmph5 = factory.create(self._outfile,'a')
        t_cmph5.resetMoleculeIDs()
        t_cmph5.log('CmpH5Merger.py',
                    __VERSION__,
                    str(datetime.datetime.now().isoformat()),
                    ' '.join(sys.argv),
                    'Merging')
        t_cmph5.close()

        # XXX 
        # we'll need to remove these temporarily.
        # compute the common pulse metrics. JHB
        def getAndDispose(cmpFile):
            z = h5py.File(cmpFile,'r')
            y = self._getValDict(z, False)['PulseMetrics']
            z.close()
            return y
                 
        tmplist = self._FNs
        tmplist.append(self._seedFN)
        allPulseDatasets = [ set(getAndDispose(x)) for x in tmplist]
        commonPulseDatasets = reduce(set.intersection, allPulseDatasets)
        
        # XXX reopen, remove.
        t_cmph5 = h5py.File(self._outfile, 'a')
        for path in t_cmph5['/AlnGroup/Path'].value.tolist():
            for ds in t_cmph5[path].keys():
                if not ds in commonPulseDatasets:
                    del t_cmph5[path][ds]
        t_cmph5.close()

        

    #################
    # Merge methods #
    #################
    def mergeAlnGroupPath(self):
        """
        Merge CmpH5Merger's /AlnGroup/Path.
        """
        logging.info("Merging AlnGroup/Path")
        if (self.cmph5_out['/AlnGroup/ID'].shape[0] == 0 or \
            self.cmph5_out['/AlnGroup/Path'].shape[0] == 0):
            return

        idPath     = zip(self.cmph5_out['/AlnGroup/ID'][()], \
                    self.cmph5_out['/AlnGroup/Path'][()])

        newIds     = list()
        newPaths   = list()
        newIdPath  = list()
        oldIdNewId = dict()
        for i, path in idPath:
            if not path in newPaths:
                newPaths.append(path)
                newIds.append(len(newPaths))
            oldIdNewId[i] = len(newPaths)

        newShape  = (len(newPaths), )
        self.cmph5_out['AlnGroup/ID'].resize(newShape)
        self.cmph5_out['AlnGroup/ID'][()] = n.array(newIds)
        self.cmph5_out['AlnGroup/Path'].resize(newShape)
        self.cmph5_out['AlnGroup/Path'][()] = n.array(newPaths)

        for i in range(0, len(self.cmph5_out['/AlnInfo/AlnIndex'])):
            gID = self.cmph5_out['/AlnInfo/AlnIndex'][(i, self._IDX['AlnGroupID'])]
            self.cmph5_out['/AlnInfo/AlnIndex'][(i,self._IDX['AlnGroupID'])] = oldIdNewId[gID]

    def extendAlnInfo(self, cmph5_in):
        """
        Merge cmph5_in's /AlnInfo with the seeds.
        """
        logging.info('Extending alninfo from [%s]' % cmph5_in.filename.split('/')[-1])

        aIdx_in = cmph5_in['/AlnInfo/AlnIndex'].value
        aIdx = self.cmph5_out['/AlnInfo/AlnIndex']

        if len(self.offsetResets):
            ## XXX: deep-sorting.
            aMap = dict(zip(cmph5_in['AlnGroup/ID'][:], cmph5_in['AlnGroup/Path'][:]))
            for i in xrange(0, aIdx_in.shape[0]):
                reset = self.offsetResets[aMap[aIdx_in[i, self._IDX['AlnGroupID']]]]
                aIdx_in[i, self._IDX['Offset_begin']] += reset
                aIdx_in[i, self._IDX['Offset_end']] += reset

        aIdx_in[:,self._IDX['AlnID']] = aIdx_in[:,self._IDX['AlnID']] + aIdx.shape[0]
        aIdx_in[:,self._IDX['MovieID']] = n.array([self.F_MovieID[x] for x
                                                   in aIdx_in[:,self._IDX['MovieID']]], dtype='uint32')
        aIdx_in[:,self._IDX['AlnGroupID']] = n.array([self.F_AlnGroupPath[x] for x
                                                      in aIdx_in[:,self._IDX['AlnGroupID']]], dtype='uint32')
        aIdx_in[:,self._IDX['RefGroupID']] = n.array([self.F_RefGroupPath[x] for x
                                                      in aIdx_in[:,self._IDX['RefGroupID']]], dtype='uint32')
        self._extendDset(aIdx, aIdx_in)

        for subgrp in [key for key in self.cmph5_out['/AlnInfo'].keys() if key != 'AlnIndex']:
            dout = self.cmph5_out['/AlnInfo'][subgrp]
            newVal = cmph5_in['/AlnInfo'][subgrp].value
            self._extendDset(dout, newVal)

        self.cmph5_out['/AlnInfo'].attrs.modify('nRow', self.cmph5_out['/AlnInfo/AlnIndex'].shape[0])

    def mergeDatasetsFromGroups(self, cmph5_in, sourceGroupName, targetGroupName):
        ## XXX: deep-sorting
        sourceGroup = cmph5_in[sourceGroupName]
        targetGroup = self.cmph5_out[targetGroupName]
        offsetReset = -1
        for datasetName in sourceGroup.keys():
            if datasetName in targetGroup:
                targetDataset = targetGroup[datasetName]
                sourceDataset = sourceGroup[datasetName]
                if len(sourceDataset.shape) == 1:
                    start = len(targetDataset)
                    newSize = start + len(sourceDataset)
                    targetDataset.resize((newSize, ))
                    targetDataset[start:newSize] = sourceDataset[:]
                    offsetReset = start ## ugly, same value for all datasets in group.
                else:
                    raise PBH5ToolsException("merge", "Don't know how to deal with rank" +
                                             "> 1 datasets.")
        self.offsetResets[targetGroupName] = offsetReset

    def extendAlnGroup(self,cmph5_in):
        """
        Merge cmph5_in's /AlnGroup with the seeds.
        """
        logging.info('Extending alngroups from [%s]' % cmph5_in.filename.split('/')[-1])

        cache_AGP = cmph5_in['/AlnGroup/Path'].value.tolist()
        lastRGRPID = n.max(self.cmph5_out['/AlnGroup/ID'].value.tolist())
        rgpMap = dict(zip(cache_AGP,cmph5_in['/AlnGroup/ID'].value.tolist()))
        allRGRPs = [str(x) for x in cache_AGP]
        for rgp in allRGRPs:
            if not self.C_RGPToCopy.get(rgp):
                self.C_RGPToCopy[rgp] = rgp

        alngrp = [[None]*len(self.C_RGPToCopy) for i in xrange(3)] # newAlnGrpID, oldAlnGrpID, newAlnGrpPath
        cg = 0
        for subgrp in self.C_RGPToCopy.iteritems():
            logging.debug("Copying %s to %s." % (subgrp[0], subgrp[1]))
            ## XXX: NULL_GROUP probably doesn't ever occur?
            if not subgrp[0].endswith("NULL_GROUP") and not subgrp[1] in self.cmph5_out:
                self.cmph5_out.copy(cmph5_in[subgrp[0]], subgrp[1]) # Most expensive operation!
            else:
                ## XXX: deep-sorting
                if subgrp[1] in self.cmph5_out:
                    self.mergeDatasetsFromGroups(cmph5_in, subgrp[0], subgrp[1])

            lastRGRPID += 1
            alngrp[0][cg] = lastRGRPID
            alngrp[1][cg] = rgpMap[subgrp[0]]
            alngrp[2][cg] = subgrp[1]
            cg += 1

        dout = self.cmph5_out['/AlnGroup/Path']
        newVal = n.array(alngrp[2][:cg], dtype=object)
        self._extendDset(dout, newVal)

        dout = self.cmph5_out['/AlnGroup/ID']
        newVal = n.array(alngrp[0][:cg], dtype='uint32')
        self._extendDset(dout, newVal)

        # Get mappings to fix AlignmentIndex
        for i in zip(alngrp[1][:cg],alngrp[0][:cg]):
            self.F_AlnGroupPath[i[0]] = i[1]

        self.cmph5_out['/AlnGroup'].attrs.modify('nRow', self.cmph5_out['/AlnGroup/ID'].shape[0])

    def extendRefGroup(self, cmph5_in):
        """
        Merge cmph5_in's /RefGroup with the seeds.
        """
        logging.info('Extending refgroups from [%s]' % cmph5_in.filename.split('/')[-1])

        t_refDict = self._getRefDict(cmph5_in)
        lastRefID = n.max(self.cmph5_out['/RefGroup/ID'].value)
        lastRefName = n.sort(self.cmph5_out['/RefGroup/Path'].value)[-1]
        self.F_AlnGroupPath = {}
        self.C_RGPToCopy = {} # input rgrp: output rgrp
        changeMap = {} # inputCmph5 RefGroupPath: outputCmph5 RefGroupPath
        if self.refDict != t_refDict:
            for ref in t_refDict:
                exists = False
                for backref in self.refDict:
                    if self.refDict[backref] == t_refDict[ref]:
                        changeMap[ref] = backref
                        exists = True
                if not exists:
                    newRefName = ref
                    if ref in self.refDict:
                        t_lastRefName = n.sort(changeMap.values())[-1] if changeMap else lastRefName
                        newRefName = '/ref%06d' % n.max(map(lambda x: int(findall('ref(\\d+)', x)[0])+1,
                                                            [t_lastRefName, lastRefName]))
                        lastRefName = newRefName
                    lastRefID += 1

                    changeMap[ref] = newRefName
                    self.outIDDict[newRefName] = lastRefID
        else:
            t = self.cmph5_out['/RefGroup/Path'].value.tolist()
            changeMap = dict(zip(t,t))

        inIDDict = dict(zip(cmph5_in['/RefGroup/Path'].value,cmph5_in['/RefGroup/ID'].value))
        self.F_RefGroupPath = dict([(inIDDict[x[0]],self.outIDDict[x[1]]) for x in changeMap.items()])

        cache_RIFN = self.cmph5_out['/RefInfo/FullName'].value
        cache_RIID = self.cmph5_out['/RefInfo/ID'].value
        t_lastRefInfoID = n.max(self.cmph5_out['/RefGroup/RefInfoID'])

        refg = [[None]*len(changeMap) for i in xrange(3)] # ID, Path, RefInfoID
        refi = [[None]*len(changeMap) for i in xrange(4)] # ID, FullName, Length, MD5
        ci = 0
        cg = 0
        for oldRefPath in changeMap:
            newRefPath = changeMap[oldRefPath]
            if not self.refDict.get(newRefPath):
                # RefGroupID
                self.refDict[newRefPath] = t_refDict[oldRefPath]
                refg[0][cg] = self.outIDDict[newRefPath]

                # RefGroupPath
                refg[1][cg] = newRefPath

                # RefInfo
                if self.refDict[newRefPath][0] in cache_RIFN:
                    idx = n.nonzero(cache_RIFN == self.refDict[newRefPath][0])[0]
                    lastRefInfoID = cache_RIID[idx][0]
                    refg[2][cg] = lastRefInfoID
                else:
                    t_lastRefInfoID = t_lastRefInfoID + 1
                    refg[2][cg] = t_lastRefInfoID

                    refi[0][ci] = t_lastRefInfoID
                    refi[1][ci] = self.refDict[newRefPath][0]
                    refi[2][ci] = self.refDict[newRefPath][1]
                    refi[3][ci] = self.refDict[newRefPath][2]
                    ci += 1
                cg += 1

                # Add new RefGroup
                self.cmph5_out.create_group(newRefPath)
                for subgrp in cmph5_in[oldRefPath].values():
                    if not re.findall('Consensus',subgrp.name):
                        self.C_RGPToCopy[subgrp.name] = self._fixRefId(newRefPath[1:], subgrp.name)

            elif self.refDict.get(newRefPath) and newRefPath != oldRefPath:
                for subgrp in cmph5_in[oldRefPath].values():
                    if not re.findall('Consensus',subgrp.name):
                        self.C_RGPToCopy[subgrp.name] = self._fixRefId(newRefPath[1:], subgrp.name)

        if ci:
            for i,dset in enumerate([('ID','uint32'),('FullName',object),('Length','uint32'),('MD5',object)]):
                dout = self.cmph5_out['/RefInfo'][dset[0]]
                newVal = n.array(refi[i][:ci], dtype=dset[1])
                self._extendDset(dout, newVal)

        if cg:
            for i,dset in enumerate([('ID','uint32'),('Path',object),('RefInfoID','uint32')]):
                dout = self.cmph5_out['/RefGroup'][dset[0]]
                newVal = n.array(refg[i][:cg], dtype=dset[1])
                self._extendDset(dout, newVal)

        self.cmph5_out['/RefGroup'].attrs.modify('nRow', self.cmph5_out['/RefGroup/ID'].shape[0])
        self.cmph5_out['/RefInfo'].attrs.modify('nRow', self.cmph5_out['/RefInfo/ID'].shape[0])

    def extendMovieInfo(self, cmph5_in):
        """
        Merge cmph5_in's /MovieInfo with the seeds.
        Notes: Using .value and NOT .value.tolist() to avoid strange
        events when comparing string with numpy.object_
        """
        logging.info('Merging %d movies from [%s] into the existing %d' %
                     (cmph5_in['/MovieInfo/Name'].shape[0],
                      cmph5_in.filename.split('/')[-1],
                      self.cmph5_out['/MovieInfo/Name'].shape[0]))

        # Extend MovieInfo ONLY with new movies
        cache_MIMin = cmph5_in['/MovieInfo/Name'].value
        cache_MIMout = self.cmph5_out['/MovieInfo/Name'].value
        newMovies = [m for m in cache_MIMin if m not in cache_MIMout]
        tin_movieDict = dict(zip(cache_MIMin, cmph5_in['/MovieInfo/ID'].value))
        tout_movieDict = dict(zip(cache_MIMout, self.cmph5_out['/MovieInfo/ID'].value))
        if newMovies:
            newidx = [cmph5_in['/MovieInfo/Name'].value == m for m in newMovies]
            newidx = reduce(lambda x,y: x|y,newidx)
            oldidx = n.logical_not(newidx)
            self.F_MovieID = [(tin_movieDict[m],tout_movieDict[m]) for m in cache_MIMin[oldidx]]

            for dsetName in ['Exp','Name','Run', 'FrameRate']:
                if dsetName in self.cmph5_out['/MovieInfo'].keys():
                    dout = self.cmph5_out['/MovieInfo'][dsetName]
                    din = cmph5_in['/MovieInfo'][dsetName]
                    self._extendDset(dout, din.value[newidx])

            # MovieID
            offsetID = n.max(self.cmph5_out['/MovieInfo/ID'].value) + 1
            dout = self.cmph5_out['/MovieInfo/ID']
            din = cmph5_in['/MovieInfo/ID'].value[newidx]
            newVal = n.array(range(offsetID, offsetID + din.shape[0]), dtype='uint32')
            self._extendDset(dout, newVal)

            self.F_MovieID.extend(zip(din,newVal))
            self.F_MovieID = dict(self.F_MovieID)

            # Fix MasterDataset nRow
            self.cmph5_out['/MovieInfo'].attrs.modify('nRow', self.cmph5_out['/MovieInfo/ID'].shape[0])
        else:
            self.F_MovieID = dict([(tin_movieDict[m],tout_movieDict[m]) for m in cache_MIMin])

    #################
    # Setup methods #
    #################

    def _setup(self):
        """
        Setup CmpH5Merger using the first input cmp.h5 as the yardstick
        for comparing the rest and making sure they meet the same standards
        """
        badSeed = True

        ## XXX this doesn't seem that safe, e.g., what if they are all empty. 
        while badSeed:
            self.cmph5_out = h5py.File(os.path.abspath(self._seedFN), 'r')
            self._valDict = self._getValDict(self.cmph5_out, self._forceMerge)

            # If it is empty and we have at least one more cmpH5, make that the seed and toss this one.
            if not self._valDict['AlnInfoDSets'] and len(self._FNs) > 0:
                logging.info('Rejecting [%s] as seed file' % self._seedFN
                    + ' (0-size AlignmentIndex or AlnGroups don\'t share the'
                    + ' same datasets)')
                self._seedFN = self._FNs[0]
                self._FNs = self._FNs[1:]
                self.cmph5_out.close()
            else:
                badSeed = False
                self.cmph5_out.close()
                logging.info('Copying seed cmp.h5 from [%s]' % self._seedFN)
                subprocess.call('cp %s %s' % (os.path.abspath(self._seedFN), self._outfile), shell=True)
                self.cmph5_out = h5py.File(self._outfile, 'r+')

        # Check if the seed is empty
        if not self._valDict['AlnInfoDSets'] and not len(self._FNs):
            logging.info('The seed [%s] has no alignments and there are no more files left to merge' %
                         self._seedFN)

        else:
            # Get AlignmentIndex column indices
            self._IDX = factory.create(self._seedFN,'r')._colName2Index

            # Private methods for processing
            self._fixRefId = lambda newSt,oldSt: re.sub('ref\d+', newSt, oldSt)

            # Sanitize the seed
            self._sanitizeSeed()

            # Create reference dictionary
            self.refDict = self._getRefDict(self.cmph5_out)
            self.outIDDict = dict(zip(self.cmph5_out['/RefGroup/Path'].value,self.cmph5_out['/RefGroup/ID'].value))

            # Remove consensus
            for rgrp in self.cmph5_out['/RefGroup/Path'].value.tolist():
                if 'Consensus' in self.cmph5_out[rgrp].keys():
                    del self.cmph5_out[rgrp+'/Consensus']

            # Remove sorting
            if 'OffsetTable' in self.cmph5_out['/RefGroup'].keys():
                del self.cmph5_out['/RefGroup/OffsetTable']

         

    def _sanitizeSeed(self):
        """
        Reset all IDs found in /AlnGroup/ID and /MovieInfo/ID, to series
        of integers starting at 1 and ending at the number of rows of
        each dataset.
        """
        aIdx = self.cmph5_out['/AlnInfo/AlnIndex']

        # Fix MovieID and ReadGroupPathID
        dsetMap = {'/MovieInfo/ID':'MovieID','/AlnGroup/ID':'AlnGroupID'}
        for dsetName in dsetMap:
            idFIX = {}
            toFix = False
            for i,t_id in enumerate(self.cmph5_out[dsetName].value):
                idFIX[t_id] = i+1
                if t_id != i+1:
                    toFix = True
                    self.cmph5_out[dsetName][i] = i+1

            if idFIX and toFix:
                aIdx[:,self._IDX[dsetMap[dsetName]]] = n.array([idFIX[x] for x in
                                                                aIdx[:,self._IDX[dsetMap[dsetName]]]],
                                                               dtype='uint32')
    def _getValDict(self, cmph5, ignorePM=False):
        """
        Generate dictionary used for validating .cmp.h5 files on their
        own as well as against each other.
        """
        if cmph5['/AlnInfo/AlnIndex'].shape[0] == 0:
            return {'AlnInfoDSets':'','PulseMetrics':''}
        valDict = {}

        if not ignorePM:
            valDict['PulseMetrics'] = []
            a = [sorted(cmph5[grp].keys()) for grp
                 in cmph5['/AlnGroup/Path'].value.tolist() if 'AlnArray' in cmph5[grp].keys()]
            valDict['PulseMetrics'] = a[0]
            if filter(lambda x: x != a[0], a):
                return {'AlnInfoDSets':'','PulseMetrics':''}

        valDict['AlnInfoDSets'] = sorted(cmph5['/AlnInfo'].keys())

        return valDict

    ##################
    # Helper Methods #
    ##################

    def _validateCmpH5(self, cmph5, ignorePM=False):
        """
        Validate cmph5 against the seed.
        """
        t_valDict = self._getValDict(cmph5, ignorePM)
        if not t_valDict['AlnInfoDSets']:
            logging.error('Rejecting [%s] since it has a 0-sized AlnIndex' % cmph5.filename)
        elif sorted(t_valDict['AlnInfoDSets']) != sorted(self._valDict['AlnInfoDSets']):
            t_mdsets = ','.join([d for d in self._valDict['AlnInfoDSets'] if d not in t_valDict['AlnInfoDSets']])
            logging.error('Rejecting [%s] since it is missing AlnInfo DataSets: %s' % (cmph5.filename, t_mdsets))

        ## XXX : this check makes it impossible to merge files with
        ## different pulse datasets present.
        # if not ignorePM:
        #     if not t_valDict['PulseMetrics']:
        #         logging.info('Rejecting [%s] since AlnGroup datasets are not shared by all AlnGroups' % cmph5.filename)
        #     elif sorted(t_valDict['PulseMetrics']) != sorted(self._valDict['PulseMetrics']):
        #         t_mdsets = ','.join([d for d in self._valDict['PulseMetrics'] if d not in t_valDict['PulseMetrics']])
        #         logging.info('Rejecting [%s] since it is missing AlnGroup DataSets: %s' % (cmph5.filename, t_mdsets))

        return self._getValDict(cmph5, ignorePM) == self._valDict

    def _getRefDict(self,cmph5):
        """
        Encapsulate all data from /RefGroup/ into a dictionary.
        Notes: Caching into lists necessary for speed and to avoid
        having numpy.object_ isntances instead of strings.
        """
        rInfo = dict(zip(cmph5['/RefInfo/ID'].value.tolist(),
                         zip(cmph5['/RefInfo/FullName'].value.tolist(),
                             cmph5['/RefInfo/Length'].value.tolist(),
                             cmph5['/RefInfo/MD5'].value.tolist())))
        cache_RGP = cmph5['/RefGroup/Path'].value.tolist()
        cache_RGRID = cmph5['/RefGroup/RefInfoID'].value.tolist()
        return dict([(cache_RGP[i],rInfo[rID])for i,rID in enumerate(cache_RGRID)])

    def _extendDset(self, dout, newVal):
        """
        Extend the dout HDF5 Dataset with newVal. Set the 'lastRow'
        attribute where appropriate.
        """
        newVLen = newVal.shape[0]
        oldVlen = dout.shape[0]

        if len(dout.shape) == 1:
            newShape = (dout.shape[0] + newVLen,)
            dout.resize(newShape)
            dout[oldVlen:(oldVlen + newVLen)] = newVal
        else:
            newShape = (dout.shape[0] + newVLen, dout.shape[1])
            dout.resize(newShape)
            dout[oldVlen:(oldVlen + newVLen),:] = newVal

        if 'lastRow' in dout.attrs.keys():
            dout.attrs.modify('lastRow', oldVlen+newVLen)



