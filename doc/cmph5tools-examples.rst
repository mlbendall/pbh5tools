############################
cmph5tools.py Query Examples
############################

This interface is used to both produce data tables as well as new cmp.h5 files. The interface is meant to be somewhat similar to SQL.
At the heart of the new tools is a small query language for extracting alignments and computing statistics over those alignments. 
The three relevant clauses are: ``what``, ``where``, and ``groupBy``. 

--------------------------------------------
Example 1: Produce a sub-sampled cmp.h5 file
--------------------------------------------

Take 50% of the reads: ::

    $ cmph5tools.py select --where "SubSample(rate=.5)" \
    > --outFile ss.cmp.h5 aligned_reads.cmp.h5
    
-------------------------------------------
Example 2: Produce per-Barcode cmp.h5 files
-------------------------------------------

Filter by AverageBarcodeScore: ::

    $ cmph5tools.py select --where "AverageBarcodeScore >= 30" \
    > --groupBy Barcode aligned_reads.cmp.h5
   
--------------------------------------------------
Example 3: Produce tabular data from a cmp.h5 File    
--------------------------------------------------

Grouped Statistics: :: 

    $ cmph5tools.py stats --what "Tbl(q = Percentile(ReadLength, 90), m = Median(Accuracy))" \
    > --groupBy Barcode aligned_reads.cmp.h5 | tail
    bc_88--bc_88      486.40          0.91
    bc_89--bc_89      561.00          0.91
    bc_9--bc_9        479.80          0.90 
    bc_90--bc_90      563.60          0.89
    bc_91--bc_91      554.60          0.91
    bc_92--bc_92      523.00          0.90
    bc_93--bc_93      542.00          0.90
    bc_94--bc_94      518.00          0.90
    bc_95--bc_95      512.20          0.91
    bc_96--bc_96      609.60          0.92

------------------------------------------------------------------------------
Example 4: Query the package to determine the available metrics and statistics
------------------------------------------------------------------------------

Metrics and Statistics: ::

    $ cmph5tools.py listMetrics
    --- Metrics:
    ByFactor[metric, factor, statistic]	
    _MoleculeReadStart	
    _MinSubreadLength	
    _MaxSubreadLength	
    _UnrolledReadLength	
    DefaultWhere	
    DefaultGroupBy	
    TemplateSpan
	The number of template bases covered by the read	
    ReadLength	
    NErrors	
    ReadDuration	
    FrameRate	
    IPD	
    PulseWidth	
    Movie	
    Reference	
    RefIdentifier	
    HoleNumber	
    ReadStart	 
    ReadEnd	
    TemplateStart	
    TemplateEnd	
    MoleculeId	
    MoleculeName	
    Strand	
    AlignmentIdx	
    Barcode	
    AverageBarcodeScore	
    MapQV	
    WhiteList	
    SubSample[rate, n]
       	boolean vector with true occuring at rate rate or nreads = n
 
    --- Statistics:
    Min	
    Max	
    Sum	
    Mean	
    Median	
    Count	
    Percentile[metric, ptile]	
    Round[metric, digits]

-----------------------------------
Example 5: Familiar SQL-like syntax
-----------------------------------

Filter by barcode and group by reference: ::

    $ cmph5tools.py stats --what "Tbl(a=Accuracy,b=Barcode)" \
    > --where "Barcode == 'bc_78--bc_78'"  \
    > --groupBy Reference aligned_reads.cmp.h5
    Group                a          b
    MET_600_t2_2      0.96          bc_78--bc_78          
    MET_600_t2_2      0.82          bc_78--bc_78          
    MET_600_t2_2      0.85          bc_78--bc_78          
    MET_600_t2_2      0.89          bc_78--bc_78          
    MET_600_t2_2      0.87          bc_78--bc_78          
    MET_600_t2_2      0.90          bc_78--bc_78          
    MET_600_t2_2      0.90          bc_78--bc_78          
    MET_600_t2_2      0.94          bc_78--bc_78

--------------------------------------
Example 6: Familiar SQL-like functions
--------------------------------------

Count alignments: ::

    $ cmph5tools.py stats --what "Count(Reference)" \
    > --where "Barcode == 'bc_78--bc_78'" \
    > --groupBy Reference aligned_reads.cmp.h5
    Group             Count(Reference)
    MET_600_t2_2                     8
