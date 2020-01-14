#initial
import numpy as np
import pandas as pd
import tool.tool as tl
import datetime, calendar

def score(df_x,fixed_dir = tl.DIR_PARA+'fixed/'):
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
    s_break = tl.K_BREAK_set 
    
    DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
    DATES = tl.DATE_list    #所有的日期 - 對照用
    D_WEEK = tl.D_WEEK_set  	#D_WEEK - 第 w 週中所包含的日子集合
    WEEK_of_DAY = tl.WEEK_list #WEEK_of_DAY - 日子j所屬的那一週


    #輸入班表
    i_nb = np.array(df_x)
    
    #計算人力情形

    people = np.zeros((nDAY,nT))
    
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(nT):
                #print(i,j,k)
                if i_nb[i][j] in SHIFTset['phone']:
                    people[j][k] = people[j][k] + A_t.values[i_nb[i][j]][k]   

    
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
                if j in SHIFTset['night']:
                    count = count + 1
            night_t = count / nightdaylimit[i]
        nightcount.append(night_t)
    nightcount = max(nightcount)

    breakCount = np.zeros((nEMPLOYEE,nW,5))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            w_d = WEEK_of_DAY[j]
            for r in range(len(s_break)):
                if i_nb[i][j] in s_break[r]:
                    breakCount[i][w_d][r] = 1
                    break
    breakCount = int(sum(sum(sum(breakCount))))
    
    nooncount = []
    for i in i_nb:
        count = 0
        for j in i:
            if j in SHIFTset['noon']:
                count = count + 1
        nooncount.append(count)
    nooncount = max(nooncount)

    result = P0 * lack + P1 * surplus + P2 * nightcount + P3 * breakCount + P4 * nooncount
    #print(result, lack, surplus, nightcount, breakCount, nooncount)
    return result
