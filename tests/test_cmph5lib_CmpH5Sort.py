from nose.tools import assert_equal
from nose import SkipTest

import bisect
import h5py as h
from numpy import *

from pbcore import data
import pbh5tools.CmpH5Sort as CS
import pbcore.io.rangeQueries as RQ
from pbcore.io import CmpH5Reader

def brute_force_number_in_range(s, e, vec):
    return(len(filter(lambda x : s <= x < e, vec)))

def generate_positions(size, coverage, lScale = 50):
    NN = size*coverage
    tS = random.randint(0, size, NN)
    tE = tS + array(map(int, random.exponential(lScale, NN) + 1))
    ar = array([tS, tE]).transpose()
    ar = ar[lexsort((tE, tS)),]
    return(ar)

def brute_force_search(tStart, tEnd, nBack, nOverlap, start, end):
    toKeep = array([False]*len(tStart))
    res = array(range(0, len(tStart)))

    for i in range(0, len(tStart)):
        # four cases to deal with.
        if (tStart[i] >= start and tStart[i] <= end):
            toKeep[i] = True
        elif (tEnd[i] > start and tEnd[i] <= end):
            toKeep[i] = True
        elif (tStart[i] <= start and tEnd[i] >= end):
            toKeep[i] = True
        elif (tStart[i] >= start and tEnd[i] <= end):
            toKeep[i] = True
        else:
            continue
    return(res[toKeep])

def brute_force_get_reads(aIdx, start, end, format):
    if aIdx.shape[0] == 0:
        return aIdx
    idxs = self.__brute_force_search(aIdx[:,format.TARGET_START],
                                     aIdx[:,format.TARGET_END],
                                     aIdx[:,format.N_BACK],
                                     aIdx[:,format.N_OVERLAP],
                                     start, end)
    return(aIdx[idxs,])

def compare_implementations(size, coverage = 1):
    NN = size * coverage
    ar = generate_positions(size, coverage)
    res = CS.computeIndices(ar[:,0], ar[:,1])
    resDP = CS.computeIndicesDP(ar[:,0], ar[:,1])
    assert(sum(res[:,0:2] == resDP[:,0:2]) == NN*2)

class TestCmpH5Format:
    def test___init__(self):
        cmpH5_format = CS.CmpH5Format(h.File(data.getCmpH5(),"r"))
        assert_equal(cmpH5_format.ALN_INFO, 'AlnInfo')

class TestNumberWithinRange:
    def test_number_within_range(self):
        for j in range(0, 100):
            a = sort(random.randint(0, 100, 100))
            s,e = sort(random.randint(0, 100, 2))
            assert_equal(CS.numberWithinRange(s,e,a), 
                         brute_force_number_in_range(s,e,a))
       
class TestComputeIndices:
    def test_compute_indices(self):
        for i in [100, 200]:
            for j in [1, 5]:
                compare_implementations(i, j)

class TestComputeIndicesDP:
    def test_compute_indices_d_p(self):
        for i in [100, 200]:
            for j in [1, 5]:
                compare_implementations(i, j)

class TestComputeRefIndexTable:
    def test_compute_ref_index_table(self):
        refIDs = [5,1,1,1,1,1,1,1,1,1,2,2,2,2,2]
        tbl    = CS.computeRefIndexTable(array(refIDs))
        utbl   = [ 5, 0, 1,
                   1, 1, 10,
                   2, 10, 15 ]
        assert_equal(sum(tbl.ravel() == utbl), len(utbl))

class TestGetOverlappingRanges:
    def test_get_overlapping_ranges(self):
        for i in [100, 500]:
            for j in [.1, 1, 5, 10]:
                for k in range(0, 10):
                    ar = generate_positions(i, j)
                    idx = CS.computeIndicesDP(ar[:,0], ar[:,1])
                    aArray = hstack((ar, idx))
                    s = random.randint(0, i, 1)
                    e = int(1 + random.exponential(30, 1))
                    x = RQ.getOverlappingRanges(aArray[:,0], aArray[:,1], 
                                                aArray[:,2], aArray[:,3], s, 
                                                s + e + 1)
                    y = brute_force_search(aArray[:,0], aArray[:,1], aArray[:,2], 
                                           aArray[:,3], s, s + e)
                    assert(all(sort(x) == sort(y)))


class TestGetReadsInRange:
    def __init__(self):
        self.h5FileName = data.getCmpH5()
        self.cmpH5 = CmpH5Reader(self.h5FileName)
        
    def test_get_reads_in_range(self):
        for j in range(0, 100):
            a = sort(random.randint(0, 100, 100))
            s,e = sort(random.randint(0, 100, 2))
            assert_equal(CS.numberWithinRange(s,e,a),  brute_force_number_in_range(s,e,a))
       

