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
import numpy as NP

from pbcore.io import CmpH5Reader

from pbtools.pbh5tools.PBH5ToolsException import PBH5ToolsException

def hasEval(thing):
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
        return BinOp(other, self, '+')
    def __rdiv__(self, other):
        return BinOp(other, self, '/')
    def __rsub__(self, other):
        return BinOp(other, self, '-')
    def __rmul__(self, other):
        return BinOp(other, self, '*')
    def __eq__(self, other):
        return BinOp(self, other, '=')
    def __ne__(self, other):
        return BinOp(self, other, '!=')
    def __lt__(self, other):
        return BinOp(self, other, '<')
    def __le__(self, other):
        return BinOp(self, other, '<=')
    def __gt__(self, other):
        return BinOp(self, other, '>')
    def __ge__(self, other):
        return BinOp(self, other, '>=')

    def __and__(self, other):
        return BinOp(self, other, '&')
    def __or__(self, other):
        return BinOp(self, other, '|')

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
        elif self.op == '=':
            return self.l(cmpH5, idx) == self.r(cmpH5, idx)
        elif self.op == '!=':
            return self.l(cmpH5, idx) != self.r(cmpH5, idx)
        elif self.op == '<':
            return self.l(cmpH5, idx) < self.r(cmpH5, idx)
        elif self.op == '<=':
            return self.l(cmpH5, idx) <= self.r(cmpH5, idx)
        elif self.op == '>':
            return self.l(cmpH5, idx) > self.r(cmpH5, idx)
        elif self.op == '>=':
            return self.l(cmpH5, idx) >= self.r(cmpH5, idx)
        elif self.op == '|':
            return self.l(cmpH5, idx) | self.r(cmpH5, idx)
        elif self.op == '&':
            return self.l(cmpH5, idx) & self.r(cmpH5, idx)
        elif self.op == ':':
            return [(str(x) + ":" + str(y)) for x,y in zip(self.l(cmpH5, idx), 
                                                           self.r(cmpH5, idx))]
        else:
            raise Exception("Undefined operation:" + self.op)

class Flatten(Expr):
    def __init__(self, expr):
        self.expr = expr

    def eval(self, cmpH5, idx):
        r = self.expr.eval(cmpH5, idx)
        if isinstance(r, (list, tuple)):
            return NP.concatenate(r)
        else:
            return r

class Statistic(Expr):
    def __init__(self, metric):
        self.metric = metric

    def eval(self, cmpH5, idx):
        r = self.metric.eval(cmpH5, idx)
        if isinstance(r, (list, tuple)):
            return NP.array([self.f(rr) for rr in r])
        else:
            return self.f(r)

class Metric(Expr):
    def __init__(self):
        self.r = None
    def eval(self, cmpH5, idx):
        return self.produce(cmpH5, idx)

class Factor(Metric):
    def __rmul__(self, other):
        return BinOp(other, self, ':')
    def __mul__(self, other):
        return BinOp(self, other, ':')

class Tbl(object):
    """The Tbl object provides a grouping construct for columns."""
    def __init__(self, **args):
        self.cols = args
    def __iter__(self):
        for a in self.cols:
            yield (a, self.cols[a])
    def eval(self, cmpH5, idx):
        return [(a, self.cols[a].eval(cmpH5, idx)) for a in self.cols.keys()]


def split(x, f):
    # I'm thinking it is faster to do the allocation of the NP array
    # rather than the appends.
    assert(len(x) == len(f))
    levels  = NP.unique(f)
    counts  = {k:0 for k in levels} 
    for i in xrange(0, len(x)):
        counts[f[i]] += 1
    results = { k:NP.zeros(v, dtype = int) for k,v in counts.items() }
    for i in xrange(0, len(x)):
        k = f[i]
        results[k][counts[k] - 1] = x[i]
        counts[k] -= 1
    return results


def toRecArray(res):
    recArrays = []
    for k in res.keys():
        elt = res[k]
        nameAndType = [(n[0], n[1].dtype) for n in elt]
        dta = [n[1] for n in elt]
        if isinstance(k, str):
            if isinstance(dta[0], NP.ndarray): 
                groupNames = NP.array([k] * len(dta[0]))
            else:
                groupNames = k
            nameAndType.insert(0, ('Group', object))
            dta.insert(0, groupNames)
        recArrays.append(NP.rec.array(dta, dtype = nameAndType))
    return NP.hstack(recArrays)

