import gurobipy as gp
from gurobipy import GRB
import csv
import numpy as np

#  It is assumed we can parse a csv file into an array of N rows and M columns
# table = [[25, 10, 5],
#          [5, 10, 25],
#          [10, 5, 5]]
# table = [[2, 3, 4, 5],
#          [4, 7, 2, 8],
#          [8, 5, 3, 3],
#          [2, 5, 9, 7],
#          [9, 3, 7, 4]]
# table = [[9, 5, 6, 5, 11],
#          [4, 4, 4, 16, 8],
#          [6, 14, 9, 4, 3],
#          [2, 3, 11, 10, 10],
#          [7, 3, 3, 18, 5]]
# table = [[10, 2, 12, 14, 4, 6],
#          [3, 5, 1, 15, 19, 9],
#          [8, 18, 1, 14, 17, 3],
#          [13, 4, 14, 10, 2, 3],
#          [8, 16, 20, 4, 1, 19],
#          [15, 11, 7, 3, 17, 10]]
# table = [[50, 5, 2, 5, 2, 5],
#          [5, 2, 5, 2, 5, 50],
#          [50, 5, 2, 5, 2, 5],
#          [5, 2, 5, 2, 5, 50],
#          [50, 5, 2, 5, 2, 5],
#          [5, 2, 5, 2, 5, 50]]
# 13x13
# table = [[0.5979020943511684, 0.8100886000051254, 0.41020645215348217, 0.02436385433173427, 0.1559207043785129, 0.7510264949948375, 0.2642317366518374, 0.7843500257734056, 0.36922467841278284, 0.7969845284254878, 0.15722759635281247, 0.4393788544245367, 0.39650088343358825], [0.09703535041015021, 0.765952087310373, 0.2419703386712192, 0.20940141480946228, 0.31127217576202004, 0.9007219056920596, 0.7827270122608189, 0.6884577935409274, 0.8327868237448497, 0.036089436040636524, 0.4327030453283198, 0.8340229594293123, 0.8179278408778782], [0.8569010103631092, 0.3408898013312365, 0.9241184363145253, 0.9623120563518848, 0.16312052712962288, 0.6650659078657719, 0.013242445436777994, 0.5088354624118233, 0.8876574484246532, 0.35488033117872386, 0.8887154024850067, 0.09866623981837264, 0.5929303473074844], [0.12354781340434962, 0.9788578859468582, 0.7669655691808615, 0.5314487384911731, 0.3064731346991597, 0.10890398026175097, 0.9051554354302866, 0.09319071444418425, 0.2535819811956508, 0.3873675879470815, 0.22860278987998894, 0.47163426379846385, 0.12640330390468646], [0.9344262696632145, 0.3760760487913971, 0.9275357157758993, 0.033588655323051775, 0.6699940620209331, 0.8463339882211426, 0.6368963730466892, 0.4402284755223459, 0.9062237500443728, 0.2881748010609727, 0.29645849481496145, 0.05502003689729007, 0.704836070689555], [0.3369902725042868, 0.21033296240214006, 0.28208653640517856, 0.012012370814369122, 0.7206900788832802, 0.4430075007883064, 0.49485244375531534, 0.5403728048384142, 0.12790137396322587, 0.8302998844609827, 0.7916796488344494, 0.4553165582095332, 0.25207476825702313], [0.7692074468350604, 0.3254491794549639, 0.7220901391354575, 0.751479181052505, 0.7118492857258443, 0.7165861393405308, 0.5815333311353995, 0.3247654673503675, 0.607564086137924, 0.9018832678472394, 0.4410598654958827, 0.4288731715056424, 0.4090637314322938], [0.3850397671397101, 0.37693662555893837, 0.24883997841828775, 0.8041977300808109, 0.3891270444798035, 0.7746050933214678, 0.6604779274842993, 0.7141863390481433, 0.6174353075947604, 0.8038903702277201, 0.6227765916617436, 0.06279317723795952, 0.1188226596556381], [0.5465152048677339, 0.5511614840352879, 0.10641840056012697, 0.19928772684699403, 0.2385052350395238, 0.9746311648563374, 0.6042348170148488, 0.3623055876637987, 0.27095908045523265, 0.048734594621916094, 0.8685092978550576, 0.3994718807250711, 0.16543563501151326], [0.3985390828666099, 0.2143788894542299, 0.011733320565643246, 0.9823685411507334, 0.22219993820728312, 0.8884612329232018, 0.31262755972846235, 0.14694514365695655, 0.7168816784358872, 0.4915849639049066, 0.3586194188750701, 0.5329921401131871, 0.7682426977444421], [0.8822595931282258, 0.15174577495133856, 0.4002295022153183, 0.5749757116088159, 0.820709690009159, 0.729624501258963, 0.9607433040740194, 0.5284186462042729, 0.01125229180105225, 0.3356317208788069, 0.2748237878700175, 0.1753126569960468, 0.41450991366711076], [0.30069716658451284, 0.9750272672054728, 0.4455093388022723, 0.735266048507276, 0.5305994380882669, 0.7045832754557361, 0.5944470616524046, 0.8666537662326412, 0.6557196089181612, 0.7114771122951512, 0.7864627070237941, 0.0553222461024695, 0.9154668672215386], [0.3829871078619096, 0.7479330165240807, 0.7028740850487812, 0.6161808841757749, 0.8314888672125755, 0.5366267621422833, 0.8878002825909155, 0.8651443583069858, 0.35157020509406345, 0.5329804874381868, 0.9324040794781742, 0.0975313974642974, 0.13021839188229933]]
# 14x14
# table = [[0.3340856919367742, 0.5084062083647538, 0.02813499460395874, 0.6038350087243113, 0.5667251632996448, 0.09972676655058643, 0.10411717506185614, 0.3065819818396931, 0.49471912619729375, 0.2762055177123611, 0.9352759322581882, 0.9195647878583438, 0.4901801943920664, 0.2788652632652511], [0.4703412431976549, 0.46419218467331935, 0.8696262245278679, 0.24942131967294567, 0.6752112240137033, 0.7849369944818292, 0.4360425005421382, 0.10578913780181498, 0.8983883166589289, 0.18489546430093917, 0.03228829477402462, 0.42749929788142427, 0.35842708834693726, 0.8914215703433356], [0.11432232091401895, 0.5751725412896933, 0.4464999606642164, 0.8920398016014423, 0.5637693699820404, 0.6516231165495769, 0.5967807409777917, 0.0720726102661704, 0.691909119310741, 0.5025712831518115, 0.8695546947610514, 0.7715988676337417, 0.5267476066461815, 0.6325942443720965], [0.5372693620303574, 0.5447391266296926, 0.4521539723828898, 0.2809437735773267, 0.46604593465681443, 0.7268924034465332, 0.2859009570154061, 0.0035356520693116122, 0.344312839068064, 0.24597167439295742, 0.04119780596045053, 0.8240058844411499, 0.8455432715191594, 0.024609328382884987], [0.3710568374369523, 0.32016556479690883, 0.5930790938929064, 0.6026372012155562, 0.19235353234682895, 0.8862225936411763, 0.29835933099020917, 0.6104827786499101, 0.8654993329279431, 0.473295965301453, 0.3875118550771295, 0.10823422560697038, 0.08917528046617373, 0.7049215440567572], [0.34287395842267776, 0.480226234716974, 0.3104009246047549, 0.8837685324899031, 0.15136823516464548, 0.5375709646582466, 0.8088411257424148, 0.07832973143389488, 0.23563102865169827, 0.798878941406321, 0.7258208302605732, 0.6389744048488883, 0.4767981820552226, 0.34897005481254706], [0.8611879527717314, 0.16082614557801955, 0.3871884928627922, 0.40783739734387414, 0.19147083443952717, 0.23862004562324823, 0.8823174175720656, 0.9574412225420063, 0.08786828850671691, 0.11333776915711902, 0.7162471003282946, 0.9693423690422953, 0.13109561291013927, 0.0348312511942368], [0.9470609671770928, 0.47191522068015324, 0.8264292627643961, 0.4062871830616277, 0.6472729054744124, 0.28137421766978254, 0.08976700316149178, 0.4913843621995715, 0.5066012694959477, 0.30407009857037104, 0.6642245062321439, 0.6566327393994957, 0.5091090001613198, 0.30241230351767523], [0.09378431418074351, 0.20941679961170023, 0.6963990285799871, 0.7936200891698342, 0.3570850548619384, 0.694331810950938, 0.8338712323529461, 0.17886528665766555, 0.34034048469911815, 0.9476022026893998, 0.9639735967281214, 0.6738721335285205, 0.910647287361914, 0.1548938666311347], [0.20596717434791112, 0.5625671226155775, 0.009726059775467921, 0.313575679819894, 0.3805565889135065, 0.9030928360605286, 0.2420328620416038, 0.1890456214714944, 0.49848593232729344, 0.7130502609127467, 0.978338471506251, 0.8014213579277382, 0.5231947351259016, 0.8119454631480958], [0.2387764139460966, 0.18961637692440003, 0.9581056136186643, 0.16888817693930847, 0.9541314387386886, 0.880367341430266, 0.777083292053797, 0.533064757916379, 0.8424364762410399, 0.8971735647328521, 0.15122016263043103, 0.022705656599846136, 0.47883246797134293, 0.5732566964562846], [0.9204471165485818, 0.2272359074181608, 0.4299558429556454, 0.9347197251694025, 0.1138697594145307, 0.056779195934974935, 0.6966840583573485, 0.45997625938263986, 0.2659215800083592, 0.24707524067812403, 0.41048545104686474, 0.5434231694815232, 0.8678449720547485, 0.1097260797740417], [0.532153059355472, 0.06542555551874707, 0.38675147297962764, 0.9521277677490785, 0.1821200612285062, 0.6707895767543347, 0.7119366170777484, 0.13691925856356846, 0.43312965650900326, 0.5559162240716413, 0.09347964618002214, 0.49549473753778417, 0.16333124286632128, 0.5285917222678128], [0.1955771045975696, 0.4196086739278827, 0.24270646043406952, 0.2667727443951947, 0.9890589716341497, 0.7411406678159893, 0.056489199613576124, 0.19450919575745607, 0.5287245075788504, 0.7403696557286561, 0.6242576549733742, 0.5527527454445618, 0.9784313271034333, 0.7281432800183616]]
# 15x15
# table = [[0.05407582432245739, 0.3902571775354329, 0.1807399627371873, 0.572152733463377, 0.6300477418425424, 0.949295808383623, 0.27368319917006523, 0.9469356252880858, 0.5276850339015879, 0.13434699823109808, 0.08088908044347709, 0.8899092786464547, 0.5401103948470608, 0.02636233305583724, 0.06237390887781269], [0.38499633198132055, 0.3419812420657693, 0.3302922237191409, 0.7986740288371954, 0.9880192673316313, 0.5420436853634482, 0.24191493777034745, 0.2897957901681939, 0.7032084828983878, 0.20435189347779448, 0.11233819534155587, 0.5830880738565112, 0.3697723855931859, 0.11075464115463918, 0.48884264084636087], [0.5509169239777091, 0.07337219906429804, 0.2521466540502255, 0.8360373494443603, 0.6115640021753623, 0.2725605950127038, 0.2686543252598621, 0.9146190233575724, 0.5355413421134306, 0.8246277168458725, 0.3266178020501801, 0.5410785303763856, 0.25837280274118013, 0.12549476093235945, 0.590002508518379], [0.7854852858597708, 0.12468707279145419, 0.6449062764314221, 0.010656158773873048, 0.6451887308026036, 0.5846076902138592, 0.3944477651880707, 0.860556338400106, 0.6507839073530557, 0.5607000249372985, 0.0167192181394894, 0.48226621767765276, 0.5230494491114566, 0.5771815972659514, 0.7414516305348183], [0.2542151700290147, 0.09215873380216444, 0.9881273762109263, 0.7838016561583423, 0.360756531081889, 0.34762079017107106, 0.4021180587562504, 0.8235720434471652, 0.809850361335605, 0.31286540645668925, 0.8565937916411714, 0.5215527432274033, 0.7027091487085554, 0.8197222840412033, 0.31400800531307604], [0.9955280683983927, 0.24871089395891632, 0.2065562018475362, 0.9421928480812864, 0.5655297735428387, 0.5299438755125857, 0.7834281435575007, 0.8935165856446841, 0.1230799104809529, 0.6339113230348005, 0.971350279015133, 0.7135027775710614, 0.3568013819465008, 0.7848058626141222, 0.6795508682633863], [0.6011084982169224, 0.8128962095914077, 0.7437927485207189, 0.4623515927097597, 0.762740157781281, 0.029131121821624806, 0.41279071032223436, 0.13487711515771983, 0.1545138041664592, 0.19019602493204235, 0.6736018258001985, 0.2756801162377658, 0.5461502685630487, 0.7195147353845224, 0.9335155685747378], [0.7584035977352103, 0.6973596140750984, 0.7617765459334488, 0.9237637398227988, 0.1528156542728295, 0.5577789820637101, 0.3168878184065361, 0.44527092488687514, 0.31479659126800397, 0.9092275982110937, 0.24770408085024276, 0.33836658168274514, 0.882671167668768, 0.23260125771542672, 0.5000876446352756], [0.9009302487919597, 0.5648200098853673, 0.9206042130361132, 0.9044089720033713, 0.1524510020766029, 0.8314746438743019, 0.9661996123412531, 0.0542728774767004, 0.3776049928529891, 0.47594707655896173, 0.9399308506135374, 0.10550745678711926, 0.13038534456384498, 0.20414436930768431, 0.6988204177358142], [0.30318711924389363, 0.9709879715929356, 0.7537804899283481, 0.7709140726858512, 0.2198259167979476, 0.4153069473467671, 0.6200894969803632, 0.750134016105157, 0.8571532911965234, 0.17188519087593068, 0.5470515283825026, 0.1049459945877248, 0.8129259528405646, 0.8323722844289214, 0.7642518434018489], [0.3487153368370386, 0.6891128649540867, 0.6863715979872058, 0.8276006951877959, 0.966185633358081, 0.7913647898449283, 0.7529893005735939, 0.5908219369690823, 0.822885227734132, 0.9242770424598031, 0.8317691488090926, 0.5547628693993834, 0.021418955624733504, 0.4757902575041222, 0.9187184929063946], [0.5370653761360726, 0.323292087552993, 0.48945902150464826, 0.3992046573899213, 0.9018117948123693, 0.6643384373662624, 0.3848706205707684, 0.49171675551986427, 0.08015656979839059, 0.1303150217279485, 0.43811029879643115, 0.1281751931546733, 0.752395673676971, 0.9496379209589382, 0.5246034954055314], [0.6123804515680263, 0.32817835389530925, 0.20679460724724363, 0.026455681441213907, 0.2604102920935688, 0.8990979612355037, 0.2091377262270402, 0.8028537863646377, 0.4227982000869035, 0.8011140641911412, 0.22610718517599282, 0.9389658554255084, 0.03691471955781089, 0.4877137645150029, 0.06055996343151904], [0.7342704620088695, 0.6429841653198503, 0.14101909728333517, 0.48608259427613965, 0.864654867644214, 0.8305153447752412, 0.32298924452447364, 0.9330886526977424, 0.10224714357374087, 0.2259278958810611, 0.024639000721715876, 0.36998750731016883, 0.21347096775979457, 0.7787236907387539, 0.2865026977906374], [0.7120878485776435, 0.6410093760281729, 0.3433337959958056, 0.9816993809320669, 0.8903541305700501, 0.15792923367225942, 0.7659270047414999, 0.8361391786531575, 0.4999189823338819, 0.8849569471782149, 0.593312706244898, 0.32966740948547324, 0.831464758701541, 0.1474716959981911, 0.6926903551822897]]
# 16x16
# table = [[0.007525403166613542, 0.4785823882914577, 0.7870550677732598, 0.2946101217871715, 0.4354757891668526, 0.9385959800706841, 0.8166850405232418, 0.9071912468583965, 0.6683296013411106, 0.6162776443446468, 0.966036493375325, 0.20397470440580234, 0.39271400091383535, 0.7655182631835393, 0.6309113257034791, 0.916140733883597], [0.81733557521578, 0.4267741876162172, 0.36800223509006913, 0.5144310191250773, 0.9440879121378656, 0.1266849692397024, 0.1477693813072597, 0.15782516400254598, 0.30129548157787345, 0.3675602439909337, 0.29478488035692396, 0.25713475068506453, 0.3328358425195812, 0.8351074048876338, 0.09485963074771664, 0.39988169265360296], [0.06869283427221806, 0.5285578439356838, 0.2533262078268126, 0.04309447321503035, 0.6476139559614192, 0.47825051593608403, 0.3478612928642566, 0.9494860704481175, 0.5342425921650252, 0.4333845750306802, 0.9522250330260454, 0.3514243429643742, 0.15113133276706214, 0.7070737622077711, 0.49337495379686436, 0.9692906620662025], [0.6582633731740524, 0.9491412216106614, 0.11644449330989615, 0.9075039994288474, 0.2883097748241862, 0.8179534785356893, 0.5120799963330686, 0.709000351591257, 0.4553105721648426, 0.7872265539155003, 0.7295177246771587, 0.42779852591687983, 0.7580907770842523, 0.26136455741175324, 0.6766498827301632, 0.750215788991569], [0.8404351572887232, 0.5581854587096418, 0.7971802313275879, 0.21462643309028073, 0.930734255673213, 0.052998436088101286, 0.43147936415225974, 0.20956698233839677, 0.7918189551818683, 0.023120669010144645, 0.9618192532890201, 0.9882511617147127, 0.4921832658245133, 0.3283742480984029, 0.7861310459176278, 0.007992182428167571], [0.04460315274645199, 0.21228686419736087, 0.6392267552015028, 0.0294716645281472, 0.2520880171199473, 0.5681229025445562, 0.3049001862642823, 0.9819875933903317, 0.2844992686992478, 0.5131154859010408, 0.5678556291743386, 0.59576267515515, 0.4291810715194665, 0.907046342364851, 0.2756377173877873, 0.16740218817198327], [0.9219231014763454, 0.08881339756048956, 0.9336484083808095, 0.6057567506982667, 0.5627738967681163, 0.9941126685843346, 0.5662089662260161, 0.12540720362540425, 0.09216193509177739, 0.15790777432149072, 0.04389946833811098, 0.2627520820946132, 0.7466762638885157, 0.7476027706440035, 0.4979693830582598, 0.5692771127999354], [0.4877914012054193, 0.86967217456826, 0.2997369374743635, 0.2721225386680096, 0.19817686328121709, 0.9358349720839578, 0.2511678231675374, 0.002883678111067045, 0.3400953388203798, 0.518635464322356, 0.8140576333995214, 0.6458316981437096, 0.7569251243756582, 0.3806562533497655, 0.5385214020619221, 0.6647791354241653], [0.12186924553471856, 0.8489011905498192, 0.9859889354824323, 0.736569266788496, 0.32143449694634996, 0.4490403616795685, 0.6199579074237055, 0.6971793861544743, 0.4463263943145853, 0.19185629133370685, 0.9508527413229377, 0.6023545354135535, 0.6239906842545146, 0.9238205697618121, 0.13540427395824217, 0.43321568284909173], [0.6478413217882892, 0.3689978120070396, 0.43578825842980473, 0.26372082305708244, 0.3274362728670628, 0.5804890939091556, 0.26923999608298554, 0.024410957649988796, 0.47746278522262575, 0.29360554976185027, 0.17893001424025268, 0.7880464565519331, 0.1839626106916311, 0.1024188834475912, 0.9309876259307994, 0.9106718369305528], [0.799304665067993, 0.6348078871539269, 0.6018106065415968, 0.701238235584224, 0.20537663715963028, 0.6134939887039675, 0.4977314452648637, 0.12435989352856602, 0.04015347985601614, 0.06607137214759917, 0.3265622492487281, 0.7462617172181987, 0.08791646948656984, 0.5577539023105195, 0.40160263403799, 0.2758111462098535], [0.09661391744436665, 0.4875295629951676, 0.9621403568800726, 0.26947079410791064, 0.0961932605560526, 0.4046667098659965, 0.8660082819650695, 0.3056167840138885, 0.32047041727588255, 0.3136286463823835, 0.97195487564264, 0.6004069199143849, 0.9266953978513094, 0.44148300514846395, 0.6669621129187553, 0.3544609993751381], [0.499046489923609, 0.6874298219757332, 0.6546424362491342, 0.7224446375725788, 0.033865217190732766, 0.6173981912855913, 0.13737719237061496, 0.7512246363375639, 0.34474827646593553, 0.4656492160690102, 0.0901875199194565, 0.010501752438017542, 0.8021266183847154, 0.5586567685360689, 0.25948792083836625, 0.39591006682095786], [0.8348676264070201, 0.8674755806182941, 0.008557987552714641, 0.29005136435468326, 0.06681065860019508, 0.8655305505324453, 0.8141385792301661, 0.44647021849412816, 0.44778177321863943, 0.7634695838554854, 0.05805616031403893, 0.07278505075058606, 0.5960100151462076, 0.38983373072825156, 0.9198573358868838, 0.7061201328765391], [0.5982350686729913, 0.8125742475128694, 0.9798609683361094, 0.012000028961260956, 0.18266059628590248, 0.24068713464384295, 0.5537205881141019, 0.12002939918643096, 0.6179410464196323, 0.1115972749298092, 0.5126515446056262, 0.8836597596253728, 0.7772426460122819, 0.6600403859800967, 0.8183278614968513, 0.06350981880545203], [0.8237647576457099, 0.10746526247976207, 0.8613828745118568, 0.47077843518475593, 0.6399602573812514, 0.3485011192266102, 0.5333331249768324, 0.27852728108594227, 0.5635397882878566, 0.2608391854286878, 0.9672598302893798, 0.9628699566416126, 0.3813482810570539, 0.19828489246857772, 0.9062087171085176, 0.6472177756498532]]

