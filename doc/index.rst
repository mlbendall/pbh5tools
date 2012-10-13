.. pbh5tools documentation master file, created by
   sphinx-quickstart on Thu Nov 10 17:09:22 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
pbh5tools
=========

``pbh5tools`` is a collection of tools that can manipulate the content or extract data from 
2 types of h5 files:

* ``cmp.h5``: files that contain alignment information.
* ``bas.h5`` and ``pls.h5``: files that contain base-call information.

``pbh5tools`` is comprised of 2 scripts that each depends on one of the
above data inputs: ``cmph5tools.py`` and ``bash5tools.py``. The former
is multi-commandline tool that provides access to a series of tasks
that can manipulate the content of ``cmp.h5`` files, compare such
files for equivalence as well as extract alignment information data
and summary metrics (see below). The ``bash5tools.py`` produces
``fasta``, ``fastq`` and ``csv`` files from a given ``bas.h5`` file.

What follows is a more in-depth description of the 2 scripts and their usage.

############
Dependencies
############

``pbh5tools`` depend on PacBio's ``pbcore`` library as well as the ``numpy`` and ``h5py`` python 
libraries.

############
Installation
############

To install ``pbh5tools``, run the following command from the ``pbh5tools`` root directory: ::

    python setup.py install

####################
Tool: bash5tools.py
####################

``bash5tools.py`` can extract read sequences and quality values for
both Raw and circular consensus sequencing (CCS) readtypes and use
create ``fastq`` and ``fasta`` files. Additionally, summary metric
information can be extracted for such reads in 2 formats:

* comma separated values (``csv``): file containing comma separated
  metric values, one line per read.
* detail (``dat``): more verbose version of the ``csv`` file
  content. This format is primarily used to visually inspect the read
  content of a ``bas.h5`` file.  Additionaly, it serves as example
  implementation to demonstrate how ``pbcore.io.BasH5IO`` can be used
  to process ``bas.h5`` files.

An example ``csv`` file generated using the as input the CCS reads
contained in the ``bas.h5`` file (using the following commandline
argument: ``--readType=CCS``) is shown bellow: ::

    ReadID,ZMWStatus,CCSReadLength,NumberOfPasses,MinQV,MaxQV,MeanQV
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/5,OUTSIDEFOV,84,24,41,126,98.5357142857
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/12,SEQUENCING,69,40,45,126,99.9420289855
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/13,SEQUENCING,89,10,41,86,63.1685393258
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/15,SEQUENCING,87,14,39,99,66.0

where:

* **ReadID**: Unique ID for the read that follows the following
    format: moviename_holenumber.
* **ZMWStatus**: Status for the ZMW/hole which generated the given
  read. Status can be FIDUCIAL, OUTSIDEFOV or SEQUENCING. The latter
  status is representative of reads that are used in downstream
  analysis and also those that will be present in both ``fasta`` and
  ``fastq`` files.
* **CCSReadLength**: Read length.
* **NumberOfPasses**: Number of subreads that were used to generate
    this CCS read.
* **MinQV**: The minimum per-base QV for all bases in the read.
* **MaxQV**: The maximum per-base QV for all bases in the read.
* **MeanQV**: The mean per-base QV for all bases in the read.

An example ``csv`` file for Raw reads (``--readType=Raw``) is shown
bellow: ::

    ReadID,ZMWStatus,ReadScore,ReadLength,NumberOfSubreads,NumberOfAdapters,MinQV,MaxQV,MeanQV
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/0,OUTSIDEFOV,0.0,87,1,0,33,39,33.1149425287
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/1,OUTSIDEFOV,0.0,98,1,0,33,37,33.1326530612
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/2,OUTSIDEFOV,0.0,121,1,0,33,38,33.132231405
    m110905_221747_42141_c100202782554400000315048309191122_s1_p0/3,OUTSIDEFOV,0.0,90,1,0,33,34,33.0111111111

where:

* **ReadScore**: Read score.
* **NumberOfSubreads**: Number of subreads that were sequenced from this ZMW.
* **NumberOfAdapters**: Number of adapters that were sequenced from this ZMW.

