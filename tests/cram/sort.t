  $ export INH5=`python -c "from pbcore import data ; print data.getCmpH5()"`
  $ cmph5tools.py sort --deep --outFile tmp.cmp.h5 $INH5
  $ echo $?  
  0
  $ cmph5tools.py sort --deep --inPlace tmp.cmp.h5
  $ echo $?  
  0
  $ cmph5tools.py sort --deep tmp.cmp.h5
  $ echo $?
  0
  $ cmph5tools.py sort --outFile ftmp.cmp.h5 $INH5
  $ echo $?
  0
  $ python -c "from pbcore.io import CmpH5Reader; a = CmpH5Reader('tmp.cmp.h5'); b = CmpH5Reader('ftmp.cmp.h5'); print(all([a[i] == b[i] for i in xrange(len(a))]));"
  True
  $ cmph5tools.py sort --outFile ptmp.cmp.h5 --deep --usePythonIndexer $INH5
  $ echo $?
  0
  $ cmph5tools.py equal tmp.cmp.h5 ptmp.cmp.h5
  $ echo $?
  0