# Olympics table. Countries chosen as the top 10 medal total in 2012 Olympics
#         AU  CH  FR  GE  IT  JA  RU SK  UK   US
table = [[27, 52, 29, 82, 19, 22, 1, 27, 20, 108],   # 1992
         [41, 48, 37, 65, 35, 14, 63, 27, 15, 102],  # 1996
         [59, 54, 38, 56, 34, 18, 88, 28, 28, 93],   # 2000
         [49, 60, 33, 48, 32, 37, 92, 30, 30, 103],  # 2004
         [46, 95, 40, 41, 28, 25, 72, 29, 46, 110],  # 2008
         [35, 91, 35, 44, 28, 38, 68, 30, 65, 104],   # 2012
         [29, 70, 42, 42, 28, 41, 56, 21, 67, 121]]  # 2016


#table = np.random.rand(16, 16)
#table = table.tolist()
print(table)

# Normalize Table size
def normalize(table):
    s = sum([sum(row) for row in table])
    for row in range(len(table)):
        for col in range(len(table[row])):
            table[row][col] = table[row][col]/s
    return table


# For an arbitrary NxM table, we would have 2NM variables, of which they are height, length, or error
# The first NxM are the lengths, then the next N are the heights, and the last N*(M-1) are the errors
# Adds variables to the passed in model
def add_errs(table, model):
    n_row = len(table)
    n_col = len(table[0])

    # Lengths
    for i in range(n_row*n_col):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='l'+str(i+1))
    # Heights
    for i in range(n_row):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='h'+str(i+1))
    # Errors
    for i in range(n_row*(n_col-1)):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='e'+str(i+1))


