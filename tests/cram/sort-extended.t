  $ export INCMP=$TESTDIR/../../etc/aligned_reads_ss.cmp.h5
  $ cmph5tools.py sort $INCMP --outFile out.cmp.h5

  $ cmph5tools.py select --groupBy Barcode \
  > --where "(Barcode == 'bc_42--bc_42') | (Barcode == 'bc_28--bc_28')" $INCMP
  $ cmph5tools.py merge --outFile m1.cmp.h5 bc_42--bc_42.cmp.h5 \
  > bc_28--bc_28.cmp.h5

  $ cmph5tools.py merge --outFile m2.cmp.h5 bc_28--bc_28.cmp.h5 \
  > bc_42--bc_42.cmp.h5
  $ cmph5tools.py equal m1.cmp.h5 m2.cmp.h5
  (False, '40 alignments differ')
  $ cmph5tools.py sort --inPlace m1.cmp.h5
  $ cmph5tools.py sort --inPlace m2.cmp.h5
  $ cmph5tools.py equal m1.cmp.h5 m2.cmp.h5
  True

  $ cmph5tools.py select --where "SubSample(.05)" $INCMP \
  > --outFile ss.cmp.h5
  $ cmph5tools.py sort --outFile sss.cmp.h5 ss.cmp.h5
  $ cmph5tools.py equal sss.cmp.h5 ss.cmp.h5
  (False, *) (glob)

  $ cmph5tools.py validate sss.cmp.h5
  True
  $ cmph5tools.py validate ss.cmp.h5
  True
  $ cmph5tools.py validate m1.cmp.h5      
  True
  $ cmph5tools.py validate m2.cmp.h5      
  True
