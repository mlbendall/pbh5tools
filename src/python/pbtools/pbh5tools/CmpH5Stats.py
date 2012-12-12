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

class Csv(object):
    def __init__(self, **args):
        self.cols = args
    def __iter__(self):
        for a in self.cols:
            yield (a, self.cols[a])

def hasEval(thing):
    ## duck typing
    return 'eval' in dir(thing)

def procMe(thing):
    if hasEval(thing):
        return lambda cmpH5, idx : thing.eval(cmpH5, idx)
    else:
        return lambda cmpH5, idx : thing

class Expr(object):
    def eval(self, cmpH5, idx):
        pass

    def __add__(self, other):
        return BinOp(self, other, '+')
    def __div__(self, other):
        return BinOp(self, other, '/')
    def __sub__(self, other):
        return BinOp(self, other, '-')
    def __mul__(self, other):
        return BinOp(self, other, '*')

    def __radd__(self, other):
        return BinOp(other, self, "+")
    def __rdiv__(self, other):
        return BinOp(other, self, "/")
    def __rsub__(self, other):
        return BinOp(other, self, "-")
    def __rmul__(self, other):
        return BinOp(other, self, "*")
    
class BinOp(Expr):
    def __init__(self, l, r, op):
        self.l  = procMe(l)
        self.r  = procMe(r)
        self.op = op

    def eval(self, cmpH5, idx):
        if self.op == '+':
            return self.l(cmpH5, idx) + self.r(cmpH5, idx)
        elif self.op == '-':
            return self.l(cmpH5, idx) - self.r(cmpH5, idx)
        elif self.op == '/':
            return self.l(cmpH5, idx) / self.r(cmpH5, idx)
        elif self.op == '*':
            return self.l(cmpH5, idx) * self.r(cmpH5, idx)
        else:
            raise Exception("Undefined operation:" + self.op)

class Flatten(Expr):
    def __init__(self, expr):
        self.expr = expr

    def eval(self, cmpH5, idx):
        r = self.expr.eval(cmpH5, idx)
        if isinstance(r, (list, tuple)):
            return np.concatenate(r)
        else:
            return r

class Statistic(Expr):
    def __init__(self, metric):
        self.metric = metric

    def eval(self, cmpH5, idx):
        r = self.metric.eval(cmpH5, idx)
        if isinstance(r, (list, tuple)):
            return np.array([self.f(rr) for rr in r])
        else:
            return self.f(r)

class Mean(Statistic):
    def f(self, x): 
        return np.mean(x)

class Median(Statistic):
    def f(self, x):
        return np.median(x)

class Q(Statistic):
    def __init__(self, metric, qtile = 95.0):
        super(Q, self).__init__(metric)
        self.qtile = qtile

    def f(self, x):
        return np.percentile(x, self.qtile)

class Metric(Expr):
    def __init__(self):
        self.r = None

    def eval(self, cmpH5, idx):
        return self.produce(cmpH5, idx)
        # if None == self.r:
        #     self.r = 
        # return self.r 

class _TemplateSpan(Metric):
    def produce(self, cmpH5, idx):
        return (cmpH5.tEnd[idx] - cmpH5.tStart[idx])

class _ReadLength(Metric):
    def produce(self, cmpH5, idx):
        return (cmpH5.rEnd[idx] - cmpH5.rStart[idx])

class _NErrors(Metric):
    def produce(self, cmpH5, idx):
        return (cmpH5.nMM[idx] + cmpH5.nIns[idx] + cmpH5.nDel[idx])

class _ReadDuration(Metric):
    def produce(self, cmpH5, idx):
        return np.array([ sum(cmpH5[i].IPD() + cmpH5[i].PulseWidth()) 
                          for i in idx ])
class _FrameRate(Metric):
    def produce(self, cmpH5, idx):
        return np.array([ cmpH5[i].movieInfo.FrameRate for i in idx ])

class _IPD(Metric):
    def produce(self, cmpH5, idx):
        return [ cmpH5[i].IPD() for i in idx ]

class _PulseWidth(Metric):
    def produce(self, cmpH5, idx):
        return [ cmpH5[i].PulseWidth() for i in idx ] 

################################################################################
##
## Define the core metrics, try to define all metrics in terms of some
## basic metrics.
##
################################################################################
ReadLength          = _ReadLength()
TemplateSpan        = _TemplateSpan()
NErrors             = _NErrors()    
ReadFrames          = _ReadDuration() * 1.0
FrameRate           = _FrameRate()
IPD                 = _IPD()
PulseWidth          = _PulseWidth()
Accuracy            = 1.0 - NErrors/(ReadLength * 1.0)
PolRate             = TemplateSpan/(ReadFrames/(FrameRate * 1.0))
ReadLength          = ReadLength


class CmpH5Stats(object):
    def __init__(self, cmpH5Filename, groupBy = None):
        self.groupBy = groupBy
        self.reader  = CmpH5Reader(cmpH5Filename)
        self.csv     = Csv(mean_accuracy   = Mean(Accuracy), 
                           meanReadLength  = Mean(ReadLength),
                           medianPolRate   = Median(PolRate),
                           meanPolRate     = Mean(PolRate),
                           meanIPD         = Mean(Flatten(IPD)),
                           medianIPD       = Median(Flatten(IPD)))
        
        ## make a hash where each element contains indices of the
        ## subreads for the strata.
        if self.groupBy == 'movie':
            movieNames  = [self.reader.movieInfo(id)[1] for id in self.reader.MovieID]
            uMovieNames = set(movieNames)
            self.idxs = dict([(elt, np.where([ elt == m for m in mn ])[0]) 
                              for elt in uMovieNames])
        else:
            self.idxs = {"" : np.arange(0, 100)}

        
    def processIdxSet(self, idx):
        for e in self.csv:
            print e[0]
            print e[1].eval(self.reader, idx)
        
    
    def emitToCsv(self, dta):
        from IPython.Shell import IPShellEmbed; IPShellEmbed(argv=[])()
        pass

    def run(self):
        self.emitToCsv({ key : self.processIdxSet(self.idxs[key]) for key in 
                         self.idxs.keys() })
