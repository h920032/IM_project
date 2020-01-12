#initial
import numpy as np
import pandas as pd
import tool.tool as tl
import datetime, calendar
"""

year = 2020
month = 1



dir_name = './data/'
A_t = pd.read_csv(dir_name + 'fixed/' + 'fix_class_time.csv', header = 0, index_col = 0)
DEMAND_t = pd.read_csv(dir_name + 'per_month/' + "Need.csv", header = 0, index_col = 0).T
EMPLOYEE_t = pd.read_csv(dir_name + 'per_month/' + "Employee.csv", header = 0)
NM_t = EMPLOYEE_t['NM']
NW_t = EMPLOYEE_t['NW']
E_NAME = list(EMPLOYEE_t['Name_English'])   #E_NAME - 對照名字與員工index時使用
E_SENIOR_t = EMPLOYEE_t['Senior']
E_POSI_t = EMPLOYEE_t['Position']
E_SKILL_t = EMPLOYEE_t[['skill-phone','skill-CD','skill-chat','skill-outbound']]
SKILL_NAME = list(E_SKILL_t.columns)
P_t = pd.read_csv(dir_name + 'parameters/' + 'weight_p1-3.csv', header = None, index_col = 0)
Kset_t = pd.read_csv(dir_name + 'fixed/' + 'fix_classes.csv', header = None, index_col = 0)
SKset_t = pd.read_csv(dir_name + 'parameters/' + 'skill_class_limit.csv', header = None, index_col = 0)
M_t = pd.read_csv(dir_name + 'per_month/' + "Assign.csv", header = None, skiprows=[0])
L_t = pd.read_csv(dir_name+ 'parameters/' +"lower_limit.csv", header = None, skiprows=[0])
U_t = pd.read_csv(dir_name+ 'parameters/' +"upper_limit.csv", header = None, skiprows=[0])
Ratio_t = pd.read_csv(dir_name+ 'parameters/' +"senior_limit.csv",header = None, skiprows=[0])
SENIOR_bp = Ratio_t[3]
timelimit = pd.read_csv(dir_name+ 'parameters/' +"time_limit.csv", header = 0)
nightdaylimit = pd.read_csv(dir_name+ 'parameters/' +"class_upperlimit.csv", header = 0).loc[0][0]

nEMPLOYEE = EMPLOYEE_t.shape[0]
nDAY = tl.get_nDAY(year,month)
nW = tl.get_nW(year,month)
nK = 19

DEMAND = DEMAND_t.values.tolist()

P0 = 100
P1 = P_t[1]['P1']
P2 = P_t[1]['P2']
P3 = P_t[1]['P3']

S_NIGHT = [11, 12, 13]
S_BREAK = [[11,12],[1,7,14,15],[2,8,16,18],[3,9,17],[4,10]]

#輸入班表
df_x = []
for i in pd.read_csv("Schedule_2019_4.csv", header = 0, index_col = 0).drop('name', axis = 1).values.tolist():
    df_x.append(list(filter(lambda x: x!='X', i)))

"""

def final_score(year, month, A_t, nEMPLOYEE, nDAY, nW, nK, nT, nR, DEMAND, P0, P1, P2, P3, P4, SHIFTset, Shift_name, WEEK_of_DAY, nightdaylimit, BREAK, df_x):

    S_DEMAND = []
    S_DEMAND.extend(SHIFTset['phone'])
    for i in range(len(S_DEMAND)):
        S_DEMAND[i] += 1

    S_NIGHT = []
    S_NIGHT.extend(SHIFTset['night'])                                     #S_NIGHT - 所有的晚班
    for i in range(len(S_NIGHT)):
        S_NIGHT[i] += 1
    
    S_NOON = []
    S_NOON.extend(SHIFTset['noon'])                                       #S_NOON - 所有的午班
    for i in range(len(S_NOON)):
        S_NOON[i] += 1

    S_BREAK = [tmp for tmp in range(nR)]
    for r in range(nR):
        S_BREAK[r] = []
        for j in range(len(BREAK[r])):
            S_BREAK[r].append(BREAK[r][j]+1)

    K_type_dict= {}
    for ki in range(len(Shift_name)+1):
        if ki == 0:
            K_type_dict[ki] =''
        else:
            K_type_dict[ki] =Shift_name[ki-1]
    #K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
    #K_type_dict = {1:'O',2:'A2',3:'A3',4:'A4',5:'A5',6:'MS',7:'AS',8:'P2',9:'P3',10:'P4',11:'P5',12:'N1',13:'M1',14:'W6',15:'CD',16:'C2',17:'C3',18:'C4',19:'OB'}
    i_nb = np.vectorize({v: k for k, v in K_type_dict.items()}.get)(np.array(df_x))
    
    #計算人力情形
    people = np.zeros((nDAY,nT))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(nT):
                if i_nb[i][j] in S_DEMAND:
                    people[j][k] = people[j][k] + A_t.values[i_nb[i][j]-1][k]
    output_people = (people - DEMAND).tolist()
    
    lack = 0
    for i in output_people:
        for j in i:
            if j < 0:
                lack = -j + lack

    surplus = 0
    surplus_t = 0
    for i in output_people:
        for j in i:
            if j > 0:
                surplus_t = j
                if surplus_t > surplus:
                    surplus = surplus_t

    nightcount = []
    for i in range(len(i_nb)):
        night_t = 0
        if (nightdaylimit[i]>0):
            count = 0
            for j in i_nb[i]:
                if j in S_NIGHT:
                    count = count + 1
            night_t = count / nightdaylimit[i]
        nightcount.append(night_t)
    nightcount = max(nightcount)

    nooncount = []
    for i in i_nb:
        count = 0
        for j in i:
            if j in S_NOON:
                count = count + 1
        nooncount.append(count)
    nooncount = max(nooncount)
    
    breakCount = np.zeros((nEMPLOYEE,nW,5))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            w_d = WEEK_of_DAY[j]
            for r in range(len(S_BREAK)):
                if i_nb[i][j] in S_BREAK[r]:
                    breakCount[i][w_d][r] = 1
                    break
    breakCount = int(sum(sum(sum(breakCount))))

    print('lack = ',lack, ', surplus = ',surplus, ', nightCount = ',nightcount, ', breakCount = ',breakCount, ', noonCount = ',nooncount)
    result = P0 * lack + P1 * surplus + P2 * nightcount + P3 * breakCount + P4 * nooncount

    #print(result)
    return result
