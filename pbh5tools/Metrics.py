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

import sys
import os
import h5py
import numpy as NP
import inspect
import re

from pbcore.io import CmpH5Reader
from pbh5tools.PBH5ToolsException import PBH5ToolsException

NOTINCSV_LABEL = 'NotInCsv'

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
    def __init__(self, ll, rr, op):
        self.ll = ll
        self.rr = rr
        self.l  = procMe(ll)
        self.r  = procMe(rr)
        self.op = op

    def __str__(self):
        return str(self.ll) + str(self.op) + str(self.rr)

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

def processClass(cls, name, bases, dct):
    ignoreRes = ['^Default', '^Metric$', '^Statistic$', '^Factor$',
                 '^FactorStatistic']

    if not any(map(lambda x : re.match(x, name), ignoreRes)):
        if '__init__' in dct:
            # if it has an init it takes arguments which define the
            # metric.
            f = dct['__init__']
            a = inspect.getargspec(f)
            if len(a.args) > 1:
                argspec = '[' + ", ".join(a.args[1:]) + ']'
            else:
                argspec = ''
            myName  = name
        else:
            myName  = re.sub('^_', '', name)
            argspec = ''

        if '__doc__' in dct:
            docstr = dct['__doc__']
        else:
            docstr = ''

        return myName + argspec + ('\n\t' + docstr if
                                   docstr else docstr)
    else:
        return None


class DocumentedMetric(type):
    Metrics = []
    def __new__(cls, name, bases, dct):
        DocumentedMetric.Metrics.append(processClass(cls, name,
                                                     bases, dct))
        return type.__new__(cls, name, bases, dct)

    @staticmethod
    def list():
        return filter(lambda x : x, DocumentedMetric.Metrics)

class DocumentedStatistic(type):
    Statistics = []
    def __new__(cls, name, bases, dct):
        DocumentedStatistic.Statistics.append(processClass(cls, name,
                                                           bases, dct))
        return type.__new__(cls, name, bases, dct)

    @staticmethod
    def list():
        return filter(lambda x : x, DocumentedStatistic.Statistics)

class Statistic(Expr):
    __metaclass__ = DocumentedStatistic
    def __init__(self, metric):
        self.metric = metric

    def eval(self, cmpH5, idx):
        r = self.metric.eval(cmpH5, idx)
        if isinstance(r, (list, tuple)):
            return NP.array([self.f(rr) for rr in r])
        else:
            e = self.f(r)
            return e if isinstance(e, NP.ndarray) else NP.array([e])

    def __str__(self):
        return self.__class__.__name__ + '(' + str(self.metric) + ')'

class Metric(Expr):
    __metaclass__ = DocumentedMetric

    def eval(self, cmpH5, idx):
        return self.produce(cmpH5, idx)

    def __str__(self):
        return re.sub('^_', '', self.__class__.__name__)


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
    # reverse it.
    return { k:v[::-1] for k,v in results.items() }


def toRecArray(res):
    ## XXX : this ain't beautiful.
    def myDtype(x):
        if 'dtype' in dir(x):
            return x.dtype
        else:
            return type(x)
    def myLen(x):
        if isinstance(x, NP.ndarray):
            return len(x)
        else:
            return 1

    def expand(groupName, seq):
        return NP.array([groupName]*myLen(seq))

    def convertToRecArray(elt, groupName = None):
        ## recArrays don't like things other than strings for names.
        nat = [(str(n[0]), myDtype(n[1])) for n in elt]
        dta = [n[1] for n in elt]
        if groupName:
            nat.insert(0, ('Group', object))
            dta.insert(0, expand(groupName, dta[0]))

        return NP.rec.array(dta, dtype = nat)

    if DefaultGroupBy.word() in res:
        return convertToRecArray(res[DefaultGroupBy.word()])
    else:
        recArrays = []
        for k in sorted(res.keys()):
            recArrays.append(convertToRecArray(res[k], k))
        return NP.hstack(recArrays)

