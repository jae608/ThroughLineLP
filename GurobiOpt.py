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
# table = [[0.2209148716575542, 0.3569383578791975, 0.9215875961564114, 0.18851090845264895, 0.5760537199052342, 0.8880580141582214, 0.8645787634123707, 0.15574882052538452, 0.14047073576634428, 0.9729667923842291, 0.020006937358597265, 0.069271416604341, 0.9839700382278456, 0.03127298445330373, 0.13738892162220406], [0.3356134458411547, 0.40697355599195983, 0.10986634406123719, 0.08634441469184728, 0.15898611338217727, 0.5569367256041802, 0.11962142947706966, 0.6307765207171542, 0.6446460698803629, 0.4911818453229009, 0.5339311297645213, 0.09225246223021177, 0.9420367593774388, 0.6484802546943809, 0.3510757667919625], [0.9928805606852225, 0.6973906672123094, 0.34755057223384456, 0.1399361577919207, 0.9475196807447078, 0.6249749235482209, 0.5313676926864364, 0.8736300100493736, 0.2380849073225717, 0.01809527103204045, 0.48667395621449294, 0.28684375956591246, 0.2798846353585045, 0.9526324623337374, 0.2908037352994043], [0.07838004012294597, 0.06361118346956962, 0.6568372061808008, 0.22677244501582405, 0.12104903574516546, 0.5413772876407867, 0.37904321452026857, 0.5897799342978128, 0.9104845765134529, 0.5590138996517251, 0.5912699181076804, 0.758337076209645, 0.32788713628312083, 0.9578283282029317, 0.6695921129998581], [0.2898887734451283, 0.2757659907319181, 0.5642526789152191, 0.8826587316405098, 0.4737116633807025, 0.23119214125549536, 0.8895849457262216, 0.44973540086004626, 0.650764660851253, 0.41834682132927314, 0.8852470899996523, 0.5445176780369537, 0.8824608342489417, 0.9220100121876104, 0.759933150551741], [0.44458796617172947, 0.5669788460299088, 0.7047202717903815, 0.028494532282773766, 0.2376223912875235, 0.19039669778186552, 0.5316373050302048, 0.9719233505575678, 0.628202574471163, 0.7415811711819768, 0.06736055306239486, 0.18523578869738067, 0.69213999932317, 0.783912195638696, 0.10988738052773972], [0.5362572392442584, 0.06145099364852036, 0.33817473040041934, 0.48017457513872275, 0.8405530837560362, 0.3303422968331864, 0.6721359919457037, 0.04131414040517811, 0.030128063654128123, 0.04802481075500409, 0.025476143070361168, 0.6991399844068359, 0.481896623002943, 0.28330546817732827, 0.28158637505340334], [0.38659718461195336, 0.529850411867542, 0.36718740482488044, 0.14351344920428843, 0.15233116967410698, 0.7143347164173831, 0.3168770592478627, 0.1279008529578448, 0.5244401912266051, 0.32974480060462585, 0.06464848715415472, 0.31394743199036135, 0.7611586177278956, 0.4287711488020043, 0.06292602325031149], [0.20036014506162236, 0.7907783970553451, 0.8852813806946367, 0.059284191903620775, 0.3841664899851358, 0.9996574864689722, 0.9818280799318131, 0.8168968743970262, 0.2912063928817751, 0.3551242925178131, 0.486966625129725, 0.7199004000952194, 0.33686696270102434, 0.5677595331112455, 0.33938644361076986], [0.7828803643114832, 0.7523184496020988, 0.4609805236055383, 0.41894764458086486, 0.5567562811280299, 0.6511445753709075, 0.3078007766309808, 0.19350661154724624, 0.0018374503354759986, 0.2783070308108181, 0.8989987989006752, 0.06442957931571724, 0.0047513766604802, 0.2804339183686162, 0.5985049476969221], [0.4403845395308704, 0.47887821617379434, 0.2878638582447225, 0.2445375631364407, 0.07591178747637106, 0.44399589391379735, 0.3001079540260563, 0.08464772717724722, 0.2912727839370931, 0.8460521069345397, 0.3263599933276976, 0.9316939336179493, 0.28395931633033966, 0.9905190874864225, 0.05056021160290147], [0.7873814876327501, 0.3783926477345775, 0.9530757893180631, 0.6920437169685384, 0.19630135300328988, 0.8578347859478553, 0.07231370808788984, 0.8596180559385402, 0.20598560831238066, 0.941708336364452, 0.5611593434496318, 0.17839025236874728, 0.41795573161159405, 0.06153477378665051, 0.08258175714760208], [0.9911496765461254, 0.40567720414501673, 0.9669066921658571, 0.0060208132038145346, 0.5079021275676099, 0.263939565667052, 0.00887284733693705, 0.9440630716016752, 0.4937796300892837, 0.8758902569576816, 0.7978769220169518, 0.043067806416474674, 0.041571819873437055, 0.007983495481770797, 0.5381306596071727], [0.152903770676184, 0.6478175904526255, 0.8362014523918502, 0.7026844471098234, 0.49837979305604363, 0.40609557465216883, 0.1903474057735658, 0.8125569013658721, 0.1386607834707816, 0.07658144068383499, 0.36604997414355944, 0.8220987458916235, 0.9762550737440018, 0.8276191394010538, 0.19891341934888618], [0.0937117099986331, 0.7041169110993132, 0.9687926573380289, 0.9110567537839998, 0.9599898353255452, 0.17616034158874094, 0.0959001059070026, 0.25599131822238574, 0.3421328568145703, 0.437323355594451, 0.4207307939507644, 0.021754271583358742, 0.8642264286380056, 0.592241515349617, 0.45721097578876146]]


table = np.random.rand(15, 15)
table = table.tolist()
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
    m.Params.TimeLimit = 60.0

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
                c.append(j % 6)

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