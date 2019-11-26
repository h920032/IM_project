#initial
import numpy as np
import pandas as pd
import data.tool as tl
import datetime, calendar
year = 2020
month = 1

dir_name = './data/'
A_t = pd.read_csv(dir_name + 'fix_class_time.csv', header = 0, index_col = 0)
DEMAND_t = pd.read_csv(dir_name+"進線人力.csv", header = 0, index_col = 0).T
EMPLOYEE_t = pd.read_csv(dir_name+"EMPLOYEE.csv", header = 0)
NM_t = EMPLOYEE_t['NM']
NW_t = EMPLOYEE_t['NW']
E_NAME = list(EMPLOYEE_t['name_English'])   #E_NAME - 對照名字與員工index時使用
E_SENIOR_t = EMPLOYEE_t['Senior']
E_POSI_t = EMPLOYEE_t['Position']
E_SKILL_t = EMPLOYEE_t[['skill-phone','skill-CD','skill-chat','skill-outbound']]
SKILL_NAME = list(E_SKILL_t.columns)
P_t = pd.read_csv(dir_name + '軟限制權重.csv', header = None, index_col = 0)
Kset_t = pd.read_csv(dir_name + 'fix_classes.csv', header = None, index_col = 0)
SKset_t = pd.read_csv(dir_name + 'skills_classes.csv', header = None, index_col = 0)
M_t = pd.read_csv(dir_name+"特定班別、休假.csv", header = None, skiprows=[0])
L_t = pd.read_csv(dir_name+"下限.csv", header = None, skiprows=[0])
U_t = pd.read_csv(dir_name+"上限.csv", header = None, skiprows=[0])
Ratio_t = pd.read_csv(dir_name+"CSR年資占比.csv",header = None, skiprows=[0])
SENIOR_bp = Ratio_t[3]
timelimit = pd.read_csv(dir_name+"時間限制.csv", header = 0)
nightdaylimit = pd.read_csv(dir_name+"晚班天數限制.csv", header = 0).loc[0][0]

nEMPLOYEE = EMPLOYEE_t.shape[0]
nDAY = tl.get_nDAY(year,month)
nW = tl.get_nW(year,month)
nK = 19

DEMAND = DEMAND_t.values.tolist()

P0 = 100
P1 = P_t[1]['P1']
P2 = P_t[1]['P2']
P3 = P_t[1]['P3']
P4 = P_t[1]['P4']

S_NIGHT = [11, 12, 13]
S_BREAK = [[11,12],[1,7,14,15],[2,8,16,18],[3,9,17],[4,10]]

#輸入班表
df_x = []
for i in pd.read_csv("排班結果.csv", header = 0, index_col = 0).drop('name', axis = 1).values.tolist():
    df_x.append(list(filter(lambda x: x!='X', i)))
K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
K_type_dict = {1:'O',2:'A2',3:'A3',4:'A4',5:'A5',6:'MS',7:'AS',8:'P2',9:'P3',10:'P4',11:'P5',12:'N1',13:'M1',14:'W6',15:'CD',16:'C2',17:'C3',18:'C4',19:'OB'}
i_nb = np.vectorize({v: k for k, v in K_type_dict.items()}.get)(np.array(df_x))

#計算人力情形
people = np.zeros((nDAY,24))
for i in range(0,nEMPLOYEE):
    for j in range(0,nDAY):
        for k in range(0,24):
            people[j][k] = people[j][k] + A_t.values[i_nb[i][j]-1][k]
output_people = (people - DEMAND).tolist()
lack = 0
for i in output_people:
    for j in i:
        if j < 0:
            lack = -j + lack

surplus = 0
for i in output_people:
    for j in i:
        if j > 0:
            surplus = j + surplus

nightcount = []
for i in i_nb:
    count = 0
    for j in i:
        if j == 12 or j == 13 or j == 14:
            count = count + 1
    nightcount.append(count)
nightcount = max(nightcount)

date = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(1), "%Y-%m-%d")
weekday = date.weekday()
if weekday == 5 or weekday == 6:
    weekday = 0

breakCount = np.ones((nEMPLOYEE,nW,5))
for i in range(nEMPLOYEE):
    for j in range(nDAY):
        w_d = int((j+weekday)/5)
        if i_nb[i][j]!=1:
            for k in range(5):
                if A_t.values[i_nb[i][j]-1][k+5]==1:
                    breakCount[i][w_d][k]=0
breakCount = int(sum(sum(sum(breakCount))))

df_a = EMPLOYEE_t.drop(['name_English', 'name_Chinese', 'id', 'Senior', 'Position', 'NM','NW'],axis = 1).values
df_c = np.zeros((nEMPLOYEE,nK))
for i in range(nEMPLOYEE):
    if sum(df_a[i]) > 0:
        for j in range(nDAY):
            df_c[i][i_nb[i][j]-1]=df_c[i][i_nb[i][j]-1]+1

complement = int(max(max(df_c.reshape(1,nEMPLOYEE*nK))))

result = P0 * lack + P1 * surplus + P2 * nightcount + P3 * breakCount + P4 * complement

print(result)
