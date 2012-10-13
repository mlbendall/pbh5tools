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

import pbcore.io.rangeQueries as RQ

__VERSION__ = ".72"

class CmpH5Format:
     def __init__(self, cmpH5):
        if ('Version' in cmpH5.attrs):
            self.VERSION = cmpH5.attrs['Version']
        
        self.ALN_INFO             = 'AlnInfo'
        self.REF_INFO             = 'RefInfo'
        self.MOVIE_INFO           = 'MovieInfo'
        self.REF_GROUP            = 'RefGroup'
        self.ALN_GROUP            = 'AlnGroup'
        self.ALN_INDEX_NAME       = 'AlnIndex'
        self.ALN_INDEX            = '/'.join([self.ALN_INFO, self.ALN_INDEX_NAME])

        self.REF_GROUP_ID         = '/'.join([self.REF_GROUP, 'ID'])
        self.REF_GROUP_PATH       = '/'.join([self.REF_GROUP, 'Path'])
        self.REF_OFFSET_TABLE     = '/'.join([self.REF_GROUP, 'OffsetTable'])

        self.ALN_GROUP_ID         = '/'.join([self.ALN_GROUP, 'ID'])
        self.ALN_GROUP_PATH       = '/'.join([self.ALN_GROUP, 'Path'])

        (self.ID, self.ALN_ID, self.MOVIE_ID, self.REF_ID, self.TARGET_START, 
         self.TARGET_END, self.RC_REF_STRAND, self.HOLE_NUMBER, self.SET_NUMBER, 
         self.STROBE_NUMBER, self.MOLECULE_ID, self.READ_START, self.READ_END, 
         self.MAP_QV, self.N_MATCHES, self.N_MISMATCHES, self.N_INSERTIONS, 
         self.N_DELETIONS, self.OFFSET_BEGIN, self.OFFSET_END, self.N_BACK, 
         self.N_OVERLAP) = range(0, 22)

        self.extraTables = [ '/'.join([self.ALN_INFO, x]) for x in cmpH5[self.ALN_INFO].keys() 
                             if not x == self.ALN_INDEX_NAME]


def numberWithinRange(s, e, vec):
    """
    Compute the number of elements in vec (where vec is sorted), such
    that each element, e obeys the following constraint: start <= e <
    end.
    """
    lI = RQ.leftmostBinSearch(vec, s)
    rI = RQ.rightmostBinSearch(vec, e)
    return(len(filter(lambda x : s <= x < e, vec[lI:rI])))
    

def computeIndices(tStart, tEnd):
    """
    Given a sorted (tStart, tEnd) compute a two-column matrix with
    columns nBack and nOverlap.

    nBack is defined as follows: given a position j, nBack is the
    offset for the smallest i, such that tEnd[i] > tStart[j], i.e., j
    - nBack == i.

    nOverlap is defined as follows: given a position j, nOverlap is |
    tEnd[i] > tStart[j] | for all i in 1,...,j - 1.
    """
    res = NP.zeros(2 * len(tStart), dtype = "int32").reshape(len(tStart), 2)

    for i in range(len(tStart) - 1, 0, -1):
        j = i - 1
        nBack = 0
        nOver = 0

        while (j >= 0):
            if (tEnd[j] > tStart[i]):
                nOver += 1
                nBack = (i - j)
            j -= 1

        res[i, 0] = nBack
        res[i, 1] = nOver
    return(res)


