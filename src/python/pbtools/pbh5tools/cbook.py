"""
A collection of utility functions and classes.  Many (but not all)
from the Python Cookbook -- hence the name cbook
"""

def to_filehandle(fname, flag='rU', return_opened=False):
    """
    *fname* can be a filename or a file handle.  Support for gzipped
    files is automatic, if the filename ends in .gz.  *flag* is a
    read/write flag for :func:`file`
    """
    if is_string_like(fname):
        if fname.endswith('.gz'):
            import gzip
            # get rid of 'U' in flag for gzipped files.
            flag = flag.replace('U','')
            fh = gzip.open(fname, flag)
        elif fname.endswith('.bz2'):
            # get rid of 'U' in flag for bz2 files
            flag = flag.replace('U','')
            import bz2
            fh = bz2.BZ2File(fname, flag)
        else:
            fh = file(fname, flag)
        opened = True
    elif hasattr(fname, 'seek'):
        fh = fname
        opened = False
    else:
        raise ValueError('fname must be a string or file handle')
    if return_opened:
        return fh, opened
    return fh

def is_numlike(obj):
    'return true if *obj* looks like a number'
    try: obj+1
    except: return False
    else: return True
