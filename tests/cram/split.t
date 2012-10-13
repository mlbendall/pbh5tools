  $ export INH5=`python -c "from pbcore import data ; print data.getCmpH5()['cmph5']"`
  $ cmph5tools.py split $INH5
  $ echo $?
  0
  $ ls ref000001.cmp.h5
  ref000001.cmp.h5
  $ echo $?
  0