def groupCsv(csvFile, idxs, reader):
    #csvFile is a csv text file with header. first column used as group name
    #other columns are from 'listMetrics'
    mapValToGrp = {} 
    with open( csvFile ) as ofile:
        header = ofile.readline().rstrip('\r\n')
        #eval header after replacing s/,/* to conform to groupByStr format
        #do this here before walking thru file in case of errors in heading
        groupBy = eval('*'.join(header.split(',')[1:]))
        for line in ofile.readlines():
            columns = line.rstrip('\r\n').split(',')
            mapValToGrp[ ':'.join(columns[1:]) ] = columns[0] 
    return [ mapValToGrp.get(val,NOTINCSV_LABEL) for val in groupBy.eval(reader,idxs) ]
        

# Stats
class Min(Statistic):
    def f(self, x):
        return NP.min(x[~NP.isnan(x)])

class Max(Statistic):
    def f(self, x):
        return NP.max(x[~NP.isnan(x)])

class Sum(Statistic):
    def f(self, x):
        return NP.sum(x[~NP.isnan(x)])

class Mean(Statistic):
    def f(self, x):
        return NP.mean(x[~NP.isnan(x)])

class Median(Statistic):
    def f(self, x):
        return NP.median(x[~NP.isnan(x)])

class Count(Statistic):
    def f(self, x):
        return len(x)

class Percentile(Statistic):
    def __init__(self, metric, ptile = 95.0):
        super(Percentile, self).__init__(metric)
        self.ptile = ptile

    def f(self, x):
        return NP.percentile(x[~NP.isnan(x)], self.ptile)

class Round(Statistic):
    def __init__(self, metric, digits = 0):
        super(Round, self).__init__(metric)
        self.digits = digits
    def f(self, x):
        return NP.around(x, self.digits)


##
## XXX : Not sure that this is correct. This will work, but it begs
## the question whether or not we need some new category, like
## 'Operator' to encompass particular ways of tabulating.
##
## Additionally, FactorStatistics can be computed using a group by -
## it is only the case that you need this in a where where you need
## this new concept.
class ByFactor(Metric):
    __metaclass__ = DocumentedMetric

    def __init__(self, metric, factor, statistic):
        self.metric     = metric
        self.factor     = factor
        self.statistic  = statistic(metric)

    def produce(self, cmpH5, idx):
        r   = self.metric.eval(cmpH5, idx)
        fr  = split(range(len(idx)), self.factor.eval(cmpH5, idx))
        res = NP.zeros(len(idx), dtype = NP.int)
        for v in fr.values():
            res[v] = self.statistic.f(r[v])
        return res

class _MoleculeReadStart(ByFactor):
    def __init__(self):
        super(_MoleculeReadStart, self).__init__(ReadStart, MoleculeName, Min)

class _MinSubreadLength(ByFactor):
    def __init__(self):
        super(_MinSubreadLength, self).__init__(ReadLength, MoleculeName, Min)

class _MaxSubreadLength(ByFactor):
    def __init__(self):
        super(_MaxSubreadLength, self).__init__(ReadLength, MoleculeName, Max)

class _UnrolledReadLength(ByFactor):
    def __init__(self):
        super(_UnrolledReadLength, self).__init__(ReadLength, MoleculeName, Sum)

# Metrics
class _DefaultWhere(Metric):
    def produce(self, cmpH5, idx):
        return NP.ones(len(idx), dtype = bool)
DefaultWhere = _DefaultWhere()

class _DefaultGroupBy(Metric):
    @staticmethod
    def word():
        return 'DefaultGroupBy'

    def produce(self, cmpH5, idx):
        return NP.array([DefaultGroupBy.word()] * len(idx))
DefaultGroupBy = _DefaultGroupBy()


