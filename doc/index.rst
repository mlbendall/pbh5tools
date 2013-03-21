.. pbh5tools documentation master file, created by
   sphinx-quickstart on Thu Nov 10 17:09:22 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
pbh5tools
=========

``pbh5tools`` is a collection of tools that can manipulate the content or extract data from 
two types of h5 files:

* ``cmp.h5``: files that contain alignment information.
* ``bas.h5`` and ``pls.h5``: files that contain base-call information.

``pbh5tools`` is comprised of two executables: ``cmph5tools.py`` and
``bash5tools.py``. At the moment, the ``cmph5tools.py`` program
provides a rich set of tools to manipulate and analyze the data in a
``cmp.h5`` file. The ``bash5tools.py`` provides mechanisms to extract
basecall information from bas.h5 files. 

############
Dependencies
############

   'pbcore >= 0.1'
   'numpy >= 1.6.0',
   'h5py >= 1.3.0'

############
Installation
############

To install ``pbh5tools``, run the following command from the ``pbh5tools`` root directory: ::

   make install

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
the following subtools:

1. **merge**: Merge multiple ``cmp.h5`` files into a single file.

2. **sort**: Sort a ``cmp.h5`` file.

3. **select**: Create a new file from a ``cmp.h5`` file by specifying
which reads to include.

4. **equal**: Compare the contents of 2 ``cmp.h5`` files for
equivalence.

5. **summarize**: Summarize the contents of a ``cmp.h5`` file in a
verbose, human readable format.

6. **stats**: Extract summary metrics from a ``cmp.h5`` file into a
``csv`` file.

7. **valid**: Determine whether a ``cmp.h5`` file is valid.

8. **listMetrics**: Emit the available metrics and statistics for use
in the ``select`` and ``stats`` subcommands.

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

More examples are available in the examples.t file.

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

