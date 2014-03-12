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
                    F_44--R_44                    516.80                    0.90
                    F_45--R_45                    534.60                    0.90
                    F_46--R_46                    517.80                    0.90
                    F_47--R_47                    515.80                    0.91
                    F_48--R_48                    624.20                    0.91
                      F_5--R_5                    571.60                    0.90
                      F_6--R_6                    507.90                    0.90
                      F_7--R_7                    572.40                    0.90
                      F_8--R_8                    574.40                    0.91
                      F_9--R_9                    485.60                    0.90


## Example 3: query the package to determine the available metrics and statistics

  $ cmph5tools.py listMetrics
  --- Metrics:
  ByFactor[metric, factor, statistic]\t (esc)
  _MoleculeReadStart\t (esc)
  _MinSubreadLength\t (esc)
  _MaxSubreadLength\t (esc)
  _UnrolledReadLength\t (esc)
  DefaultWhere\t (esc)
  DefaultGroupBy\t (esc)
  TemplateSpan
  \tThe number of template bases covered by the read\t (esc)
  ReadLength\t (esc)
  NErrors\t (esc)
  ReadDuration\t (esc)
  FrameRate\t (esc)
  IPD\t (esc)
  PulseWidth\t (esc)
  Movie\t (esc)
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
  AverageBarcodeScore\t (esc)
  MapQV\t (esc)
  WhiteList\t (esc)
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
  > --where "Barcode == 'F_28--R_28'" \
  > --groupBy Reference $INCMP
                         Group                       a                             b
                EGFR_600_t29_1                    0.91                    F_28--R_28
                EGFR_600_t29_1                    0.91                    F_28--R_28
                EGFR_600_t29_1                    0.95                    F_28--R_28
                EGFR_600_t29_1                    0.93                    F_28--R_28
                EGFR_600_t29_1                    0.91                    F_28--R_28
                EGFR_600_t29_1                    0.90                    F_28--R_28
                EGFR_600_t29_1                    0.94                    F_28--R_28
                EGFR_600_t29_1                    0.93                    F_28--R_28
                 EGFR_600_t9_1                    0.86                    F_28--R_28

## Example 5: Familiar SQL-like functions

  $ cmph5tools.py stats --what "Count(Reference)" \
  > --where "Barcode == 'F_10--R_10'" \
  > --groupBy Reference $INCMP
                         Group                    Count(Reference)
                EGFR_600_t11_1                                  62

## Handling IPD, PulseWidth, and Base-level Metrics