class _TemplateSpan(Metric):
    """The number of template bases covered by the read"""
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
        mtb = cmpH5.movieInfoTable
        mapping = NP.zeros((NP.max([ i.ID for i in mtb]) + 1, ), dtype = object)
        mapping[NP.array([i.ID for i in mtb])] = \
            NP.array([i.Name for i in mtb])
        return mapping[cmpH5.alignmentIndex.MovieID[idx]]

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

class _MoleculeId(Factor):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['MoleculeID'][idx]

class _MoleculeName(Factor):
    def produce(self, cmpH5, idx):
        molecules = zip(cmpH5.alignmentIndex['MovieID'][idx],
                        cmpH5.alignmentIndex['HoleNumber'][idx])
        return NP.array(['%s_%s' % (m,h) for m,h in molecules])

class _Strand(Factor):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex['RCRefStrand'][idx]

class _AlignmentIdx(Factor):
    def produce(self, cmpH5, idx):
        return idx

class _Barcode(Factor):
    def produce(self, cmpH5, idx):
        return NP.array([cmpH5[i].barcodeName for i in idx])
         
class _AverageBarcodeScore(Metric):
    def produce(self, cmpH5, idx):
        bestScore = cmpH5.file[ '/AlnInfo/Barcode' ][idx,2].astype(float)
        nScored   = cmpH5.file[ '/AlnInfo/Barcode' ][idx,0]
        return bestScore / nScored

class _MapQV(Metric):
    def produce(self, cmpH5, idx):
        return cmpH5.alignmentIndex.MapQV[idx]

class _WhiteList(Factor):
    def produce(self, cmpH5, idx):
        return NP.array( [ '%s/%i' % ( cmpH5[i].movieInfo[1], cmpH5[i].HoleNumber ) for i in idx ] )

class SubSample(Metric):
    """boolean vector with true occuring at rate rate or nreads = n"""
    def __init__(self, rate = 1, n = None):
        self.rate = rate
        self.n    = n

    def produce(self, cmpH5, idx):
        if self.n is not None:
            return NP.in1d(idx, NP.floor(NP.random.uniform(0, len(idx), self.n)))
        else:
            return NP.array(NP.random.binomial(1, self.rate, len(idx)), dtype = bool)
            
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
DefaultWhat         = Tbl(readLength = ReadLength, accuracy = Accuracy)
Reference           = _Reference()
RefIdentifier       = _RefIdentifier()
HoleNumber          = _HoleNumber()
AlignmentIdx        = _AlignmentIdx()
Strand              = _Strand()
MoleculeId          = _MoleculeId()
MoleculeName        = _MoleculeName()
TemplateEnd         = _TemplateEnd()
TemplateStart       = _TemplateStart()
ReadEnd             = _ReadEnd()
ReadStart           = _ReadStart()
Barcode             = _Barcode()
MapQV               = _MapQV()
WhiteList           = _WhiteList()
AverageBarcodeScore = _AverageBarcodeScore()

MoleculeReadStart   = _MoleculeReadStart()
MinSubreadLength    = _MinSubreadLength()
MaxSubreadLength    = _MaxSubreadLength()
UnrolledReadLength  = _UnrolledReadLength()

DefaultSortBy       = Tbl(alignmentIdx = AlignmentIdx)

def query(reader, what = DefaultWhat, where = DefaultWhere,
          groupBy = DefaultGroupBy, groupByCsv = None, 
          sortBy = DefaultSortBy, limit = None):
    idxs = NP.where(where.eval(reader, range(0, len(reader))))[0]
    if groupByCsv:
        groupBy = groupCsv(groupByCsv, idxs, reader)
    else:
        groupBy = groupBy.eval(reader, idxs)
    results = {}
    
    for k,v in split(idxs, groupBy).items():
        sortVals = sortBy.eval(reader, v)
        sortIdxs = v[NP.lexsort(map(lambda z : z[1], sortVals)[::-1])][:limit]
        results[k] = what.eval(reader, sortIdxs)
    return results