-----
Usage
-----
::

    usage: bash5tools.py [-h] [-i] [-d] [-v] [--outFilePref OUTFILEPREF]
                         [--readType READTYPE] [--outType OUTTYPE]
                         [--minLength MINLEN] [--minReadscore MINRS]
                         [--minMeanQV MINMQV] [--minNumberOfPasses MINNP]
                         input.bas.h5

    Tool for extracting data from .bas.h5
    Notes: For all command-line arguments, default values are listed in [].

    positional arguments:
      input.bas.h5          input .bas.h5 filename

    optional arguments:
      -h, --help            show this help message and exit
      -i, --info            turn on progress monitoring to stdout [False]
      -d, --debug           turn on progress monitoring to stdout and keep temp files [False]
      -v, --version         show program's version number and exit
      --outFilePref OUTFILEPREF
                        output filename prefix []
      --readType READTYPE   read type (CCS or Raw) [Raw]
      --outType OUTTYPE     output file type (fasta, fastq, csv or detail) [fasta]

    read filtering arguments:
      --minLength MINLEN    min read length [0]
      --minReadscore MINRS  min read score, valid only when used with --readType-Raw [0]
      --minMeanQV MINMQV    min per read mean Quality Value [0]
      --minNumberOfPasses MINNP
                            min number of CCS passes, valid only when used with --readType=CCS [0]

--------
Examples
--------

Extracting all Raw reads from ``input.bas.h5`` without any filtering
and exporting to FASTA (``myreads.fasta``): ::

    python bash5tools.py --inFile input.bas.h5 --outFilePref myreads --outType fasta --readType Raw

Extracting all CCS reads from ``input.bas.h5`` that have read lengths
larger than 100 and exporting to FASTQ (``myreads.fastq``): ::

    python bash5tools.py --inFile input.bas.h5 --outFilePref myreads --outType fastq --readType CCS --minLength 100

Extracting all CCS reads from ``input.bas.h5`` and exporting data to
the Detail file output format (``myreads.dat``): ::

    python bash5tools.py --inFile input.bas.h5 --outFilePref myreads --outType detail --readType CCS

####################
Tool: cmph5tools.py
####################

``cmph5tools.py`` is a multi-commandline tool that provides access to
the following 6 subtools:

1. **merge**: Merge multiple ``cmp.h5`` files into one.
2. **sort**: Sort a ``cmp.h5`` file.
3. **trim**: Trim the contents of a ``cmp.h5`` file by downsampling
   subread alignments or splitting the original ``cmp.h5`` file into
   multiple, smaller files.
4. **compare**: Compare the contents of 2 ``cmp.h5`` files for
equivalence.
5. **summarize**: Summarize the contents of a ``cmp.h5`` file in a
verbose, human readable format.
6. **tocsv**: Extract summary metrics from a ``cmp.h5`` file into a
``csv`` file.

To list all available subtools provided by ``cmph5tools.py`` simply
run: ::

    cmph5tools.py --help

Each subtool has its own usage information which can be generated by
running: ::

    cmph5tools.py <toolname> --help

To run any subtool it is suggested to use the ``--info`` commandline
argument since this will provide progress information while the script
is running via printing in stdout: ::

    cmph5tools.py <toolname> --info <other arguments>

What follows is a more detailed overview of each subtool including
examples.

--------------
Subtool: merge
--------------

``cmph5tools.py merge`` accepts multiple ``cmp.h5`` files as input
from which it will select the first file as the seed, create a copy on
disk and proceed to sequentially merge the rest of the ``cmp.h5``
files into it. All input files are checked for validity before they
are merged. Input files containing 0 alignments or inconsistencies in
the type and content of their HDF5DataSets (compared to eachother
within a file and between a given ``cmp.h5`` file and the seed), will
be rejected. If one knowingly wants to force the merge to go through
and by-pass such validation, the ``--forceMerge`` commandline argument
can be used. This is not advised but may come handy for ``cmp.h5``
files that contain different collection of pulse metrics HDF5DataSets
and one is solely interested in looking at the alignment content of
the merged file and not the kinetics-associated content.

