#################################################################################
# Copyright (c) 2011-2013, Pacific Biosciences of California, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of Pacific Biosciences nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE.  THIS SOFTWARE IS PROVIDED BY PACIFIC BIOSCIENCES AND ITS
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL PACIFIC BIOSCIENCES OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#################################################################################

import os
import sys
import shutil
import datetime
import logging
import tempfile

import h5py as H5
import numpy as NP

def deleteAttrIfExists(ds, nm):
    if nm in ds.attrs:
        del ds.attrs[nm]

def deleteIfExists(ds, nm):
    if nm in ds:
        del ds[nm]

def copyAttributes(inDs, outDs):
    for k in inDs.attrs.keys():
        logging.debug("copying attribute: %s" % k)
        elt = inDs.attrs[k]
        if isinstance(elt, basestring):
            # h5py wants to simplify things down, so I think that this
            # is a possibility.
            # preserve numpy string type if possible
            # the h5.special_dtype defined below will lose dtype.
            newDtype = elt.dtype if hasattr(elt,'dtype') else H5.special_dtype(vlen = str)
        elif elt.dtype == 'object':
            # this has to do with a numpy problem.
            newDtype = H5.special_dtype(vlen = str)
        else:
            newDtype = elt.dtype
            
        outDs.attrs.create(k, inDs.attrs[k], dtype = newDtype)

def copyDataset(absDsName, inCmp, outCmp, selection = None,
                copyAttrs = True):

    inDs = inCmp[absDsName]
    if selection is not None:
        if len(inDs.shape) <= 1:
            ndta = inDs.value[selection]
        else:
            ndta = inDs.value[selection,:]
    else:
        ndta = inDs.value

    outDs = outCmp.create_dataset(absDsName, data = ndta,
                                  dtype = inDs.dtype, chunks = True)
    if copyAttrs:
        copyAttributes(inDs, outDs)

    return outDs

