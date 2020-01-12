#initial
import numpy as np
import pandas as pd
import tool.tool as tl
import datetime, calendar

def score(df_x,fixed_dir = './data/parameters/fixed/'):
    A_t = pd.read_csv(fixed_dir + 'fix_class_time.csv', header = 0, index_col = 0)
    EMPLOYEE_t = tl.Employee_t
    
    Shift_name = tl.CLASS_list
    nightdaylimit = EMPLOYEE_t['night_perWeek']

    year  = tl.YEAR
    month = tl.MONTH

    nEMPLOYEE = tl.nE
    nDAY = tl.nD
    nK = tl.nK
    nT = tl.nT
    nR = tl.nR
    nW = tl.nW
    mDAY = tl.mDAY
    DEMAND = tl.DEMAND

    P0, P1, P2, P3, P4 = tl.P

    SHIFTset = tl.K_CLASS_set
    BREAK_t = tl.K_BREAK_set 
    
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
        for j in range(len(BREAK_t[r])):
            S_BREAK[r].append(BREAK_t[r][j]+1)

    S_DEMAND = []
    S_DEMAND.extend(SHIFTset['phone'])
    for i in range(len(S_DEMAND)):
        S_DEMAND[i] += 1
    
    DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
    DATES = tl.DATE_list    #所有的日期 - 對照用
    D_WEEK = tl.D_WEEK_set  	#D_WEEK - 第 w 週中所包含的日子集合
    WEEK_of_DAY = tl.WEEK_list #WEEK_of_DAY - 日子j所屬的那一週


    #輸入班表

    K_type = Shift_name
    # K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
    # K_type_dict = {0:'',1:'O',2:'A2',3:'A3',4:'A4',5:'A5',6:'MS',7:'AS',8:'P2',9:'P3',10:'P4',11:'P5',12:'N1',13:'M1',14:'W6',15:'CD',16:'C2',17:'C3',18:'C4',19:'OB'}
    K_type_int = {0:''}
    for i in range(len(Shift_name)):
        K_type_int[i+1] = i
    # K_type_int = {0:'',1:0,2:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,10:9,11:10,12:11,13:12,14:13,15:14,16:15,17:16,18:17,19:18}
    i_nb = np.vectorize({v: k for k, v in K_type_int.items()}.get)(np.array(df_x))
    
    #計算人力情形

    people = np.zeros((nDAY,nT))
    
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(nT):
                #print(i,j,k)
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

    breakCount = np.zeros((nEMPLOYEE,nW,5))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            w_d = WEEK_of_DAY[j]
            for r in range(len(S_BREAK)):
                if i_nb[i][j] in S_BREAK[r]:
                    breakCount[i][w_d][r] = 1
                    break
    breakCount = int(sum(sum(sum(breakCount))))
    
    nooncount = []
    for i in i_nb:
        count = 0
        for j in i:
            if j in S_NOON:
                count = count + 1
        nooncount.append(count)
    nooncount = max(nooncount)

    result = P0 * lack + P1 * surplus + P2 * nightcount + P3 * breakCount + P4 * nooncount
    #print(result, lack, surplus, nightcount, breakCount, nooncount)
    return result
