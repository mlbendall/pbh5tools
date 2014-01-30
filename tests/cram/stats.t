  $ . $TESTDIR/portability.sh

Set up inputs and basic command string.
  $ INH5=`python -c "from pbcore import data ; print data.getCmpH5()['cmph5']"`
  $ CMD="cmph5tools.py stats $INH5"

Print Readlength to stdout
  $ $CMD --what "ReadLength" | head -5
  ReadLength
  301                           
  404                           
  342                           
  254                           
Print multiple columns                        
  $ $CMD --what "Tbl(readlength = ReadLength, accuracy = Accuracy)" | head -5
  readlength                    accuracy
  301                               0.84
  404                               0.82
  342                               0.87
  254                               0.82
Aggregate statistics on entire dataset
  $ $CMD --what "Tbl(mrl = Percentile(ReadLength, 90), macc = Mean(Accuracy))"
                         mrl                    macc
                      481.80                    0.83
Access movie name for each alignment
  $ $CMD --what "Movie" | head -5
                         Movie
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0
Aggregate statistics for a single movie
  $ $CMD --what "Tbl(mrl = Percentile(ReadLength, 90), macc = Mean(Accuracy))" --where "Movie == 'm110818_075520_42141_c100129202555500000315043109121112_s1_p0'"
                         mrl                    macc
                      547.80                    0.84
Aggregate statistics grouped by movie                      
  $ $CMD --what "Tbl(mrl = Percentile(ReadLength, 90), macc = Mean(Accuracy))" --groupBy "Movie"
                         Group                       mrl                    macc
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                    547.80                    0.84
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0                    445.20                    0.83
Aggregate statistics grouped by multiple factors
  $ $CMD --what "Tbl(mrl = Percentile(ReadLength, 90), macc = Mean(Accuracy))" --groupBy "Movie * Reference"
                         Group                       mrl                    macc
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    547.80                    0.84
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011                    445.20                    0.83
Per-alignment metrics grouped by multiple factors
  $ $CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD))" --groupBy "Movie * Reference" | head -5
                         Group                    readlength                    errorRate                     ipd
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    342                                0.13                    0.18
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    254                                0.18                    0.25
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    267                                0.16                    0.15
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    354                                0.16                    0.24
Per-alignment metrics grouped and filtered 
  $ $CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD), holeNumber = HoleNumber)" --groupBy "Movie * Reference" --where "HoleNumber != 9" | head -5
                         Group                    readlength                    errorRate                     ipd                    holeNumber
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    342                                0.13                    0.18                    2001                          
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    254                                0.18                    0.25                    2001                          
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    267                                0.16                    0.15                    4009                          
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011                    354                                0.16                    0.24                    2008                          
Check MapQV output
  $ $CMD --what "Tbl(readlength = ReadLength, mapqv = MapQV)" --where "(ReadLength > 400) & (MapQV > 0)" | head -5
  readlength                    mapqv
  404                           254                      
  684                           254                      
  674                           254                      
  486                           254                      
Generate whitelist for other pipelines.  **zmw's not unique, includes header**
  $ $CMD --what WhiteList --where "ReadLength > 400" --outFile out.csv
  $ tail -n +2 out.csv | uniq
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0/3008
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0/1000
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0/2006
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0/1007
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0/4007
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0/1002
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0/9
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0/9
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0/2003
Test 'select' subtool commands
  $ SCMD="cmph5tools.py select $INH5"
Generate new cmp.h5 files per movie with length/accuracy filtering
  $ $SCMD --where "(ReadLength > 100) & (Accuracy < .8)" --groupBy "Movie"
  $ cmph5tools.py summarize *.cmp.h5
  ----------------------------------------
  filename: m110818_075520_42141_c100129202555500000315043109121112_s1_p0.cmp.h5
  version:  1.2.0.SF
  n reads:  3
  n refs:   1
  n movies: 1
  n bases:  666
  avg rl:   222
  avg acc:  0.7942
  
  \t Movie Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0     666                0.8             222.0
  
  \t Reference Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  lambda_NEB3011     666                0.8             222.0
  ----------------------------------------
  filename: m110818_075520_42141_c100129202555500000315043109121112_s2_p0.cmp.h5
  version:  1.2.0.SF
  n reads:  3
  n refs:   1
  n movies: 1
  n bases:  676
  avg rl:   225
  avg acc:  0.7943
  
  \t Movie Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0     676                0.8             225.3
  
  \t Reference Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  lambda_NEB3011     676                0.8             225.3
