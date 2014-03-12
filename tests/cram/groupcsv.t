  $ export INCMP=$TESTDIR/../../etc/aligned_reads_ss.cmp.h5
  $ export INCSV=$TESTDIR/../../etc/grouped.csv
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
