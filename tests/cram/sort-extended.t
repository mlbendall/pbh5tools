  $ export INCMP=$TESTDIR/../../etc/aligned_reads_ss.cmp.h5
  $ cmph5tools.py sort $INCMP --outFile out.cmp.h5

  $ cmph5tools.py select --groupBy Barcode \
  > --where "(Barcode == 'F_42--R_42') | (Barcode == 'F_28--R_28')" $INCMP
  $ cmph5tools.py sort --inPlace F_42--R_42.cmp.h5
  $ cmph5tools.py merge --outFile m1.cmp.h5 F_42--R_42.cmp.h5 \
  > F_28--R_28.cmp.h5

  $ cmph5tools.py merge --outFile m2.cmp.h5 F_28--R_28.cmp.h5 \
  > F_42--R_42.cmp.h5
  $ cmph5tools.py equal m1.cmp.h5 m2.cmp.h5
  * alignments differ (glob)
  [1]
  $ cmph5tools.py sort --inPlace m1.cmp.h5
  $ cmph5tools.py sort --inPlace m2.cmp.h5
  $ cmph5tools.py equal m1.cmp.h5 m2.cmp.h5

  $ cmph5tools.py select --where "SubSample(.05)" $INCMP \
  > --outFile ss1.cmp.h5
  $ cmph5tools.py select --where "SubSample(.10)" $INCMP \
  > --outFile ss2.cmp.h5
  $ cmph5tools.py equal ss1.cmp.h5 ss2.cmp.h5
  cmp.h5 files differ in length* (glob)
  [1]
  $ cmph5tools.py validate ss1.cmp.h5
  $ cmph5tools.py validate ss2.cmp.h5
  $ cmph5tools.py validate m1.cmp.h5      
  $ cmph5tools.py validate m2.cmp.h5      
