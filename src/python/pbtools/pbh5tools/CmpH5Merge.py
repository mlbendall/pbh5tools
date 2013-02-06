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
from pbtools.pbh5tools.CmpH5Utils import *

def makeRefName(rID):
    return "ref%06d" % rID

def allEqual(v):
    def f(e):
        return e.all() if type(e) == NP.ndarray else e
    return all(f(v[0] == a) for a in v)

def empty(cmpH5):
    return cmpH5[CmpH5Format(cmpH5).ALN_INDEX].shape[0] <= 0

def processMovies(outCmp, inCmps, fmt):
    umovies = [] 
    newMovieID = 1

    def l(i, nm):
        return cmpH5[nm][i] if nm in cmpH5 else None
    def w(i, nm, dtype):
        if any([z[i] == None for z in umovies]):
            logging.info("No dataset: %s" % nm)
        else:
            outCmp.create_dataset(nm, data = NP.array([z[i] for z in umovies], 
                                                      dtype = dtype))
    for cmpH5 in inCmps:
        for i,n in enumerate(cmpH5[fmt.MOVIE_INFO_NAME]):
            if not n in [u[1] for u in umovies]:
                umovies.append((newMovieID, 
                                l(i, fmt.MOVIE_INFO_NAME),
                                l(i, fmt.MOVIE_INFO_FRAME_RATE),
                                l(i, fmt.MOVIE_INFO_RUN),
                                l(i, fmt.MOVIE_INFO_EXP)))
                newMovieID += 1
    # write the information to the new file.
    w(0, fmt.MOVIE_INFO_ID, int)
    w(1, fmt.MOVIE_INFO_NAME, H5.special_dtype(vlen = str))
    w(2, fmt.MOVIE_INFO_FRAME_RATE, int)
    w(3, fmt.MOVIE_INFO_RUN, int)
    w(4, fmt.MOVIE_INFO_EXP, int)
   
    return umovies

def makeOrAppend(outCmp, dsName, newDta, chunks = True):
    if not dsName in outCmp:
        outCmp.create_dataset(dsName, data = newDta, chunks = chunks)
    else:
        d = outCmp[dsName]
        e = d.shape[0]
        if len(d.shape) == 2:
            d.resize((e + newDta.shape[0], d.shape[1]))
            d[e:(e + newDta.shape[0]), ] = newDta
        else:
            d.resize((e + newDta.shape[0],))
            d[e:(e + newDta.shape[0])] = newDta

