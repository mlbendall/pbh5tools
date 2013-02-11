
INH5=`python -c "from pbcore import data ; print data.getCmpH5()['cmph5']"`
CMD="cmph5tools.py stats $INH5"

$CMD --what "ReadLength"
$CMD --what "Tbl(readlength = ReadLength, accuracy = Accuracy)"
$CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))"
$CMD --what "Movie"
$CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))" \
    --where "Movie == 'm110818_075520_42141_c100129202555500000315043109121112_s1_p0'"

$CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))" \
    --groupBy "Movie"

$CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))" \
    --groupBy "Movie * Reference"

$CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD))" \
    --groupBy "Movie * Reference"

$CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD), holeNumber = HoleNumber)" \
    --groupBy "Movie * Reference" --where "HoleNumber != 9"

## show select functionality.
SCMD="cmph5tools.py select $INH5"

$SCMD --where "(ReadLength > 100) & (Accuracy < .8)" --groupBy "Movie"

cmph5tools.py summarize *.cmp.h5

$SCMD --idx 1 2 3 4 --outFile 1234.cmp.h5

cmph5tools.py summarize 1234.cmp.h5