def computeIndicesDP(tStart, tEnd):
    """
    Given a sorted tStart, tEnd compute a two-column matrix with
    columns nBack and nOverlap.

    nBack is defined as follows: given a position j, nBack is the
    offset for the smallest i, such that tEnd[i] > tStart[j], i.e., j
    - nBack == i.

    nOverlap is defined as follows: given a position j, nOverlap is |
    tEnd[i] > tStart[j] | for all i in 1,...,j - 1.

    This is a dynamic programming implementation and is *substantially*
    faster than computeIndices.
    """
    res = NP.zeros(2 * len(tStart), dtype = "int32").reshape(len(tStart), 2)
    sortedEnds = NP.sort(tEnd)

    for i in range(1, len(tStart)):
        nEnding = numberWithinRange(tStart[i - 1], tStart[i], sortedEnds - 1)

        if (nEnding == 0):
            res[i, 0] = res[i - 1, 0] + 1            
            res[i, 1] = res[i - 1, 1] + 1
        else:
            res[i, 1] = res[i - 1, 1] - nEnding + 1

            advance = 0
            for k in range(i - 1 - res[i - 1, 0], i):
                if (tEnd[k] > tStart[i]):
                    break
                advance += 1
            res[i, 0] = res[i - 1, 0] - advance + 1

    return(res)


def computeRefIndexTable(refIDs, refIDVector):
    """
    Compute a table of offsets for refID given the unique refIDs in
    the file.
    """
    def table(vector, bins):
        counts = dict(zip(bins, [0]*len(bins)))
        for i in xrange(0, len(vector)):
            counts[vector[i]]+= 1
        return counts

    ## XXX: In practice, these should already be sorted, but they
    ## might not be on occassion. In that case, you get the offset
    ## structure out of sync with the AlnIndex. The trick is to do it
    ## sorted and then to unsort it. Bug 20878
    rperm = NP.argsort(refIDs)
    rcnts = table(refIDVector, refIDs[rperm]).values()
    rsums = NP.cumsum(rcnts)
    offsetStart = NP.concatenate((NP.array([0]), rsums[:-1]))
    offsets = NP.array(zip(refIDs[rperm], offsetStart, rsums), dtype = "uint32")
    offsets = offsets[NP.array(range(0, offsets.shape[0]))[NP.argsort(rperm)],:]
    assert(all(offsets[:,0] == refIDs))
    return offsets

def __pathExists(h5, path):
    try:
        h5[path]
        return True
    except Exception, E:
        return False