def cmpH5Merge(inFiles, outFile):
    try:
        inCmps = [H5.File(z, 'r') for z in inFiles]
        outCmp = H5.File(outFile, 'w') # fail if it exists.
        
        logging.debug("Loaded input and output h5 files.")
        
        if not allEqual([CmpH5Format(z).VERSION for z in inCmps]):
            raise PBH5ToolsException("Different cmp.h5 versions.")
    
        fmt = CmpH5Format(inCmps[0])
    
        if not allEqual([z[fmt.REF_INFO]['MD5'].value for z in inCmps]):
            raise PBH5ToolsException("Different reference sequences.")
    
        # check for consisteny of things like barcode and edna/z score
        # datasets.
        hasBarcode = all([ fmt.BARCODE_INFO in z for z in inCmps ])
        extraDatasets = [set(filter(lambda x : not x == fmt.ALN_INDEX_NAME, 
                                    z[fmt.ALN_INFO].keys())) for z in inCmps ]
        extraDatasets = reduce(set.intersection, extraDatasets)
               
        def filterPrint(x):
            if empty(x):
                logging.warn("Skipping emtpy file: %s" % x.filename)
                return False
            else:
                return True
        inCmps = filter(filterPrint, inCmps)
        
        if not len(inCmps):
            raise PBH5ToolsException("No non-empty files to merge.")

        # copy REF_INFO, FILE_LOG, and BARCODE_INFO if its there.
        outCmp.copy(inCmps[0][fmt.REF_INFO], fmt.REF_INFO)
        outCmp.copy(inCmps[0][fmt.FILE_LOG], fmt.FILE_LOG)

        if hasBarcode: 
            outCmp.copy(inCmps[0][fmt.BARCODE_INFO], fmt.BARCODE_INFO)
        
        # top-level attributes.
        copyAttributes(inCmps[0], outCmp)

        # go through by REF_INFO_ID and select the relevant bits from each file. 
        refInfoIDs = outCmp[fmt.REF_INFO]['ID'].value
        
        # process the movies upfront.
        umovies = processMovies(outCmp, inCmps, fmt)
  
        # an increment for new ALN_GROUP/ID values
        alnIDBegin = 1

        # either way you structure the loops annoyances arise.
        for cmpH5 in inCmps:
            logging.debug("Processing: %s" % cmpH5.filename)
              
            # we are going to map the ref ids into the globaly unique
            # refInfoIDs.
            refIDMap = dict(zip(cmpH5[fmt.REF_GROUP_ID].value,
                                cmpH5[fmt.REF_GROUP_INFO_ID].value))

            # make a map from this cmpH5's movies to the new movie ID.
            movieMap = {}
            for oid,nm in zip(cmpH5[fmt.MOVIE_INFO_ID], cmpH5[fmt.MOVIE_INFO_NAME]):
                newID = [z[0] for z in umovies if z[1] == nm]
                if len(newID) == 1:
                    movieMap[oid] = newID[0]
                else:
                    raise PBH5Exception("Error processing movies.")
        
            for rID in refInfoIDs:
                if not rID in refIDMap.values():
                    logging.info("Skipping reference with no reads.")
                    continue
                
                # set the new reference ID.
                aIdx    = cmpH5[fmt.ALN_INDEX].value
                refID   = {x:y for y,x in refIDMap.iteritems()}[rID]
                refName = makeRefName(rID)

                if not sum(aIdx[:,fmt.REF_ID] == refID):
                    logging.info("No reads mapped to reference: %d for %s" % 
                                 (rID, cmpH5.filename))
                    continue

                # which reads go to this reference. 
                whichReads = aIdx[:,fmt.REF_ID] == refID
                aIdx = aIdx[whichReads, ]
                aIdx[:,fmt.REF_ID] = rID

                # make a map between old and new IDs 
                uAlnIDs  = NP.unique(aIdx[:,fmt.ALN_ID])
                alnIDMap = dict(zip(uAlnIDs, NP.array(range(0, len(uAlnIDs))) + 
                                    alnIDBegin))
                alnGroup = {k:v for k,v in zip(cmpH5[fmt.ALN_GROUP_ID].value,
                                               cmpH5[fmt.ALN_GROUP_PATH].value) if \
                                k in uAlnIDs}
                newAlnGroup = [(alnIDMap[k], 
                                "/%s/%s-%d" % (refName, os.path.basename(alnGroup[k]), 
                                               alnIDMap[k]),
                                alnGroup[k]) for k in alnGroup.keys()]

                # Set the new ALN_ID vals in the ALN_INDEX.
                aIdx[:,fmt.ALN_ID] = NP.array([alnIDMap[aIdx[i,fmt.ALN_ID]] for i in 
                                               range(0, aIdx.shape[0])])
                # Set the new MOVIE_ID vals. 
                aIdx[:,fmt.MOVIE_ID] = NP.array([movieMap[aIdx[i,fmt.MOVIE_ID]] for i in
                                                 range(0, aIdx.shape[0])])
            
                # copy the array data.
                for (nid,newGroup,oldGroup) in newAlnGroup:
                    logging.debug("Copying: \nfrom: %s \ninto: %s" % \
                                      (oldGroup, newGroup))
                    if not os.path.dirname(newGroup) in outCmp:
                        outCmp.create_group(refName)
                    outCmp.copy(cmpH5[oldGroup], outCmp[refName], 
                                name = os.path.basename(newGroup))
            
                # increment the ALN_GROUP id offset.
                alnIDBegin = alnIDBegin + len(uAlnIDs)

                # write the adjusted alignment information.
                makeOrAppend(outCmp, fmt.ALN_INDEX, aIdx)

                # write extra datasets in the ALN_INFO group 
                for extra in extraDatasets:
                    pth = '/'.join([fmt.ALN_INFO, extra])
                    logging.info("Processing extra dataset: %s" % pth)
                    makeOrAppend(outCmp, pth, cmpH5[pth].value[whichReads,])
            
                # write the ALN_GROUP.
                makeOrAppend(outCmp, fmt.ALN_GROUP_ID, 
                             NP.array([nid for nid,a,b in newAlnGroup]))
                makeOrAppend(outCmp, fmt.ALN_GROUP_PATH, 
                             NP.array([npth for a,npth,b in newAlnGroup], 
                                      dtype = H5.special_dtype(vlen = str)))

        # now depending on what references had alignments we'll make the
        # new REF_GROUP.
        uRefsWithAlignments = NP.unique(outCmp[fmt.ALN_INDEX][:,fmt.REF_ID])
        outCmp.create_dataset(fmt.REF_GROUP_ID, data = uRefsWithAlignments)
        outCmp.create_dataset(fmt.REF_GROUP_PATH, 
                              data = NP.array([('/' + makeRefName(z)) for z in uRefsWithAlignments],
                                              dtype = H5.special_dtype(vlen = str)))
        outCmp.create_dataset(fmt.REF_GROUP_INFO_ID, data = uRefsWithAlignments)

        # reset the alignment IDs 
        outCmp[fmt.ALN_INDEX][:,fmt.ALN_ID] = range(1, outCmp[fmt.ALN_INDEX].shape[0] + 1)
        # reset the molecule IDs
        outCmp[fmt.ALN_INDEX][:,fmt.MOLECULE_ID] = \
            ((NP.max(outCmp[fmt.ALN_INDEX][:,fmt.MOLECULE_ID]) * 
              (outCmp[fmt.ALN_INDEX][:,fmt.MOVIE_ID] - 1)) + 
             outCmp[fmt.ALN_INDEX][:,fmt.HOLE_NUMBER] + 1)
        
    
    except Exception, e:
        logging.exception(e)
        try:
            os.remove(outFile)
        except:
            pass 
        raise e  

                