Make new cmp.h5 with subset of indexed alignments
  $ $SCMD --idx 1 2 3 4 --outFile 1234.cmp.h5
  $ cmph5tools.py summarize 1234.cmp.h5
  ----------------------------------------
  filename: 1234.cmp.h5
  version:  1.2.0.SF
  n reads:  4
  n refs:   1
  n movies: 2
  n bases:  1267
  avg rl:   317
  avg acc:  0.8391
  
  \t Movie Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0     863                0.8             287.7
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0     404                0.8             404.0
  
  \t Reference Summary: (esc)
          Group     nBases     avgAccuracy     avgReadLength
  lambda_NEB3011     1267               0.8             316.8
Check that default 'what' clause prints readlength and accuracy (all reads)
  $ cmph5tools.py stats $INH5 | head -5
  readLength                    accuracy
  301                               0.84
  404                               0.82
  342                               0.87
  254                               0.82
Export to csv file 
  $ $CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD))" --groupBy "Movie * Reference" --outFile out.csv
  $ linecount out.csv
  85
  $ tail -n 1 out.csv
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011,182,0.1538,0.3418
Export to csv file (2)
  $ $CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD))" --groupBy "Movie * Reference" --where "Accuracy > .85" --outFile out.csv
  $ linecount out.csv
  26
Check sortBy clause -- note order of sort metrics is not deterministic
  $ $CMD --what "(Accuracy,ReadLength)" --sortBy "Round(Accuracy, 2), ReadLength" --where "Movie == 'm110818_075520_42141_c100129202555500000315043109121112_s1_p0'" | head -10
  ReadLength                    1.0-NErrors/ReadLength*1.0
  116                                                 0.84
  128                                                 0.80
  153                                                 0.84
  188                                                 0.84
  195                                                 0.86
  204                                                 0.79
  211                                                 0.83
  250                                                 0.80
  254                                                 0.82
Check sortBy and grouping (no aggregate)
  $ $CMD --what "(Accuracy, )" --sortBy ReadLength --groupBy Movie | head -5
                         Group                    1.0-NErrors/ReadLength*1.0
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                          0.84
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                          0.80
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                          0.84
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                          0.84
Check sortBy and grouping (with aggregate)
  $ $CMD --what "(Mean(Accuracy), )" --sortBy ReadLength --groupBy Movie
                         Group                    Mean(1.0-NErrors/ReadLength*1.0)
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                                0.84
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0                                                0.83
Check arithmetic in what clause
  $ $CMD --what "(Mean(100* Accuracy)/Sum(Accuracy), )" --sortBy ReadLength --groupBy Movie
                         Group                    Mean(100*1.0-NErrors/ReadLength*1.0)/Sum(1.0-NErrors/ReadLength*1.0)
  m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                                                                    2.56
  m110818_075520_42141_c100129202555500000315043109121112_s2_p0                                                                                    2.22
Output columns from tuple and group by multiple factors (sorting within group)
  $ $CMD --what "(Sum(ReadLength), Mean(Accuracy))" --sortBy ReadLength --groupBy HoleNumber*Movie | head -5
                         Group                    Mean(1.0-NErrors/ReadLength*1.0)                    Sum(ReadLength)
  1000:m110818_075520_42141_c100129202555500000315043109121112_s1_p0                                                0.83                    811                                
  1000:m110818_075520_42141_c100129202555500000315043109121112_s2_p0                                                0.82                    1358                               
  1002:m110818_075520_42141_c100129202555500000315043109121112_s2_p0                                                0.87                    589                                
  1004:m110818_075520_42141_c100129202555500000315043109121112_s2_p0                                                0.82                    439                                