def __repackDataArrays(cH5, format, fixedMem = False, maxDatasetSize = 2**31 - 1):
    """
    Flatten read groups according to an indexed cmp.h5 file.
    """
    alnGroups = [x for x in cH5[format.ALN_GROUP_PATH]]
    pulseDatasets = [cH5[x].keys() for x in alnGroups]
    uPulseDatasets = sorted(list(reduce(lambda x,y: set.union(set(x), set(y)), pulseDatasets)))

    # check to make sure that all aln groups have the same datasets -
    # a set.equal operation would help
    for pd in pulseDatasets:
         error = False
         spd = sorted(pd)
         if len(spd) == len(uPulseDatasets):
              if any([ (x != y) for (x,y) in zip(spd, uPulseDatasets) ]):
                   error = True
         else:
              error = True
         if error:
              raise Exception("Datasets must agree:\n" + ",".join(spd) + 
                              "\nvs\n" + ",".join(uPulseDatasets))
    
    readGroupPaths = dict(zip(cH5[format.ALN_GROUP_ID], [ x for x in cH5[format.ALN_GROUP_PATH]]))
    refGroupPaths = dict(zip(cH5[format.REF_GROUP_ID], [ x for x in cH5[format.REF_GROUP_PATH]]))
    uPDAndType = dict(zip(uPulseDatasets, [ cH5[readGroupPaths.values()[0]][z].dtype for z in uPulseDatasets ]))

    ## XXX : this needs to be augmented with some saftey on not loading too much data.
    ##       - set a bound on the number of elts in the cache. 
    pdsCache = {} 

    def getData(read, ds, start, end):
        key = "/".join((readGroupPaths[read[format.ALN_ID]], ds))
        if not pdsCache.has_key(key):
            logging.debug("Cacheing: %s" % key)
            h5DS = cH5[key]
            smallEnoughToFitInMemory = ((h5DS.len() * h5DS.dtype.itemsize)/1024**3) < 12
            pdsCache[key] = h5DS
            if not fixedMem and smallEnoughToFitInMemory:
                logging.debug("Reading %d G." % ((h5DS.len() * h5DS.dtype.itemsize)/1024**3))
                pdsCache[key] = pdsCache[key][:]
        return(pdsCache[key][start:end])

    def getRefGroup(gID):
         return(cH5[refGroupPaths[gID]])

    def chooseAlnGroupNames(gID, readBlocks):
         rGroup = cH5[refGroupPaths[gID]]
         currentGroups = rGroup.keys()
         rint = NP.random.randint(1000, 9999)
         pref = 'rg' + str(rint) + '-'
         newNames = [ pref + str(i) for i,j in enumerate(readBlocks) ]
         if any([ nn in currentGroups for nn in newNames ]):
              return chooseAlnGroupNames(gID, readBlocks)
         else:
              return newNames

    offsets = cH5[format.REF_OFFSET_TABLE].value
    sAI = cH5[format.ALN_INDEX]
    orderedRefPaths = [""] * offsets.shape[0]
    maxDataSize = int(maxDatasetSize)
    
    ## These are updated in the main loop.
    currentAlnID = 1
    refGroupAlnGroups = []
    
    for row in xrange(0, offsets.shape[0]):
        logging.info("Processing reference: %d of %d" % (row + 1, offsets.shape[0]))

        groupID = offsets[row, 0]
        fRow = offsets[row, 1]
        lRow = offsets[row, 2]
        if (lRow == fRow):
            continue 

        reads = sAI[fRow:lRow,:]
        alens = reads[:,format.OFFSET_END] - reads[:,format.OFFSET_BEGIN]
        clens = NP.concatenate((NP.array([0], "uint64"), NP.cumsum(alens + 1)))
        tSize = clens[len(clens) - 1]
        
        readBlocks = []
        if tSize >= maxDatasetSize:
             lastStart  = 0
             for i in xrange(0, len(clens)):
                  if clens[i]-clens[lastStart] >= maxDatasetSize:
                       readBlocks.append((lastStart, i))
                       lastStart = i
             if lastStart < reads.shape[0]:
                  readBlocks.append((lastStart, reads.shape[0]))
        else:
             readBlocks = [(0, reads.shape[0])]

        # choose all the names at once for a particular reference. It
        # is important to ensure that sorting the same file again and
        # again works.
        newGroupNames = chooseAlnGroupNames(groupID, readBlocks) 

        for i,readBlock in enumerate(readBlocks):
             logging.debug("Processing readBlock (%d, %d)" % readBlock)
             dsLength = clens[readBlock[1]] - clens[readBlock[0]]
             newGroup = getRefGroup(groupID).create_group(newGroupNames[i])
             
             for pulseDataset in uPulseDatasets: 
                  logging.debug("Processing dataset: %s" % pulseDataset)
                  newDS = NP.zeros(dsLength, dtype = uPDAndType[pulseDataset])

                  currentStart = 0
                  for readIdx in xrange(readBlock[0], readBlock[1]):
                       read = reads[readIdx, ]
                       gStart, gEnd = currentStart, currentStart + alens[readIdx]
                       newDS[gStart:gEnd] = getData(read, pulseDataset, 
                                                    read[format.OFFSET_BEGIN], 
                                                    read[format.OFFSET_END])
                       currentStart = gEnd + 1

                  ## XXX : the tuples are necessary.
                  newGroup.create_dataset(pulseDataset, data = newDS, 
                                          dtype = uPDAndType[pulseDataset], 
                                          maxshape = (None, ), chunks = (16384,))
                  logging.debug("flushing:" + ",".join(pdsCache.keys()))
                  pdsCache = {}
                  


             ## once you have moved all data for a readBlock you can change
             ## the offsets.
             currentStart = 0
             for readIdx in xrange(readBlock[0], readBlock[1]):
                  read = reads[readIdx, ]
                  gStart, gEnd = currentStart, currentStart + alens[readIdx]
                  reads[readIdx, format.OFFSET_BEGIN] = gStart
                  reads[readIdx, format.OFFSET_END] = gEnd
                  reads[readIdx, format.ALN_ID] = currentAlnID
                  currentStart = gEnd + 1

             ## now write it back; have to map back into the global coord system.
             sAI[(fRow + readBlock[0]):(fRow + readBlock[1]),] = reads[readBlock[0]:readBlock[1],]
        
             ## increment the currentAlnID
             currentAlnID = currentAlnID + 1
        
        ## add the new group names to the list.
        for ngn in newGroupNames:
             refGroupAlnGroups.append("/".join((refGroupPaths[groupID], ngn)))

    ## re-identify them.
    sAI[:,format.ID] = range(1, sAI.shape[0] + 1)
    assert(len(refGroupAlnGroups) == currentAlnID - 1)

    logging.info("Writing new AlnGroupPath values.")
    del(cH5[format.ALN_GROUP_PATH])
    del(cH5[format.ALN_GROUP_ID])
    cH5.create_dataset(format.ALN_GROUP_PATH, data = map(str, refGroupAlnGroups), ## XXX : unicode.
                       dtype = H5.special_dtype(vlen = str), maxshape = (None,), chunks = (256,))
    cH5.create_dataset(format.ALN_GROUP_ID, data = range(1, currentAlnID),
                       dtype = "int32", maxshape = (None,), chunks = (256,))
    logging.info("Wrote new AlnGroupPath values.")
    
    for rg in readGroupPaths.values():
         ## this should never be false, however, MC has produced
         ## files in the past where there are duplicate paths with
         ## different IDs and therefore you'll error here (probably
         ## out of spec)
         if rg in cH5:
              del(cH5[rg])
         else:
              logging.warn("Input cmp.h5 file is out of spec, duplicate " + 
                           "alignment group paths with different IDs (sorting is unaffected)")
   

