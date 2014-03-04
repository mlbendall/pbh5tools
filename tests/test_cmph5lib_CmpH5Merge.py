import os
import tempfile
import logging
import unittest
import shutil

from pbcore.io.CmpH5IO import CmpH5Reader
import sys
from pbh5tools.CmpH5Select import cmpH5Select
from pbh5tools.CmpH5Merge import cmpH5Merge

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etc')
_CMP_H5 = os.path.join(_DATA_DIR, 'aligned_reads_ss.cmp.h5')

log = logging.getLogger(__name__)


class _TestBase(unittest.TestCase):

    # Overwrite in subclasses to disable deleting tempdir
    DELETE_TEMP_DIR = True

    @classmethod
    def setUpClass(cls):
        cls.dirName = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'dirName'):
            if os.path.exists(cls.dirName):
                if cls.DELETE_TEMP_DIR:
                    shutil.rmtree(cls.dirName)
                else:
                    log.debug("running in debug mode. Not deleting temp dir {d}".format(d=cls.dirName))

    def _getTempFile(self, suffix=None):
        """Write temp files to central location"""
        f = tempfile.NamedTemporaryFile(dir=self.dirName, suffix=suffix)
        return f.name


def _getNAlignments(fileName):
    """Util func to extract the total number of alignments from a cmp.h5 file

    :param fileName: Path to cmp.h5 file

    :type fileName: str
    :rtype: int
    """
    if not os.path.exists(fileName):
        msg = "Unable to find {f} to get number of aligments".format(f=fileName)
        log.error(msg)
        sys.stderr.write(msg + "\n")
        return 0

    nalignments = 0
    with CmpH5Reader(fileName) as r:
        for alignment in r:
            nalignments += 1

    return nalignments


class TestCmpH5Merge(_TestBase):
    def test_basic(self):
        inputFiles = [_CMP_H5]
        outputFile = self._getTempFile(suffix="_merge_basic.cmp.h5")
        cmpH5Merge(inputFiles, outputFile)

        n = _getNAlignments(outputFile)
        correctNAlignments = 2764
        self.assertEqual(n, correctNAlignments)


class TestMergeException(_TestBase):
    def test_output_file_in_inputs(self):
        inputFiles = [_CMP_H5]
        outputFile = _CMP_H5
        with self.assertRaises(ValueError) as e:
            cmpH5Merge(inputFiles, outputFile)


class TestCmpH5Select(_TestBase):
    def test_basic(self):

        b1 = 'F_42--R_42'
        b2 = 'F_28--R_28'

        where = "(Barcode == '{b1}') | (Barcode == '{b2}')".format(b1=b1, b2=b2)
        outFile = self._getTempFile(suffix="_.cmp.h5")
        # this interface doesn't really make sense. The outFile is required,
        # but it is never used.
        cmpH5Select(_CMP_H5, outFile, groupByStr="Barcode",
                    whereStr=where, outDir=self.dirName)

        #n = _getNAlignments(outFile)
        #self.assertEqual(n, 85)

        nalignmentsTuple = [(b1, 76), (b2, 9)]
        for b, nalignments in nalignmentsTuple:
            p = os.path.join(self.dirName, b + ".cmp.h5")
            self.assertTrue(os.path.exists(p), "Unable to find {b}".format(b=p))
            n = _getNAlignments(p)
            _d = dict(n=n, m=nalignments, p=p)
            msg = "Incorrect alignments (got {n} expected {m} ) from {p}".format(**_d)
            self.assertEqual(n, nalignments, msg)