^^^^^
Usage
^^^^^
::

    usage: cmph5tools.py merge [-h] [-i] [-d] [-v] [--outFile OUTFILE]
                               [--forceMerge]
                               input.cmp.h5 [input.cmp.h5 ...]
    
    Merge multiple cmp.h5 files. Supports both 'safe' merging where only cmp.h5
    files that contain the same H5Datasets compared to the sedding .cmp.file will
    be merged and 'unsafe' where no such considerations are taken into account.
    
    positional arguments:
      input.cmp.h5       input filenames
    
    optional arguments:
      -h, --help         show this help message and exit
      -i, --info         turn on progress monitoring to stdout [False]
      -d, --debug        turn on progress monitoring to stdout and keep temp files
                         [False]
      -v, --version      show program's version number and exit
      --outFile OUTFILE  output filename [out.cmp.h5]
      --forceMerge       bypass validation of cmp.h5 files before merging and
                         force merge [False]
    
^^^^^^^^
Examples
^^^^^^^^

Merging 3 ``cmp.h5`` files into a single output ``cmp.h5`` file named
``merged.cmp.h5``: ::

    cmph5tools.py merge --info --outFile=merged.cmp.h5 one.cmp.h5 two.cmp.h5 three.cmp.h5

-------------
Subtool: sort
-------------
``cmph5tools.py sort`` will sort a ``cmp.h5`` file by reference
sequence position. Sorting can be done in place or generate a new
``cmp.h5`` file. The former is the default behavior whilst for the
latter, the ``--outFile`` commandline argument is required. Finally,
by using the ``--deep`` commandline argument one can enforce deep
sorting to take place by sorting the contents of the AlignmentArray
HDF5DataSets as well. The main reason for using this argument is to
optimze retrieval of alignments from the resulting ``cmp.h5`` files
thus speeding up analysis that might depend on such data.

^^^^^
Usage
^^^^^
::

    usage: cmph5tools.py sort [-h] [-i] [-d] [-v] [--outFile OUTFILE] [--deep]
                              [--jobs JOBS] [--tmpDir TMPDIR]
                              input.cmp.h5
    
    Sort cmp.h5 files. If output-file is unspecified the input-file is
    overwritten. If there are a number of reference groups then the indexing
    processing can occur in parallel.
    
    positional arguments:
      input.cmp.h5       input filename
    
    optional arguments:
      -h, --help         show this help message and exit
      -i, --info         turn on progress monitoring to stdout [False]
      -d, --debug        turn on progress monitoring to stdout and keep temp files
                         [False]
      -v, --version      show program's version number and exit
      --outFile OUTFILE  output filename
      --deep             whether a deep sorting should be conducted, i.e. sort the
                         AlignmentArrays [False]
      --jobs JOBS        number of child processes to launch. Speed up realized
                         for multiple references groups. Not yet Implemented [1]
      --tmpDir TMPDIR    temporary directory to use when sorting in-place [/tmp]
    
^^^^^^^^
Examples
^^^^^^^^

Sort a ``cmp.h5`` file in place i.e. without creating a copy: ::

    cmph5tools.py sort --info aligned_reads.cmp.h5

Create a sorted copy of ``cmp.h5`` file, using deep sorting: ::

    cmph5tools.py sort --info --deep --outFile=myreads_sorted.cmp.h5 aligned_reads.cmp.h5

-------------
Subtool: trim
-------------
``cmph5tools.py trim`` supports 2 main functions:

* Splitting a ``cmp.h5`` file by reference sequence (``--mode=split``).
* Uniformly sampling N number of subreads within a ``cmp.h5`` and storing these in K
  number of cmp.h5 files (``--mode=sample``)

For ``--mode=sample`` the size of the generated ``cmp.h5`` files will be identical
to the original one since no actual HDF5 Datasets are removed. Downsampling is achieved by
having the ``cmp.h5`` file "indicate" to downstream tools that it solely contains the N number of 
decided subreads. Also, as indicated above, currently only splitting by reference is supported
but future implementation will support by movie as well.

