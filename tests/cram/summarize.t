Run some of the pbh5tools scripts to ensure that they run and produce
reasonable output.
  $ export INH5=`python -c "from pbcore import data ; print data.getCmpH5()['cmph5']"`
  $ cmph5tools.py summarize $INH5
  == aligned_reads_1.cmp.h5 ==
  /
      Index          : ['REF_ID' 'TARGET_START' 'TARGET_END']
      PrimaryVersion : 1.4.0.0.96725
      ReadType       : standard
      Total Subreads : 84
      Total Reads    : 28
      Version        : 1.2.0.SF
  
  /MovieInfo (2 entries):
      MasterDataset : ID
      nRow          : 2
      Data: 
          ID  Name
          1   m110818_075520_42141_c10012...
          2   m110818_075520_42141_c10012...
  
  /RefInfo (1 entries):
      MasterDataset : ID
      nRow          : 1
      Data: 
          ID  FullName        Length  MD5
          1   lambda_NEB3011  48502   a1319ff90e994c8190a4fe6569d...
  
  /RefGroup (1 entries):
      MasterDataset : ID
      nRow          : 1
      Data: 
          ID  Path        RefInfoID
          1   /ref000001  1
  
  /AlnGroup (2 entries):
      MasterDataset : ID
      nRow          : 2
      Data: 
          ID  Path
          1   /ref000001/m110818_075520_4...
          2   /ref000001/m110818_075520_4...
  
  /FileLog (3 entries):
      MasterDataset : ID
      nRow          : 3
      Data: 
          ID  Program              Version       Timestamp                   CommandLine                     Log
          1   compareSequences.py  v1.3.0.92208  2011-10-11T17:27:47.929899  /mnt/secondary/Smrtpipe/bui...  Initial Creation
          2   blasr                v1.3.0.92208  2011-10-11T17:27:47.933156  blasr /home/UNIXHOME/jbulla...  Initial Creation
          3   cmpH5Sort.py         .64           2011-10-11 17:27:48.546907  /mnt/secondary/Smrtpipe/bui...  Sorting
  
  /ref000001 (RefGroup):
  
      /ref000001/m110818_075520_42141_c100129202555500000315043109121112_s2_p0 (AlnGroup):
          Pulse Metrics : PulseWidth,IPD,QualityValue,DeletionQV
          Aligned Bases : 13551
          Aligned Reads : 45
          MasterDataset : AlnArray
  
      /ref000001/m110818_075520_42141_c100129202555500000315043109121112_s1_p0 (AlnGroup):
          Pulse Metrics : PulseWidth,IPD,QualityValue,DeletionQV
          Aligned Bases : 13663
          Aligned Reads : 39
          MasterDataset : AlnArray
  
