"""

Numerical python functions written for compatability with MATLAB
commands with the same names.

record array helper functions
-------------------------------

A collection of helper methods for numpyrecord arrays

:meth:`rec2txt`
    pretty print a record array

:meth:`rec2csv`
    store record array in CSV file

"""

import csv, os
import cbook
import numpy as np

def rec2csv(r, fname, delimiter=',', formatd=None, missing='',
            missingd=None, withheader=True):
    """
    Save the data from numpy recarray *r* into a
    comma-/space-/tab-delimited file.  The record array dtype names
    will be used for column headers.

    *fname*: can be a filename or a file handle.  Support for gzipped
      files is automatic, if the filename ends in '.gz'

    *withheader*: if withheader is False, do not write the attribute
      names in the first row

    for formatd type FormatFloat, we override the precision to store
    full precision floats in the CSV file


    .. seealso::

        :func:`csv2rec`
            For information about *missing* and *missingd*, which can
            be used to fill in masked values into your CSV file.
    """

    if missingd is None:
        missingd = dict()

    def with_mask(func):
        def newfunc(val, mask, mval):
            if mask:
                return mval
            else:
                return func(val)
        return newfunc

    if r.ndim != 1:
        raise ValueError('rec2csv only operates on 1 dimensional recarrays')

    formatd = get_formatd(r, formatd)
    funcs = []
    for i, name in enumerate(r.dtype.names):
        funcs.append(with_mask(csvformat_factory(formatd[name]).tostr))

    fh, opened = cbook.to_filehandle(fname, 'wb', return_opened=True)
    writer = csv.writer(fh, delimiter=delimiter)
    header = r.dtype.names
    if withheader:
        writer.writerow(header)

    # Our list of specials for missing values
    mvals = []
    for name in header:
        mvals.append(missingd.get(name, missing))

    ismasked = False
    if len(r):
        row = r[0]
        ismasked = hasattr(row, '_fieldmask')

    for row in r:
        if ismasked:
            row, rowmask = row.item(), row._fieldmask.item()
        else:
            rowmask = [False] * len(row)
        writer.writerow([func(val, mask, mval) for func, val, mask, mval
                         in zip(funcs, row, rowmask, mvals)])
    if opened:
        fh.close()

def rec2txt(r, header=None, padding=3, precision=3, fields=None):
    """
    Returns a textual representation of a record array.

    *r*: numpy recarray

    *header*: list of column headers

    *padding*: space between each column

    *precision*: number of decimal places to use for floats.
        Set to an integer to apply to all floats.  Set to a
        list of integers to apply precision individually.
        Precision for non-floats is simply ignored.

    *fields* : if not None, a list of field names to print.  fields
    can be a list of strings like ['field1', 'field2'] or a single
    comma separated string like 'field1,field2'

    Example::

      precision=[0,2,3]

    Output::

      ID    Price   Return
      ABC   12.54    0.234
      XYZ    6.32   -0.076
    """

    if fields is not None:
        r = rec_keep_fields(r, fields)

    if cbook.is_numlike(precision):
        precision = [precision]*len(r.dtype)

    def get_type(item,atype=int):
        tdict = {None:int, int:float, float:str}
        try: atype(str(item))
        except: return get_type(item,tdict[atype])
        return atype

    def get_justify(colname, column, precision):
        ntype = type(column[0])

        if ntype==np.str or ntype==np.str_ or ntype==np.string0 or ntype==np.string_:
            length = max(len(colname),column.itemsize)
            return 0, length+padding, "%s" # left justify

        if ntype==np.int or ntype==np.int16 or ntype==np.int32 or ntype==np.int64 or ntype==np.int8 or ntype==np.int_:
            length = max(len(colname),np.max(map(len,map(str,column))))
            return 1, length+padding, "%d" # right justify

        # JDH: my powerbook does not have np.float96 using np 1.3.0
        """
        In [2]: np.__version__
        Out[2]: '1.3.0.dev5948'

        In [3]: !uname -a
        Darwin Macintosh-5.local 9.4.0 Darwin Kernel Version 9.4.0: Mon Jun  9 19:30:53 PDT 2008; root:xnu-1228.5.20~1/RELEASE_I386 i386 i386

        In [4]: np.float96
        ---------------------------------------------------------------------------
        AttributeError                            Traceback (most recent call la
        """
        if ntype==np.float or ntype==np.float32 or ntype==np.float64 or (hasattr(np, 'float96') and (ntype==np.float96)) or ntype==np.float_:
            fmt = "%." + str(precision) + "f"
            length = max(len(colname),np.max(map(len,map(lambda x:fmt%x,column))))
            return 1, length+padding, fmt   # right justify

        return 0, max(len(colname),np.max(map(len,map(str,column))))+padding, "%s"

    if header is None:
        header = r.dtype.names

    justify_pad_prec = [get_justify(header[i],r.__getitem__(colname),precision[i]) for i, colname in enumerate(r.dtype.names)]

    justify_pad_prec_spacer = []
    for i in range(len(justify_pad_prec)):
        just,pad,prec = justify_pad_prec[i]
        if i == 0:
            justify_pad_prec_spacer.append((just,pad,prec,0))
        else:
            pjust,ppad,pprec = justify_pad_prec[i-1]
            if pjust == 0 and just == 1:
                justify_pad_prec_spacer.append((just,pad-padding,prec,0))
            elif pjust == 1 and just == 0:
                justify_pad_prec_spacer.append((just,pad,prec,padding))
            else:
                justify_pad_prec_spacer.append((just,pad,prec,0))

    def format(item, just_pad_prec_spacer):
        just, pad, prec, spacer = just_pad_prec_spacer
        if just == 0:
            return spacer*' ' + str(item).ljust(pad)
        else:
            if get_type(item) == float:
                item = (prec%float(item))
            elif get_type(item) == int:
                item = (prec%int(item))

            return item.rjust(pad)

    textl = []
    textl.append(''.join([format(colitem,justify_pad_prec_spacer[j]) for j, colitem in enumerate(header)]))
    for i, row in enumerate(r):
        textl.append(''.join([format(colitem,justify_pad_prec_spacer[j]) for j, colitem in enumerate(row)]))
        if i==0:
            textl[0] = textl[0].rstrip()

    text = os.linesep.join(textl)
    return text

