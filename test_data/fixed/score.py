#initial
import numpy as np
import pandas as pd
import data.fixed.tool as tl
import datetime, calendar

def score(df_x,nDAY,nW,year,month,fixed_dir = './data/fixed/', parameters_dir = './data/parameters/', per_month_dir = './data/per_month/',AssignTest='',NeedTest='',EmployeeTest=''):
    A_t = pd.read_csv(fixed_dir + 'fix_class_time.csv', header = 0, index_col = 0)
    DEMAND_t = pd.read_csv(per_month_dir+"Need"+NeedTest+".csv", header = 0, index_col = 0, engine = 'python').T
    EMPLOYEE_t = pd.read_csv(per_month_dir+"Employee"+EmployeeTest+".csv", header = 0, engine = 'python')
    NM_t = EMPLOYEE_t['NM']
    NW_t = EMPLOYEE_t['NW']
    E_NAME = list(EMPLOYEE_t['Name_English'])   #E_NAME - 對照名字與員工index時使用
    E_SENIOR_t = EMPLOYEE_t['Senior']
    E_POSI_t = EMPLOYEE_t['Position']
    E_SKILL_t = EMPLOYEE_t[['skill-phone','skill-CD','skill-chat','skill-outbound']]
    SKILL_NAME = list(E_SKILL_t.columns)
    P_t = pd.read_csv(parameters_dir + 'weight_p1-4.csv', header = None, index_col = 0)
    Kset_t = pd.read_csv(fixed_dir + 'fix_classes.csv', header = None, index_col = 0)
    SKset_t = pd.read_csv(parameters_dir + 'skills_classes.csv', header = None, index_col = 0)
    M_t = pd.read_csv(per_month_dir+'Assign'+AssignTest+'.csv', header = None, skiprows=[0], engine = 'python')
    L_t = pd.read_csv(parameters_dir+"lower_limit.csv", header = 0, engine='python')
    U_t = pd.read_csv(parameters_dir+"upper_limit.csv", header = None, skiprows=[0])
    Ratio_t = pd.read_csv(parameters_dir+"senior_limit.csv",header = None, skiprows=[0])
    SENIOR_bp = Ratio_t[3]
    timelimit = pd.read_csv(parameters_dir+"time_limit.csv", header=0)
    #nightdaylimit = pd.read_csv(dir_name+"晚班天數限制.csv", header = 0).loc[0][0]
    
    date = pd.read_csv(per_month_dir + 'Date.csv', header = None, index_col = 0)
    #year = int(date.iloc[0,0])
    #month = int(date.iloc[1,0])

    nEMPLOYEE = EMPLOYEE_t.shape[0]
    #nDAY = tl.get_nDAY(year,month)
    #nW = tl.get_nW(year,month)
    nK = 19
    mDAY = int(calendar.monthrange(year,month)[1])
    DEMAND = DEMAND_t.values.tolist()

    P0 = 100
    P1 = P_t[1]['P1']
    P2 = P_t[1]['P2']
    P3 = P_t[1]['P3']
    P4 = P_t[1]['P4']

    S_NIGHT = [11, 12, 13]
    S_BREAK = [[11,12],[1,7,14,15],[2,8,16,18],[3,9,17],[4,10]]
    DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
    DATES = [ int(x) for x in DEMAND_t.index ]    #所有的日期 - 對照用
    month_start = tl.get_startD(year,month)         #本月第一天是禮拜幾 (Mon=0, Tue=1..)
    D_WEEK = tl.SetDAYW(month_start+1,mDAY,nW, DAY, DATES)  	#D_WEEK - 第 w 週中所包含的日子集合
    WEEK_of_DAY = tl.SetWEEKD(D_WEEK, nW) #WEEK_of_DAY - 日子j所屬的那一週


    #輸入班表
    """
    df_x = []
    for i in pd.read_csv("排班結果.csv", header = 0, index_col = 0).drop('name', axis = 1).values.tolist():
        df_x.append(list(filter(lambda x: x!='X', i)))
    """


    K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
    K_type_dict = {0:'',1:'O',2:'A2',3:'A3',4:'A4',5:'A5',6:'MS',7:'AS',8:'P2',9:'P3',10:'P4',11:'P5',12:'N1',13:'M1',14:'W6',15:'CD',16:'C2',17:'C3',18:'C4',19:'OB'}
    K_type_int = {0:'',1:0,2:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,10:9,11:10,12:11,13:12,14:13,15:14,16:15,17:16,18:17,19:18}
    i_nb = np.vectorize({v: k for k, v in K_type_int.items()}.get)(np.array(df_x))
    #i_nb = df_x
    #計算人力情形

    people = np.zeros((nDAY,24))
    #print(people)

    #print(nDAY)
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(24):
                #print(i,j,k)
                people[j][k] = people[j][k] + A_t.values[i_nb[i][j]-1][k]   #TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'


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

    breakCount = np.zeros((nEMPLOYEE,nW,5))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            w_d = WEEK_of_DAY[j]
            if i_nb[i][j]!=1 and i_nb[i][j]!=6 and i_nb[i][j]!=7 and i_nb[i][j]!=14:
                for k in range(5):
                    if A_t.values[i_nb[i][j]-1][k+5] == 0 and A_t.values[i_nb[i][j]-1][k+6] == 0:
                        breakCount[i][w_d][k] = 1
    breakCount = int(sum(sum(sum(breakCount))))

    df_a = EMPLOYEE_t.drop(['Name_English', 'Name_Chinese', 'ID', 'Senior', 'Position', 'NM','NW'],axis = 1).values
    df_c = np.zeros((nEMPLOYEE,nK))
    for i in range(nEMPLOYEE):
        if sum(df_a[i]) > 0:
            for j in range(nDAY):
                df_c[i][i_nb[i][j]-1]=df_c[i][i_nb[i][j]-1]+1

    complement = int(max(max(df_c.reshape(1,nEMPLOYEE*nK))))

    result = P0 * lack + P1 * surplus + P2 * nightcount + P3 * breakCount + P4 * complement
    return result