# Add 2(M-1)(N-1)+(N-1)+1 Linear constraints
# 2(M-1)(N-1) of these are column boundary, the remaining N-1 are row length constraints
# Adds constraints to the passed in model
def addL_const(table, model, eps):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    lengths = vars[:len(vars)//2]
    heights = vars[len(vars)//2:len(vars)//2+n_row]
    errors = vars[len(vars)//2+n_row:]

    i = 1

    # First get the column adjacency constraints, of which there are 2(M-1)(N-1)
    # These constraints are a+b>=c and c+d>=a
    for row in range(n_row-1):
        for col in range(1, n_col):
            # Initialize a,b,c,d
            a = lengths[row*n_col:col+row*n_col]
            a.extend(errors[row*(n_col-1):row*(n_col-1)+(col)])
            b = lengths[col+row*n_col]
            c = lengths[(row+1)*n_col:col+(row+1)*n_col]
            c.extend(errors[(row+1)*(n_col-1):(row+1)*(n_col-1)+(col)])
            d = lengths[col+(row+1)*n_col]

            # Make our left and right sides for both equations
            left1 = gp.LinExpr(b)
            for var in a:
                left1.add(var)
            right1 = gp.LinExpr()
            for var in c:
                right1.add(var)
            right1.add(eps)

            left2 = gp.LinExpr(d)
            for var in c:
                left2.add(var)
            right2 = gp.LinExpr()
            for var in a:
                right2.add(var)
            right2.add(eps)

            model.addLConstr(left1, sense=GRB.GREATER_EQUAL, rhs=right1, name='bc'+str(i))
            i = i+1
            model.addLConstr(left2, sense=GRB.GREATER_EQUAL, rhs=right2, name='bc'+str(i))
            i = i+1

    i = 1
    # Get row lengths constraints
    for row in range(n_row - 1):
        l_len = lengths[row*(n_row):(row+1)*(n_row)]
        l_err = errors[row*(n_row-1):(row+1)*(n_row-1)]
        left = gp.LinExpr()
        for var in l_len:
            left.add(var)
        for var in l_err:
            left.add(var)

        r_len = lengths[(row+1) * (n_row):(row + 2) * (n_row)]
        r_err = errors[(row+1) * (n_row - 1):(row + 2) * (n_row - 1)]
        right = gp.LinExpr()
        for var in r_len:
            right.add(var)
        for var in r_err:
            right.add(var)

        m.addLConstr(left, sense=GRB.EQUAL, rhs=right, name='lc'+str(i))
        i = i + 1

    # Lastly add constraint so the height of our table is 1
    left = gp.LinExpr()
    for item in heights:
        left.add(item)
    m.addLConstr(left, sense=GRB.EQUAL, rhs=1, name='hc')


# Add NM quadratic constraints which fix the area for each cell. This requires setting NonConvex to 2
def addQ_const(table, model):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    lengths = vars[:len(vars) // 2]
    heights = vars[len(vars) // 2:len(vars) // 2 + n_row]
    errors = vars[len(vars) // 2 + n_row:]

    # We add NM Quadratic constraints.
    # These are the ones which will ensure the area of each cell is constant
    count = 1
    for i in range(n_row):
        for j in range(n_col):
            right = gp.LinExpr(table[i][j])
            left = gp.QuadExpr(heights[i]*lengths[(i*n_col)+j])
            model.addQConstr(left, sense=GRB.EQUAL, rhs=right, name='q'+str(count))
            count = count + 1


# Add the objective function. This will just be the sum of each error cell
def addObj(table, model):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    lengths = vars[:len(vars) // 2]
    heights = vars[len(vars) // 2:len(vars) // 2 + n_row]
    errors = vars[len(vars) // 2 + n_row:]

    exp = gp.QuadExpr()
    for i in range(n_row):
        for j in range(n_col-1):
            exp.add(heights[i]*errors[(i*(n_col-1))+j])
    model.setObjective(exp, sense=GRB.MINIMIZE)


try:

    epsilon = 0

    normalize(table)

    # Create a new model
    m = gp.Model("Solver")

    # Must do this so that our non-convex quadratic constraints can be used
    m.setParam(GRB.Param.NonConvex, 2)
    m.Params.TimeLimit = 180.0

    # Add the variables to our model
    add_errs(table, m)
    m.presolve()

    # Add the constraints to our model
    # Do it for both the linear and quadratic constraints separately
    addL_const(table, m, epsilon)
    m.presolve()

    # Now add the quadratic constraints
    addQ_const(table, m)
    m.presolve()

    # Lastly add the objective
    addObj(table, m)
    m.presolve()

    # Optimize our model
    m.optimize()

    # Display results
    print('Obj: %g' % m.objVal)

    # Write results to a csv so they can be visualized
    vars = m.getVars()
    n_col = len(table[0])
    n_row = len(table)
    lengths = vars[:len(vars) // 2]
    heights = vars[len(vars) // 2:len(vars) // 2 + n_row]
    errors = vars[len(vars) // 2 + n_row:]

    # Construct data into an array to return. Each row represents the data for one rectangle
    # Aquire y offsets
    yoff = [0] * (n_col + (n_col - 1))
    for i in range(0, len(heights)):
        yoff.extend([heights[i].x + yoff[(n_col + (n_col - 1)) * i]] * (n_col + (n_col - 1)))

    # Aquire Heights
    h = []
    for val in heights:
        h.extend([val.x] * (n_col + (n_col - 1)))

    # Aquire lengths
    l = []
    for i in range(n_row):
        for j in range(n_col):
            l.append(lengths[j+i*n_col].x)
            if j == n_col - 1:
                break
            l.append(errors[(n_col - 1) * i + j].x)

    # Aquire x offsets
    xoff = [0]
    for i in range(1, len(l)):
        if i % (n_col + n_col - 1) == 0:
            xoff.append(0)
        else:
            xoff.append(l[i - 1] + xoff[i - 1])

    # Aquire column number
    c = []
    for i in range(n_row):
        for j in range(2 * n_col - 1):
            if j % 2 == 1:
                c.append(-1)
            else:
                c.append(j % 20)

    # Build our data
    data = [['height', 'length', 'xoff', 'yoff', 'col']]
    for i in range((n_row * n_col) + (n_row * (n_col - 1))):
        temp = []
        temp.append(h[i])
        temp.append(l[i])
        temp.append(xoff[i])
        temp.append(yoff[i])
        temp.append(c[i])
        data.append(temp)

    # Write data into csv
    with open('mosek_LP.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        for row in data:
            mosek_writer.writerow(row)

    # # Display total error
    # e_sum = 0
    # for e in range(len(errors)):
    #     i = e//(n_col-1)
    #     e_sum = e_sum + errors[e].x * heights[i].x
    # print("The Total Error Is: " + str(e_sum))

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')