^^^^^
Usage
^^^^^
::

    usage: cmph5tools.py trim [-h] [-i] [-d] [-v] --mode MODE [--outDir OUTDIR]
                              [--splitBy SPLITBY] [--fullRefName]
                              [--nOutFiles NOUTFILES] [--nSubReads NSUBREADS]
                              input.cmp.h5

    Trim a cmp.h5 file's contents by removing references, movies or a set number
    of subreads. Also, produce sampled versions of cmp.h5 files.

    positional arguments:
      input.cmp.h5          input filename

    optional arguments:
      -h, --help            show this help message and exit
      -i, --info            turn on progress monitoring to stdout [False]
      -d, --debug           turn on progress monitoring to stdout and keep temp
                            files [False]
      -v, --version         show program's version number and exit
      --mode MODE           sample or split
      --outDir OUTDIR       output directory to store new cmp.h5 files [./]

    splitting arguments:
      --splitBy SPLITBY     reference [reference]
      --fullRefName         Use full reference name for naming splits [False]

    sampling arguments:
      --nOutFiles NOUTFILES
                            number of cmp.h5 files to generate [2]
      --nSubReads NSUBREADS
                            number of subreads per cmp.h5 file [500]

^^^^^^^^
Examples
^^^^^^^^

Split a ``cmp.h5`` file by reference and generate ``cmp.h5`` files that are named after their
respective reference sequences: ::

    cmph5tools.py trim --info --mode=split --splitBy=reference --fullRefName aligned_reads.cmp.h5

Downsample subreads from a ``cmp.h5`` file into 5 new ``cmp.h5`` files containing 500 subreads 
each: ::

    cmph5tools.py trim --info --mode=sample --nOutFiles=5 --nSubReads=500 aligned_reads.cmp.h5

----------------
Subtool: compare
----------------
``cmph5tools.py compare`` compares 2 cmp.h5 for equivalence by making sure that for the set of
alignments that originated from the same movie and ZMW, aligned sequence and pulse metrics data 
are identical. It is also made sure that the number and identity of reference sequences and movies
in the 2 cmp.h5 files are identical.

^^^^^
Usage
^^^^^
::

    usage: cmph5tools.py compare [-h] [-i] [-d] [-v] input.cmp.h5 input.cmp.h5

    Compare 2 cmp.h5 files for equivalence.

    positional arguments:
      input.cmp.h5   input filenames

    optional arguments:
      -h, --help     show this help message and exit
      -i, --info     turn on progress monitoring to stdout [False]
      -d, --debug    turn on progress monitoring to stdout and keep temp files
                     [False]
      -v, --version  show program's version number and exit

^^^^^^^^
Examples
^^^^^^^^

Compare 2 ``cmp.h5`` files for content equivalence: ::

    cmph5tools.py compare --info one.cmp.h5 two.cmp.h5

------------------
Subtool: summarize
------------------
``cmph5tools.py summarize`` summarizes the contents of a ``cmp.h5`` file in stdout.
It does so by summarizing each HDF5 Group and Dataset present within the ``cmp.h5``
file as well as providing a more top level summary that includes the number of subreads
and reads, name of reference sequences, primary analysis software versions etc.

^^^^^
Usage
^^^^^
::

    usage: cmph5tools.py summarize [-h] [-i] [-d] [-v] input.cmp.h5

    Print summary for a cmp.h5 file.

    positional arguments:
      input.cmp.h5   input filename

    optional arguments:
      -h, --help     show this help message and exit
      -i, --info     turn on progress monitoring to stdout [False]
      -d, --debug    turn on progress monitoring to stdout and keep temp files
                     [False]
      -v, --version  show program's version number and exit

^^^^^^^^
Examples
^^^^^^^^

Summarize contents for ``cmp.h5`` file and store results in a log file: ::

    cmph5tools.py summarize --info aligned_reads.cmp.h5 > mylog.txt


############
Known Issues
############
* None

##################
Indices and tables
##################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