A constant _hurdle_ with cmp.h5 is dealing with the different sized
data, i.e., base-level data and alignment-level data. The stats tool
provides convenience functions for dealing with this

  $ cmph5tools.py stats --where "(Barcode == 'F_10--R_10') & (Accuracy > .95)" \
  > --what "Tbl(idx = AlignmentIdx, ipd = Median(IPD), pw = Median(PulseWidth))" \
  > $INCMP
                        ipd                       pw                    idx
                      15.50                    11.50                    562
                       9.00                    10.00                    563
                      11.00                    10.00                    589
                      13.00                    11.00                    603
                      14.00                    10.50                    626
                       8.00                    13.00                    627

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
  
  \t Movie Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  m121005_190843_42142_c100376662550000001523029810101285_s1_p0     4770               1.0             170.4
  m121005_190843_42142_c100376662550000001523029810101285_s2_p0     2259               1.0             173.8
  m121005_210848_42142_c100376662550000001523029810101286_s1_p0     6167               1.0             192.7
  m121005_210848_42142_c100376662550000001523029810101286_s2_p0     2119               1.0             117.7
  
  \t Reference Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  EGFR_600_t11_1     1396               1.0             232.7
  EGFR_600_t13_1     83                 1.0              41.5
  EGFR_600_t15_1     252                1.0             126.0
  EGFR_600_t16_1     50                 1.0              25.0
  EGFR_600_t17_1     531                1.0             531.0
  EGFR_600_t19_1     705                1.0             235.0
  EGFR_600_t20_1     184                1.0             184.0
  EGFR_600_t21_1     122                1.0             122.0
  EGFR_600_t23_1     553                1.0             276.5
  EGFR_600_t24_1     32                 1.0              32.0
  EGFR_600_t25_1     531                1.0             265.5
  EGFR_600_t26_1     55                 1.0              27.5
  EGFR_600_t27_1     148                1.0             148.0
  EGFR_600_t28_1     91                 1.0              30.3
  EGFR_600_t2_1     239                1.0              59.8
  EGFR_600_t3_1     462                1.0             462.0
  EGFR_600_t4_1     701                1.0             350.5
  EGFR_600_t5_1     147                1.0              49.0
  EGFR_600_t6_1     201                1.0              50.2
  EGFR_600_t7_1     873                1.0             436.5
  EGFR_600_t9_1     562                1.0             112.4
   MET_600_t2_1     42                 1.0              42.0
  MET_600_t2_11     681                1.0             227.0
  MET_600_t2_13     448                1.0             448.0
  MET_600_t2_14     223                1.0             223.0
  MET_600_t2_15     43                 1.0              43.0
  MET_600_t2_16     671                1.0             167.8
  MET_600_t2_17     44                 1.0              44.0
  MET_600_t2_18     701                1.0             175.2
  MET_600_t2_19     546                1.0             182.0
   MET_600_t2_2     186                1.0              93.0
  MET_600_t2_20     394                1.0              98.5
  MET_600_t2_21     71                 1.0              35.5
   MET_600_t2_3     655                1.0             218.3
   MET_600_t2_4     1321               1.0             330.2
   MET_600_t2_5     500                1.0             500.0
   MET_600_t2_6     120                1.0             120.0
   MET_600_t2_7     660                1.0             220.0
   MET_600_t2_8     24                 1.0              24.0
   MET_600_t2_9     67                 1.0              67.0

## Selection
  $ cmph5tools.py select --groupBy Barcode \
  > --where "(Barcode == 'F_42--R_42') | (Barcode == 'F_10--R_10')" $INCMP
  $ cmph5tools.py merge --outFile merged.cmp.h5 F_42--R_42.cmp.h5 F_10--R_10.cmp.h5
  $ cmph5tools.py stats --what "Count(Reference)" --groupBy Barcode merged.cmp.h5
                         Group                    Count(Reference)
                    F_10--R_10                                  62
                    F_42--R_42                                  76


cmp.h5 files can also be split by a pre-defined csv file with three columns.
The csv must contain a header.  Column 1 is group names.  Columns 2 and 3 header
names are metrics from 'cmph5tools.py listMetrics'
  $ export INCSV=$TESTDIR/../etc/grouped.csv
  $ cmph5tools.py select --groupByCsv $INCSV $INCMP

  $ cmph5tools.py stats grpA.cmp.h5
  readLength                    accuracy
  426                               0.90
  538                               0.92
  552                               0.92
  589                               0.89
  538                               0.92
  129                               0.91
  118                               0.83
  126                               0.85
  239                               0.92
  $ cmph5tools.py stats grpB.cmp.h5
  readLength                    accuracy
  156                               0.92
  347                               0.86
  531                               0.92
  550                               0.93
  122                               0.80
  86                                0.93
  132                               0.90
  $ cmph5tools.py stats grpC.cmp.h5
  readLength                    accuracy
  151                               0.90
  193                               0.90
  439                               0.90
  546                               0.90
  563                               0.90
  565                               0.92
  568                               0.89
  148                               0.95
  59                                0.88
  $ cmph5tools.py stats grpD.cmp.h5
  readLength                    accuracy
  95                                0.94
  304                               0.88
  455                               0.95
  489                               0.86
  584                               0.87
  558                               0.90
  567                               0.87
  543                               0.90
  170                               0.98
  171                               0.82

**NOTE:** One of the reasons that the cmp.h5 file format is appealing
is that you don't need to split it to access particular strata. In
practice, we probably don't want to be splitting files up; A
_View_-type design pattern might be more appropriate.

## Implementation
The _Stats_ interface is defined
`pbtools.pbh5tools.Metrics`. Implementing new metrics and statistics
is fairly straightforward. In fact, all of the heavy lifting is
performed by D. Alexander's `CmpH5Reader`.
