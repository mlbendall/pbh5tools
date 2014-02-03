  $ export INH5=`python -c "from pbcore import data ; print data.getCmpH5()"`
  $ cmph5tools.py select $INH5 --outFile left.cmp.h5 --idx 0 1 2 3
  $ echo $?  
  0
  $ cmph5tools.py select $INH5 --outFile right.cmp.h5 --idx 4 5 6 7
  $ echo $?  
  0
  $ cmph5tools.py merge --outFile merged.cmp.h5 left.cmp.h5 right.cmp.h5
  $ echo $?
  0
  $ cmph5tools.py select $INH5 --outFile tot.cmp.h5 --idx 0 1 2 3 4 5 6 7
  $ echo $?
  0
  $ cmph5tools.py sort merged.cmp.h5
  $ cmph5tools.py sort tot.cmp.h5
  $ cmph5tools.py equal tot.cmp.h5 merged.cmp.h5
  $ echo $?
  0
  $ cmph5tools.py merge --outFile merged1.cmp.h5 $INH5
  $ echo $?
  0
  $ cmph5tools.py sort --inPlace merged1.cmp.h5
  $ echo $?
  0
  $ cmph5tools.py equal merged1.cmp.h5 $INH5
  $ echo $?       
  0
