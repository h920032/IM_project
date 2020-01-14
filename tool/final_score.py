#initial
import numpy as np
import pandas as pd
import tool.tool as tl
import datetime, calendar


def final_score(A_t, nEMPLOYEE, nDAY, nW, nK, nT, nR, DEMAND, P0, P1, P2, P3, P4, SHIFTset, WEEK_of_DAY, nightdaylimit, BREAK, df_x):

    K_type_int= {}
    for i in range(len(tl.CLASS_list)):
        K_type_int[i] = tl.CLASS_list[i]
    i_nb = np.vectorize({v: k for k, v in K_type_int.items()}.get)(np.array(df_x))
    
    #計算人力情形
    people = np.zeros((nDAY,nT))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            for k in range(nT):
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

    nooncount = []
    for i in i_nb:
        count = 0
        for j in i:
            if j in SHIFTset['noon']:
                count = count + 1
        nooncount.append(count)
    nooncount = max(nooncount)
    
    breakCount = np.zeros((nEMPLOYEE,nW,5))
    for i in range(nEMPLOYEE):
        for j in range(nDAY):
            w_d = WEEK_of_DAY[j]
            for r in range(len(BREAK)):
                if i_nb[i][j] in BREAK[r]:
                    breakCount[i][w_d][r] = 1
                    break
    breakCount = int(sum(sum(sum(breakCount))))

    print('lack = ',lack, ', surplus = ',surplus, ', nightCount = ',nightcount, ', breakCount = ',breakCount, ', noonCount = ',nooncount)
    result = P0 * lack + P1 * surplus + P2 * nightcount + P3 * breakCount + P4 * nooncount

    #print(result)
    return result