def sortCmpH5(inFile, outFile, tmpDir, deep = True, useNative = True, inPlace = False):
    """ 
    This routine takes a cmp.h5 file and sorts the AlignmentIndex
    table adding two additional columns for fast access. In addition,
    a new top-level attribute is added to the indicate that the file
    has been sorted, as well as a table to indicate the blocks of the
    alignment index associated with each reference group.
    """
    success = False;
    fout    = None # use fout as a flag to indicate that we need to copy
                   # something over after success.

    if outFile:
         # process the copied version, original should always be fine. 
         shutil.copyfile(inFile, outFile)
         _inFile = outFile
    elif inPlace:
         # process the input directly, no copies. failure in the
         # middle means corrupt file.
         _inFile = inFile
         outFile = _inFile
    elif tmpDir:
         # make copy, work there, copy back - safer, but slower.
         fout = tempfile.NamedTemporaryFile(suffix = '.cmp.h5', dir = tmpDir)
         _inFile = fout.name
         shutil.copyfile(inFile, _inFile)
         outFile = _inFile
    else:
         raise Exception("Improper call, must specify outFile, tmpDir, or inPlace must be True.")
    
    logging.info("Processing inFile: %s saving in outFile: %s" % (_inFile, outFile))


    ## Setup the indexer.
    if (useNative):
        from pbtools.pbh5tools import Indexer
        myIndexer = Indexer.Indexer().compute

    def computeIndices(tStart, tEnd):
        if (not useNative):
            return computeIndicesDP(tStart, tEnd)
        else:
            return myIndexer(tStart, tEnd)

    try:
        cH5 = H5.File(_inFile, 'a')
        format = CmpH5Format(cH5)
        logging.info("Read cmp.h5 with version %s" % format.VERSION)

        aI = cH5[format.ALN_INDEX]
        originalAttrs = aI.attrs.items()

        ## empty is a special case. In general, h5py handles
        ## zero-length slices poorly and therefore I don't want to
        ## make them. Therefore, I maintain the 'empty' variable to
        ## indicate that. This makes some code less pleasing, e.g.,
        ## computing the reference index data structure.
        if (aI.shape[0] == 0):
            logging.debug("Warning: %s empty!" % _inFile)
            success = True;
            return True; 
        
        # sort the AlignmentIndex
        aord = NP.lexsort([aI[:,format.TARGET_END], aI[:,format.TARGET_START], 
                           aI[:,format.REF_ID]])

        assert(len(aord) == aI.shape[0])
        
        sAI = aI.value[aord,:]
        del(aI)
        logging.info("Sorted AlignmentIndex.")

        # construct reference offset datastructure.
        refSeqIDs = cH5[format.REF_GROUP_ID]
        offsets = computeRefIndexTable(refSeqIDs.value, sAI[:,format.REF_ID])
        logging.info("Constructed offset datastructure.")
        
        # check that the offset data structure and the index are consistent.
        assert(all([all(offsets[i,0] == sAI[offsets[i,1]:offsets[i,2],format.REF_ID]) 
                    for i in range(0, offsets.shape[0])]))
        
        # fill overlap and back columns.
        for row in range(0, offsets.shape[0]):
            fRow = int(offsets[row, 1])
            lRow = int(offsets[row, 2])
            if (lRow - fRow <= 0):
                continue
            sAI[fRow:lRow, (format.N_BACK, format.N_OVERLAP)] = computeIndices(sAI[fRow:lRow, format.TARGET_START], 
                                                                               sAI[fRow:lRow, format.TARGET_END])

        logging.info("Constructed indices.")

        # modify the cmp.h5 file.
        # We want to keep the chunking info on the dataset.
        del(cH5[format.ALN_INDEX])
        cH5.create_dataset(format.ALN_INDEX, data = sAI, dtype = H5.h5t.NATIVE_UINT32,
                           maxshape = (None, None))
        
        ## If the file is already sorted there's no harm in resorting.
        if (__pathExists(cH5, format.REF_OFFSET_TABLE)):
            logging.info(format.REF_OFFSET_TABLE + " already exists, deleting.")
            del(cH5[format.REF_OFFSET_TABLE])

        ## create the offset datastructure in the file.
        cH5.create_dataset(format.REF_OFFSET_TABLE, data = offsets, 
                           dtype = H5.h5t.NATIVE_UINT32, maxshape = (None, None))

        ## add the index attribute.
        cH5['/'].attrs.create("Index", ['REF_ID', 'TARGET_START', 'TARGET_END'])

        ## fixup attributes.
        for oA in originalAttrs:
            cH5[format.ALN_INDEX].attrs.create(oA[0], oA[1])

        ## deep repacking.
        if (deep):
            logging.info("Repacking alignment arrays.")
            __repackDataArrays(cH5, format)
            
        ## memory free.
        del sAI
        
        ## manage any extra datasets.
        for extraTable in format.extraTables:
            if (__pathExists(cH5, extraTable)):
                logging.info("Sorting table: %s" % extraTable)

                eTable = cH5[extraTable].value
                if (len(eTable.shape) == 1):
                    eTable = eTable[aord]
                else:
                    eTable = eTable[aord,:]

                ## save attributes, if any for re-writing below.
                originalAttrs = cH5[extraTable].attrs.items()

                del(cH5[extraTable])
                cH5.create_dataset(extraTable, data = eTable, 
                                   maxshape = tuple([None for x in eTable.shape]))
                for oA in originalAttrs:
                    cH5[extraTable].attrs.create(oA[0], oA[1])

        ## if you make it this far, set the flag.
        success = True

    except Exception, E:
        logging.error(E)
        if (os.path.exists(outFile)):
            pass
        
    finally: 
        try:
            cH5.close()
            del cH5
            if success:
                try:
                    ## XXX: This we want to refactor
                    from pbcore.io.cmph5 import factory

                    cmpH5 = factory.create(outFile, 'a')
                    cmpH5.log('CmpH5Sort.py',  __VERSION__, str(datetime.datetime.now()), ' '.join([_inFile, outFile]), 'Sorting')
                    cmpH5.close()
                except Exception, E:
                    logging.warn("Unable to add information to cmpH5 FileInfo table.")
                    logging.warn(E)
                
                if fout:
                    logging.info("Overwriting input cmpH5 file.")
                    shutil.copyfile(_inFile, inFile)
                    fout.close()
        except:
            pass
        finally:
            return(success)

    

