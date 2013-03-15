  $ INH5=`python -c "from pbcore import data ; print data.getCmpH5()['cmph5']"`
  $ CMD="cmph5tools.py stats $INH5"
  
  $ $CMD --what "ReadStart"
  
  $ $CMD --what "MoleculeReadStart"  

  $ $CMD --what "MoleculeReadStart < 20"  
  
  $ $CMD --what "MaxSubreadLength > 100"
  
  $ $CMD --what "UnrolledReadLength"
