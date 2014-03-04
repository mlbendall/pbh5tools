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

import os
import logging

import h5py as H5
import numpy as NP

from pbh5tools.PBH5ToolsException import PBH5ToolsException
from pbh5tools.CmpH5Format import CmpH5Format
from pbh5tools.CmpH5Utils import copyAttributes, deleteAttrIfExists

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
    def w(i, nm):
        if any([z[i] is None for z in umovies]):
            logging.info("No dataset: %s" % nm)
        else:
            # take dtype from previous dataset.
            outCmp.create_dataset(nm, data = NP.array([z[i] for z in umovies]),
                                  dtype = inCmps[0][nm].dtype)
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
    w(0, fmt.MOVIE_INFO_ID)
    w(1, fmt.MOVIE_INFO_NAME)
    w(2, fmt.MOVIE_INFO_FRAME_RATE)
    w(3, fmt.MOVIE_INFO_RUN)
    w(4, fmt.MOVIE_INFO_EXP)

    return umovies

def makeOrAppend(outCmp, dsName, newDta, chunks = True):
    if not dsName in outCmp:
        outCmp.create_dataset(dsName, data = newDta, chunks = chunks,
                              maxshape = tuple([None for x in newDta.shape]))
    else:
        d = outCmp[dsName]
        e = d.shape[0]
        if len(d.shape) == 2:
            d.resize((e + newDta.shape[0], d.shape[1]))
            d[e:(e + newDta.shape[0]), ] = newDta
        else:
            d.resize((e + newDta.shape[0],))
            d[e:(e + newDta.shape[0])] = newDta


def _fileExists(fileName):
    if os.path.isfile(fileName):
        return os.path.abspath(fileName)
    else:
        raise IOError("Unable to find {f}".format(f=fileName))


def cmpH5Merge(inFiles, outFile):

    # input validation. This is kinda clunky
    inps = {_fileExists(f) for f in inFiles}

    # Not sure if this is the expected behavior
    if os.path.isabs(outFile):
        outp = outFile
    else:
        outp = os.path.join(os.getcwd(), outFile)

    if outp in inps:
        raise ValueError("Outfile {f} was provided as an input file.".format(f=outp))

    # start the analysis
    try:
        logging.debug("Processing:\n\t" + "\t\n".join(inFiles))
        logging.debug("Writing to:" + str(outFile))

        inCmps = [H5.File(z, 'r') for z in inFiles]
        outCmp = H5.File(outFile, 'w')

        logging.debug("Loaded input and output h5 files.")

        if not allEqual([CmpH5Format(z).VERSION for z in inCmps]):
            raise PBH5ToolsException("merge", "Different cmp.h5 versions.")

        fmt = CmpH5Format(inCmps[0])

        if not allEqual([z[fmt.REF_INFO]['MD5'].value for z in inCmps]):
            raise PBH5ToolsException("merge", "Different reference sequences.")

        # Remove cmp.h5 files which have no alignment
        inNonEmptyCmps = []
        for f in inCmps:
            alnNum = 0
            try:
                alnNum = f['/AlnInfo/AlnIndex'].shape[0]
                if alnNum > 0:
                    inNonEmptyCmps.append(f)
                else:
                    logging.warn("Skipping emtpy file: %s" % f.filename)
            except Exception:
                logging.warn("Skipping emtpy file: %s" % f.filename)

        inCmps = inNonEmptyCmps

        if not len(inCmps):
            raise PBH5ToolsException("merge", "No non-empty files to merge.")

        # check for consistency of things like barcode and edna/z score
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
            raise PBH5ToolsException("merge", "No non-empty files to merge.")

        # copy REF_INFO, FILE_LOG, and BARCODE_INFO if its there.
        outCmp.copy(inCmps[0][fmt.REF_INFO], fmt.REF_INFO)
        outCmp.copy(inCmps[0][fmt.FILE_LOG], fmt.FILE_LOG)

        if hasBarcode:
            outCmp.copy(inCmps[0][fmt.BARCODE_INFO], fmt.BARCODE_INFO)

        # top-level attributes.
        copyAttributes(inCmps[0], outCmp)
        deleteAttrIfExists(outCmp, fmt.INDEX_ATTR)

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
                    raise PBH5ToolsException("merge", "Error processing movies.")

            for rID in refInfoIDs:
                if rID not in refIDMap.values():
                    logging.info("Skipping reference with no reads.")
                    continue

                # compute new reference ID.
                aIdx    = cmpH5[fmt.ALN_INDEX].value
                refID   = {x:y for y,x in refIDMap.iteritems()}[rID]
                refName = makeRefName(rID)

                # which reads go to this reference.
                whichReads = aIdx[:,fmt.REF_ID] == refID
                if not any(whichReads):
                    # this should be covered by the test at the top,
                    # but it is not really perfectly defined by the
                    # spec as to whether something in the ref group
                    # *has* to have alignments.
                    continue
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
                             NP.array([nid for nid,a,b in newAlnGroup],
                                      dtype = cmpH5[fmt.ALN_GROUP_ID].dtype))
                makeOrAppend(outCmp, fmt.ALN_GROUP_PATH,
                             NP.array([npth for a,npth,b in newAlnGroup],
                                      dtype = cmpH5[fmt.ALN_GROUP_PATH].dtype))

        # now depending on what references had alignments we'll make the
        # new REF_GROUP.
        uRefsWithAlignments = NP.unique(outCmp[fmt.ALN_INDEX][:,fmt.REF_ID])
        outCmp.create_dataset(fmt.REF_GROUP_ID, data = uRefsWithAlignments,
                              dtype = inCmps[0][fmt.REF_GROUP_ID].dtype)
        outCmp.create_dataset(fmt.REF_GROUP_PATH,
                              data = NP.array([('/' + makeRefName(z)) for z in
                                               uRefsWithAlignments]),
                              dtype = inCmps[0][fmt.REF_GROUP_PATH].dtype)
        outCmp.create_dataset(fmt.REF_GROUP_INFO_ID, data = uRefsWithAlignments,
                              dtype = inCmps[0][fmt.REF_GROUP_INFO_ID].dtype)

        # reset the IDs
        outCmp[fmt.ALN_INDEX][:,fmt.ID] = range(1, outCmp[fmt.ALN_INDEX].shape[0] + 1)
        # reset the molecule IDs
        outCmp[fmt.ALN_INDEX][:,fmt.MOLECULE_ID] = \
            ((NP.max(outCmp[fmt.ALN_INDEX][:,fmt.MOLECULE_ID]) *
              (outCmp[fmt.ALN_INDEX][:,fmt.MOVIE_ID] - 1)) +
             outCmp[fmt.ALN_INDEX][:,fmt.HOLE_NUMBER] + 1)

        # close the sucker.
        outCmp.close()

    except Exception, e:
        try:
            # remove the file as it won't be correct
            if os.path.exists(outFile):
                os.remove(outFile)
        except:
            pass
        raise
