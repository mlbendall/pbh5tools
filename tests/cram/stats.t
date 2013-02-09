  $ INH5=`python -c "from pbcore import data ; print data.getCmpH5()['cmph5']"`
  $ CMD="cmph5tools.py stats $INH5"

  $ $CMD --what "ReadLength"
  [(153L,) (204L,) (443L,) (182L,) (174L,) (516L,) (210L,) (674L,) (697L,)
   (159L,) (425L,) (444L,) (163L,) (133L,) (117L,) (472L,) (116L,) (324L,)
   (346L,) (338L,) (318L,) (250L,) (257L,) (257L,) (170L,) (245L,) (309L,)
   (300L,) (326L,) (321L,) (312L,) (329L,) (341L,) (325L,) (334L,) (336L,)
   (277L,) (446L,) (308L,) (324L,) (328L,) (321L,) (132L,) (197L,) (242L,)
   (205L,) (148L,) (542L,) (610L,) (571L,) (188L,) (290L,) (333L,) (244L,)
   (112L,) (294L,) (290L,) (278L,) (111L,) (323L,) (306L,) (295L,) (311L,)
   (292L,) (307L,) (312L,) (316L,) (486L,) (211L,) (195L,) (322L,) (128L,)
   (362L,) (252L,) (674L,) (684L,) (265L,) (329L,) (354L,) (267L,) (254L,)
   (342L,) (404L,) (301L,)]
  $ $CMD --what "Tbl(readlength = ReadLength, accuracy = Accuracy)"
  [(153L, 0.8366013071895425) (204L, 0.7892156862745098)
   (443L, 0.8036117381489842) (182L, 0.8461538461538461)
   (174L, 0.8793103448275862) (516L, 0.8507751937984496)
   (210L, 0.819047619047619) (674L, 0.8338278931750742)
   (697L, 0.8464849354375896) (159L, 0.8050314465408805)
   (425L, 0.8705882352941177) (444L, 0.8243243243243243)
   (163L, 0.803680981595092) (133L, 0.8045112781954887)
   (117L, 0.8717948717948718) (472L, 0.864406779661017)
   (116L, 0.8362068965517242) (324L, 0.8641975308641976)
   (346L, 0.8063583815028902) (338L, 0.834319526627219)
   (318L, 0.8018867924528301) (250L, 0.8) (257L, 0.8482490272373541)
   (257L, 0.8365758754863813) (170L, 0.8235294117647058) (245L, 0.8)
   (309L, 0.889967637540453) (300L, 0.8233333333333334)
   (326L, 0.8558282208588956) (321L, 0.822429906542056)
   (312L, 0.8717948717948718) (329L, 0.851063829787234)
   (341L, 0.8592375366568915) (325L, 0.8953846153846154)
   (334L, 0.7964071856287425) (336L, 0.8511904761904762)
   (277L, 0.8916967509025271) (446L, 0.8116591928251121)
   (308L, 0.8441558441558441) (324L, 0.8611111111111112)
   (328L, 0.8567073170731707) (321L, 0.8629283489096573)
   (132L, 0.8787878787878788) (197L, 0.8426395939086294)
   (242L, 0.7975206611570248) (205L, 0.8682926829268293)
   (148L, 0.8378378378378378) (542L, 0.8247232472324724)
   (610L, 0.819672131147541) (571L, 0.8458844133099825)
   (188L, 0.8404255319148937) (290L, 0.8379310344827586)
   (333L, 0.8078078078078078) (244L, 0.8114754098360656) (112L, 0.8125)
   (294L, 0.8129251700680272) (290L, 0.8034482758620689)
   (278L, 0.8705035971223022) (111L, 0.7927927927927928)
   (323L, 0.7925696594427245) (306L, 0.8300653594771241)
   (295L, 0.8033898305084746) (311L, 0.8327974276527331)
   (292L, 0.8253424657534246) (307L, 0.8534201954397393)
   (312L, 0.8269230769230769) (316L, 0.8259493670886076)
   (486L, 0.8004115226337448) (211L, 0.8341232227488151)
   (195L, 0.8564102564102565) (322L, 0.84472049689441) (128L, 0.796875)
   (362L, 0.8591160220994475) (252L, 0.8888888888888888)
   (674L, 0.8249258160237389) (684L, 0.814327485380117) (265L, 0.8)
   (329L, 0.8449848024316109) (354L, 0.8389830508474576)
   (267L, 0.8352059925093633) (254L, 0.8228346456692913)
   (342L, 0.8742690058479532) (404L, 0.8242574257425743)
   (301L, 0.8372093023255813)]
  $ $CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))"
  [(481.80000000000007, 0.8349851724711348)]
  $ $CMD --what "Movie"
  [('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0',)]
  $ $CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))" --where "Movie == 'm110818_075520_42141_c100129202555500000315043109121112_s1_p0'"
  [(547.8000000000001, 0.8366615137876647)]
  $ $CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))" --groupBy "Movie"
  [ ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0', 445.20000000000005, 0.8335323433301427)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0', 547.8000000000001, 0.8366615137876647)]
  $ $CMD --what "Tbl(mrl = Q(ReadLength, 90), macc = Mean(Accuracy))" --groupBy "Movie * Reference"
  [ ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 547.8000000000001, 0.8366615137876647)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 445.20000000000005, 0.8335323433301427)]
  $ $CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD))" --groupBy "Movie * Reference"
  [ ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 153L, 0.1633986928104575, 0.2820907293581495)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 204L, 0.21078431372549022, 0.2854241389854282)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 443L, 0.19638826185101577, 0.20234707731156532)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 516L, 0.14922480620155043, 0.1786040372626726)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 674L, 0.16617210682492578, 0.36791190761486925)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 697L, 0.15351506456241037, 0.3275935475419207)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 116L, 0.1637931034482758, 0.5321825948254816)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 324L, 0.1358024691358024, 0.7528376167203173)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 346L, 0.1936416184971098, 0.9670881150085802)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 338L, 0.16568047337278102, 0.3990126389723558)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 318L, 0.19811320754716988, 0.9977755756498133)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 250L, 0.19999999999999996, 0.18858604431152343)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 257L, 0.15175097276264593, 0.2571198875338187)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 257L, 0.16342412451361865, 0.16793723792881354)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 309L, 0.11003236245954695, 0.27438969288057496)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 300L, 0.17666666666666664, 0.19662156422932942)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 326L, 0.14417177914110435, 0.27055127196516726)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 321L, 0.17757009345794394, 0.2843191794517256)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 312L, 0.1282051282051282, 0.20243524893736228)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 329L, 0.14893617021276595, 0.2095231169262918)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 341L, 0.1407624633431085, 0.3446324591762509)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 325L, 0.10461538461538455, 0.23048135610727163)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 334L, 0.20359281437125754, 0.41417045364836735)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 336L, 0.14880952380952384, 0.5978556587582543)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 542L, 0.17527675276752763, 0.17899069135039494)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 610L, 0.180327868852459, 0.35873142930327867)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 571L, 0.15411558669001746, 0.1795905759580916)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 188L, 0.15957446808510634, 0.21226880905476023)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 290L, 0.16206896551724137, 0.1356317191288389)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 333L, 0.1921921921921922, 0.13405358254372537)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 211L, 0.16587677725118488, 0.29023616121843526)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 195L, 0.14358974358974352, 0.3476913843399439)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 322L, 0.15527950310559002, 0.16571375449992115)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 128L, 0.203125, 0.2884366810321808)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 329L, 0.1550151975683891, 0.1798575728859945)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 354L, 0.1610169491525424, 0.24026295290154925)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 267L, 0.16479400749063666, 0.15190961744901393)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 254L, 0.17716535433070868, 0.2518628488375446)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 342L, 0.1257309941520468, 0.1839370504457351)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 182L, 0.15384615384615385, 0.3418304108001374)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 174L, 0.12068965517241381, 0.19731743034275098)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 210L, 0.18095238095238098, 0.25149134681338353)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 159L, 0.19496855345911945, 0.1375258463733601)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 425L, 0.12941176470588234, 0.32119137034696693)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 444L, 0.17567567567567566, 0.22023953618230047)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 163L, 0.19631901840490795, 0.14388508006838932)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 133L, 0.19548872180451127, 0.21814472513987607)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 117L, 0.1282051282051282, 0.3050703717093182)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 472L, 0.13559322033898302, 0.24692016536906614)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 170L, 0.17647058823529416, 0.30258739695829506)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 245L, 0.19999999999999996, 0.3708289944395727)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 277L, 0.10830324909747291, 0.2643554632414119)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 446L, 0.18834080717488788, 0.20520120458218014)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 308L, 0.1558441558441559, 0.7056262028681768)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 324L, 0.13888888888888884, 0.19053440329469282)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 328L, 0.14329268292682928, 0.31304792078529914)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 321L, 0.1370716510903427, 0.19430884245400118)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 132L, 0.12121212121212122, 0.49474612149325287)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 197L, 0.15736040609137059, 0.22348494941207964)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 242L, 0.2024793388429752, 0.36997150389616157)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 205L, 0.13170731707317074, 0.20487739749071074)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 148L, 0.16216216216216217, 0.22468407089645798)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 244L, 0.1885245901639344, 0.22027254886314518)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 112L, 0.1875, 0.7607122148786273)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 294L, 0.18707482993197277, 0.1851241702125186)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 290L, 0.1965517241379311, 0.45264261179956894)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 278L, 0.1294964028776978, 0.23846443780034565)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 111L, 0.2072072072072072, 0.23026969840934686)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 323L, 0.2074303405572755, 0.44144352301724554)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 306L, 0.16993464052287588, 0.464181538500817)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 295L, 0.19661016949152543, 0.19642882266287076)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 311L, 0.16720257234726688, 0.5227853952880074)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 292L, 0.17465753424657537, 0.2140632786162912)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 307L, 0.14657980456026065, 0.23444013564516744)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 312L, 0.17307692307692313, 0.31422984294402295)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 316L, 0.17405063291139244, 0.2286912700797938)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 486L, 0.19958847736625518, 0.3521252541875643)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 362L, 0.14088397790055252, 0.18961260463651372)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 252L, 0.11111111111111116, 0.9217964051261781)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 674L, 0.17507418397626107, 0.27145338199966385)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 684L, 0.185672514619883, 0.18452184799818966)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 265L, 0.19999999999999996, 0.28020025289283607)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 404L, 0.17574257425742568, 0.28204549657236233)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 301L, 0.16279069767441867, 0.20908013530743874)]
  $ $CMD --what "Tbl(readlength = ReadLength, errorRate = 1 - Accuracy, ipd = Mean(IPD), holeNumber = HoleNumber)" --groupBy "Movie * Reference" --where "HoleNumber != 9"
  [ ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 153L, 0.1633986928104575, 0.2820907293581495, 2003L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 204L, 0.21078431372549022, 0.2854241389854282, 2003L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 443L, 0.19638826185101577, 0.20234707731156532, 2003L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 116L, 0.1637931034482758, 0.5321825948254816, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 324L, 0.1358024691358024, 0.7528376167203173, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 346L, 0.1936416184971098, 0.9670881150085802, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 338L, 0.16568047337278102, 0.3990126389723558, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 318L, 0.19811320754716988, 0.9977755756498133, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 250L, 0.19999999999999996, 0.18858604431152343, 2007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 257L, 0.15175097276264593, 0.2571198875338187, 2007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 257L, 0.16342412451361865, 0.16793723792881354, 2007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 309L, 0.11003236245954695, 0.27438969288057496, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 300L, 0.17666666666666664, 0.19662156422932942, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 326L, 0.14417177914110435, 0.27055127196516726, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 321L, 0.17757009345794394, 0.2843191794517256, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 312L, 0.1282051282051282, 0.20243524893736228, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 329L, 0.14893617021276595, 0.2095231169262918, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 341L, 0.1407624633431085, 0.3446324591762509, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 325L, 0.10461538461538455, 0.23048135610727163, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 334L, 0.20359281437125754, 0.41417045364836735, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 336L, 0.14880952380952384, 0.5978556587582543, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 542L, 0.17527675276752763, 0.17899069135039494, 1007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 610L, 0.180327868852459, 0.35873142930327867, 1007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 571L, 0.15411558669001746, 0.1795905759580916, 1007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 188L, 0.15957446808510634, 0.21226880905476023, 1000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 290L, 0.16206896551724137, 0.1356317191288389, 1000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 333L, 0.1921921921921922, 0.13405358254372537, 1000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 211L, 0.16587677725118488, 0.29023616121843526, 4006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 195L, 0.14358974358974352, 0.3476913843399439, 4006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 322L, 0.15527950310559002, 0.16571375449992115, 1006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 128L, 0.203125, 0.2884366810321808, 1006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 329L, 0.1550151975683891, 0.1798575728859945, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 354L, 0.1610169491525424, 0.24026295290154925, 2008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 267L, 0.16479400749063666, 0.15190961744901393, 4009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 254L, 0.17716535433070868, 0.2518628488375446, 2001L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s1_p0:lambda_NEB3011', 342L, 0.1257309941520468, 0.1839370504457351, 2001L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 182L, 0.15384615384615385, 0.3418304108001374, 8L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 174L, 0.12068965517241381, 0.19731743034275098, 8L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 210L, 0.18095238095238098, 0.25149134681338353, 2000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 159L, 0.19496855345911945, 0.1375258463733601, 2000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 163L, 0.19631901840490795, 0.14388508006838932, 1008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 133L, 0.19548872180451127, 0.21814472513987607, 1008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 117L, 0.1282051282051282, 0.3050703717093182, 1002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 472L, 0.13559322033898302, 0.24692016536906614, 1002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 170L, 0.17647058823529416, 0.30258739695829506, 2009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 245L, 0.19999999999999996, 0.3708289944395727, 2009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 277L, 0.10830324909747291, 0.2643554632414119, 2004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 446L, 0.18834080717488788, 0.20520120458218014, 4007L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 308L, 0.1558441558441559, 0.7056262028681768, 2004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 324L, 0.13888888888888884, 0.19053440329469282, 2004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 328L, 0.14329268292682928, 0.31304792078529914, 2004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 321L, 0.1370716510903427, 0.19430884245400118, 2004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 132L, 0.12121212121212122, 0.49474612149325287, 2002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 197L, 0.15736040609137059, 0.22348494941207964, 1004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 242L, 0.2024793388429752, 0.36997150389616157, 1004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 244L, 0.1885245901639344, 0.22027254886314518, 1009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 112L, 0.1875, 0.7607122148786273, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 294L, 0.18707482993197277, 0.1851241702125186, 1009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 290L, 0.1965517241379311, 0.45264261179956894, 1009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 278L, 0.1294964028776978, 0.23846443780034565, 1009L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 111L, 0.2072072072072072, 0.23026969840934686, 2006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 323L, 0.2074303405572755, 0.44144352301724554, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 306L, 0.16993464052287588, 0.464181538500817, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 295L, 0.19661016949152543, 0.19642882266287076, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 311L, 0.16720257234726688, 0.5227853952880074, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 292L, 0.17465753424657537, 0.2140632786162912, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 307L, 0.14657980456026065, 0.23444013564516744, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 312L, 0.17307692307692313, 0.31422984294402295, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 316L, 0.17405063291139244, 0.2286912700797938, 3002L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 486L, 0.19958847736625518, 0.3521252541875643, 2006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 362L, 0.14088397790055252, 0.18961260463651372, 4004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 252L, 0.11111111111111116, 0.9217964051261781, 4004L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 674L, 0.17507418397626107, 0.27145338199966385, 1000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 684L, 0.185672514619883, 0.18452184799818966, 1000L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 265L, 0.19999999999999996, 0.28020025289283607, 3006L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 404L, 0.17574257425742568, 0.28204549657236233, 3008L)
   ('m110818_075520_42141_c100129202555500000315043109121112_s2_p0:lambda_NEB3011', 301L, 0.16279069767441867, 0.20908013530743874, 3008L)]
  $ SCMD="cmph5tools.py select $INH5"
  $ $SCMD --where "(ReadLength > 100) & (Accuracy < .8)" --groupBy "Movie"
  $ cmph5tools.py summarize *.cmp.h5
  ----------------------------------------
  filename: m110818_075520_42141_c100129202555500000315043109121112_s1_p0.cmp.h5
  version:  1.2.0.SF
  n reads:  3
  n refs:   1
  n movies: 1
  n bases:  666
  avg rl:   222
  avg acc:  0.7942
  ----------------------------------------
  filename: m110818_075520_42141_c100129202555500000315043109121112_s2_p0.cmp.h5
  version:  1.2.0.SF
  n reads:  3
  n refs:   1
  n movies: 1
  n bases:  676
  avg rl:   225
  avg acc:  0.7943
  $ $SCMD --idx 1 2 3 4 --outFile 1234.cmp.h5
  $ cmph5tools.py summarize 1234.cmp.h5
  ----------------------------------------
  filename: 1234.cmp.h5
  version:  1.2.0.SF
  n reads:  4
  n refs:   1
  n movies: 2
  n bases:  1267
  avg rl:   317
  avg acc:  0.8391