# Stats 
class Mean(Statistic):
    def f(self, x): 
        return NP.mean(x[~NP.isnan(x)])

class Median(Statistic):
    def f(self, x):
        return NP.median(x[~NP.isnan(x)])

class Count(Statistic):
    def f(self, x):
        return NP.array([len(x)])

class Q(Statistic):
    def __init__(self, metric, qtile = 95.0):
        super(Q, self).__init__(metric)
        self.qtile = qtile

    def f(self, x):
        return NP.percentile(x[~NP.isnan(x)], self.qtile)

# Metrics
class DefaultWhere(Metric):
    def produce(self, cmpH5, idx):
        return NP.ones(len(idx), dtype = bool)

class DefaultGroupBy(Metric):
    def produce(self, cmpH5, idx):
        return NP.ones(len(idx), dtype = bool)

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
        return NP.array([ sum(cmpH5[i].IPD() + cmpH5[i].PulseWidth()) 
                          for i in idx ])
class _FrameRate(Metric):
    def produce(self, cmpH5, idx):
        return NP.array([ cmpH5[i].movieInfo.FrameRate for i in idx ])

class _IPD(Metric):
    def produce(self, cmpH5, idx):
        return [ cmpH5[i].IPD() for i in idx ]

class _PulseWidth(Metric):
    def produce(self, cmpH5, idx):
        return [ cmpH5[i].PulseWidth() for i in idx ] 
    
class _Movie(Factor):
    def produce(self, cmpH5, idx):
        return NP.array([cmpH5[i].movieInfo['Name'] for i in idx])

class _Reference(Factor):
    def produce(self, cmpH5, idx):
        return NP.array([cmpH5[i].referenceInfo['FullName'] for i in idx])

class _RefIdentifier(Factor):
    def produce(self, cmpH5, idx):
        return NP.array([cmpH5[i].referenceInfo['Name'] for i in idx])

class _HoleNumber(Factor):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['HoleNumber'][idx]

class _ReadStart(Metric):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['rStart'][idx]

class _ReadEnd(Metric):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['rEnd'][idx]

class _TemplateStart(Metric):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['tStart'][idx]

class _TemplateEnd(Metric):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['tEnd'][idx]

class _MoleculeIdx(Factor):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['MoleculeID'][idx]

class _Strand(Factor):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['RCRefStrand'][idx]

class _AlignmentIdx(Factor):
    def produce(self, cmpH5, idx):
        return idx

class _Barcode(Factor):
    def produce(self, cmpH5, idx):
        return NP.array([ cmpH5[i].barcode for i in idx ])

###############################################################################
##
## Define the core metrics, try to define all metrics in terms of some
## basic metrics.
##
###############################################################################
ReadLength          = _ReadLength()
TemplateSpan        = _TemplateSpan()
NErrors             = _NErrors()    
ReadFrames          = _ReadDuration() * 1.0
FrameRate           = _FrameRate()
IPD                 = _IPD()
PulseWidth          = _PulseWidth()
Accuracy            = 1.0 - NErrors/(ReadLength * 1.0)
PolRate             = TemplateSpan/(ReadFrames/(FrameRate * 1.0))
Movie               = _Movie()
DefaultWhat         = (ReadLength, Accuracy)
Reference           = _Reference()
RefIdentifier       = _RefIdentifier()
HoleNumber          = _HoleNumber()
AlignmentIdx        = _AlignmentIdx()
Strand              = _Strand()
MoleculeIdx         = _MoleculeIdx()
TemplateEnd         = _TemplateEnd()
TemplateStart       = _TemplateStart()
ReadEnd             = _ReadEnd()
ReadStart           = _ReadStart()
Barcode             = _Barcode()


def query(reader, what = DefaultWhat, where = DefaultWhere(), 
          groupBy = DefaultGroupBy()):
    idxs = NP.where(where.eval(reader, range(0, len(reader))))[0]
    groupBy = groupBy.eval(reader, idxs)
    return { k:what.eval(reader, v) for k,v in 
             split(idxs, groupBy).items() }
