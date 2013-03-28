## Overview
This document describes the cmph5tools.py query interface. This
interface is used to both produce data tables as well as new cmp.h5
files. The interface is meant to be somewhat similar to SQL.

At the heart of the new tools is a small query language for extracting
alignments and computing statistics over those alignments. The three
relevant clauses are: `what`, `where`, and `groupBy`. 

## Example 1: produce a sub-sampled cmp.h5 file

  $ export INCMP=$TESTDIR/../etc/aligned_reads_ss.cmp.h5

take 50% of the reads 

  $ cmph5tools.py select --where "SubSample(.5)" $INCMP --outFile ss.cmp.h5
  $ test -f ss.cmp.h5

## Example 2: produce tabular data from a cmp.h5 file

  $ cmph5tools.py stats --what "Tbl(q = Percentile(ReadLength, 90), m = Median(Accuracy))" \
  > --groupBy Barcode $INCMP | tail
  bc_88--bc_88      486.40          0.91
  bc_89--bc_89      561.00          0.91
  bc_9--bc_9        479.80          0.90
  bc_90--bc_90      563.60          0.89
  bc_91--bc_91      554.60          0.91
  bc_92--bc_92      523.00          0.90
  bc_93--bc_93      542.00          0.90
  bc_94--bc_94      518.00          0.90
  bc_95--bc_95      512.20          0.91
  bc_96--bc_96      609.60          0.92


## Example 3: query the package to determine the available metrics and statistics

  $ cmph5tools.py listMetrics
  --- Metrics:
  ByFactor[metric, factor, statistic]\t (esc)
  _MoleculeReadStart\t (esc)
  _MinSubreadLength\t (esc)
  _MaxSubreadLength\t (esc)
  _UnrolledReadLength\t (esc)
  TemplateSpan
  \tThe number of template bases covered by the read\t (esc)
  ReadLength\t (esc)
  NErrors\t (esc)
  ReadDuration\t (esc)
  FrameRate\t (esc)
  IPD\t (esc)
  PulseWidth\t (esc)
  Movie\t (esc)
  Movie2\t (esc)
  Reference\t (esc)
  RefIdentifier\t (esc)
  HoleNumber\t (esc)
  ReadStart\t (esc)
  ReadEnd\t (esc)
  TemplateStart\t (esc)
  TemplateEnd\t (esc)
  MoleculeId\t (esc)
  MoleculeName\t (esc)
  Strand\t (esc)
  AlignmentIdx\t (esc)
  Barcode\t (esc)
  SubSample[rate, n]
  \tboolean vector with true occuring at rate rate or nreads = n (esc)
  
  --- Statistics:
  Min\t (esc)
  Max\t (esc)
  Sum\t (esc)
  Mean\t (esc)
  Median\t (esc)
  Count\t (esc)
  Percentile[metric, ptile]\t (esc)
  Round[metric, digits]

## Example 4: Familiar SQL-like syntax

  $ cmph5tools.py stats --what "Tbl(a=Accuracy,b=Barcode)" \
  > --where "Barcode == 'bc_78--bc_78'" \
  > --groupBy Reference $INCMP
  Group                a          b
  MET_600_t2_2      0.94          bc_78--bc_78          
  MET_600_t2_2      0.90          bc_78--bc_78          
  MET_600_t2_2      0.90          bc_78--bc_78          
  MET_600_t2_2      0.87          bc_78--bc_78          
  MET_600_t2_2      0.89          bc_78--bc_78          
  MET_600_t2_2      0.85          bc_78--bc_78          
  MET_600_t2_2      0.82          bc_78--bc_78          
  MET_600_t2_2      0.96          bc_78--bc_78          

## Example 5: Familiar SQL-like functions

  $ cmph5tools.py stats --what "Count(Reference)" \
  > --where "Barcode == 'bc_78--bc_78'" \
  > --groupBy Reference $INCMP
  Group             Count(Reference)
  MET_600_t2_2                     8

## Handling IPD, PulseWidth, and Base-level Metrics

A constant _hurdle_ with cmp.h5 is dealing with the different sized
data, i.e., base-level data and alignment-level data. The stats tool
provides convenience functions for dealing with this

  $ cmph5tools.py stats --where "(Barcode == 'bc_78--bc_78') & (Accuracy > .95)" \
  > --what "Tbl(idx = AlignmentIdx, ipd = Median(IPD), pw = Median(PulseWidth))" \
  > $INCMP
             ipd             pw           idx
            9.00          12.00          1683

**NOTE:** The '(' surrounding the clauses in the where predicate are

## Selection
Some of our internal tools work on an entire cmp.h5 file. In
particular, a good deal of the Milhouse plotting code treats an input
cmp.h5 file as a single condition. This _pushes_ the logic of plotting
down into the individual plotting functions, e.g.,
`gAccuracyByReferenceSequence`. Instead, we can use tools like
selection to produce plots on very arbitrary splits.

  $ cmph5tools.py select --where "Accuracy > .95" $INCMP
  $ cmph5tools.py summarize out.cmp.h5
  ----------------------------------------
  filename: out.cmp.h5
  version:  1.3.1.PB
  n reads:  91
  n refs:   40
  n movies: 4
  n bases:  15315
  avg rl:   168
  avg acc:  0.9658

## Selection
  $ cmph5tools.py select --groupBy Barcode \
  > --where "(Barcode == 'bc_42--bc_42') | (Barcode == 'bc_28--bc_28')" $INCMP
  $ cmph5tools.py merge --outFile merged.cmp.h5 bc_42--bc_42.cmp.h5 bc_28--bc_28.cmp.h5
  $ cmph5tools.py stats --what "Count(Reference)" --groupBy Barcode merged.cmp.h5
  Group             Count(Reference)
  bc_28--bc_28                     6
  bc_42--bc_42                    65


**NOTE:** One of the reasons that the cmp.h5 file format is appealing
is that you don't need to split it to access particular strata. In
practice, we probably don't want to be splitting files up; A
_View_-type design pattern might be more appropriate.

## Implementation
The _Stats_ interface is defined
`pbtools.pbh5tools.Metrics`. Implementing new metrics and statistics
is fairly straightforward. In fact, all of the heavy lifting is
performed by D. Alexander's `CmpH5Reader`.
