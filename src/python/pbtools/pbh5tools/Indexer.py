import ctypes
import os
import numpy
import pkg_resources

class Indexer(object):
    def __init__(self):
        self.SW_DLL_PATH = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "ci.so" 
        self._dll        = ctypes.CDLL(self.SW_DLL_PATH)
        
        self._dll.compute_indices.argtypes = [numpy.ctypeslib.ndpointer(dtype = numpy.intc), 
                                              numpy.ctypeslib.ndpointer(dtype = numpy.intc),
                                              numpy.ctypeslib.ndpointer(dtype = numpy.intc),
                                              numpy.ctypeslib.ndpointer(dtype = numpy.intc),
                                              ctypes.c_int]

        self._dll.left_bin_search.argtypes = [ctypes.c_int, numpy.ctypeslib.ndpointer(dtype = numpy.intc), ctypes.c_int]
        self._dll.right_bin_search.argtypes = [ctypes.c_int, numpy.ctypeslib.ndpointer(dtype = numpy.intc), ctypes.c_int]
        self._dll.number_within_range.argtypes = [numpy.ctypeslib.ndpointer(dtype = numpy.intc), 
                                                  ctypes.c_int, ctypes.c_int, ctypes.c_int]
        
    def compute(self, tStart, tEnd):
        # XXX : this needs work.
        tS = numpy.asarray(tStart, dtype = numpy.intc)
        tE = numpy.asarray(tEnd, dtype = numpy.intc)
        results = numpy.zeros(2 * len(tS), dtype = numpy.intc)
        sortedEnds = numpy.asarray(numpy.sort(tE) - 1, dtype = numpy.intc) 

        self._dll.compute_indices(tS, tE, sortedEnds, results, len(tS))
        return results.reshape((len(tS), 2))

    
    def nwithin(self, vec, s, e):
        return self._dll.number_within_range(numpy.asarray(vec, dtype = numpy.intc), s, e, len(vec))
