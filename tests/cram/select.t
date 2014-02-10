  $ . $TESTDIR/portability.sh

Set up basic commands
  $ INH5=`python -c "from pbcore import data ; print data.getCmpH5()"`
  $ CMD="cmph5tools.py stats $INH5"
Test basic output
  $ $CMD --what "ReadStart" --limit 5
  ReadStart
  3                            
  353                          
  3580                         
  3253                         
  0                            
Test basic output (2)                   
  $ $CMD --what "MoleculeReadStart"  --limit 5
                      MoleculeReadStart
                                      3
                                      3
                                   3253
                                   3253
                                      0
Boolean output vector
  $ $CMD --what "MoleculeReadStart < 20"  --limit 5
  MoleculeReadStart < 20
  True                                      
  True                                      
  False                                     
  False                                     
  True                                      
Test where clause produces correct subset                                
  $ $CMD --what "MaxSubreadLength > 100" --limit 10
  MaxSubreadLength > 100
  True                                      
  True                                      
  True                                      
  True                                      
  True                                      
  True                                      
  True                                      
  True                                      
  True                                      
  True                                      
Test stdout same as in csv output                                   
  $ $CMD --what "UnrolledReadLength" | linecount
  85

  $ $CMD --what "UnrolledReadLength" --outFile out.csv
  $ linecount out.csv
  85
