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
