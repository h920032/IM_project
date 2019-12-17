import numpy as np
import pandas as pd
import random as rd

def ABLE(this_i,this_j,this_k):
    ans = True
    
    #only one work a day
    for k in SHIFT:
        if( work[this_i,this_j,k] == 1 and k!=this_k):    
            ans = False
            return ans
    #被指定的排班及當天被排除的排班
    for tmp in ASSIGN:
        if(tmp[0]==this_i):
            if(tmp[1]==this_j):
                #被指定的排班
                if(tmp[2]==this_k):
                    return ans
                else:
                    ans = False
                    return ans

    #判斷是否正在排晚班
    arrangenightshift = False
    for tmp in S_NIGHT:
        if(this_k == tmp):
            arrangenightshift = True
            
    #正在排晚班才進去判斷
    if(arrangenightshift == True):
        #no continuous night shift:
        #非第一天或最後一天
        if(this_j!=0):
            for tmp in S_NIGHT:
                if(work[this_i,this_j-1,tmp] == 1):
                    ans = False
                    return ans
                elif (this_j!=nDAY-1):
                    if (work[this_i,this_j+1,tmp] == 1):
                        ans = False
                        return ans
        
        #第一天
        else:
            if(FRINIGHT[this_i] == 1):
                ans = False
                return ans
            elif(work[this_i,this_j+1,tmp] == 1):
                ans = False
                return ans
        #no too many night shift a week:
        whichweek = WEEK_of_DAY[this_j]
        #非第一週
        if(whichweek!=0):
            countnightshift = 0
            for theday in D_WEEK[whichweek]:
                for tmp in S_NIGHT:
                    if(work[this_i,theday,tmp] == 1):
                        if(theday == this_j and tmp == this_k):
                            countnightshift += 0
                        else:
                            countnightshift += 1
            if(countnightshift >= nightdaylimit[this_i]):
                ans = False
                return ans              
        #第一週
        else:
            countnightshift = 0
            for theday in D_WEEK[0]:
                for tmp in S_NIGHT:
                    if(work[this_i,theday,tmp] == 1):
                        if(theday == this_j and tmp == this_k):
                            countnightshift += 0
                        else:
                            countnightshift += 1
            if(countnightshift+LMNIGHT[this_i] >= nightdaylimit[this_i]):
                ans = False
                return ans            
            
    #排班的上限
    for item in UPPER:
        if(this_j in DAYset[item[0]] and this_k in SHIFTset[item[1]]):
            tmpcount = 0
            for people in EMPLOYEE:
                for tmp in  SHIFTset[item[1]]:
                    if(work[people,this_j,tmp]==1):
                        if(people == this_i and tmp == this_k):
                            tmpcount+=0
                        else:
                            tmpcount+=1
            if(tmpcount>=item[2]):
                ans = False
                return ans
    return ans 

def ARRANGEMENT(work, nEMPLOYEE, nDAY, nK, CONTAIN, CURRENT_DEMAND, nT):
    fix = []
    for i in range(nEMPLOYEE):
        employee = []
        for j in range(nDAY):
            is_arrange = False
            for k in range(nK):
                if work[i,j,k] == True:
                    is_arrange = True
                    employee.append(1)
            if is_arrange == False:
                rand = rd.randint(1,nK)
                for r in range(nK):
                    if ABLE(i,j,rand-1) == True:
                        work[i,j,rand-1] = True
                        for t in range(nT):
                            if CONTAIN[rand-1][t] == 1:              
                                CURRENT_DEMAND[j][t] -= 1
                        employee.append(0)
                        is_arrange = True
                        break
                    else:
                       rand = rd.randint(1,nK)
                if is_arrange == False:
                    for r in range(nK):
                        if ABLE(i,j,r) == True:
                            work[i,j,r] = True
                            for t in range(nT):
                                if CONTAIN[r][t] == 1:              
                                    CURRENT_DEMAND[j][t] -= 1
                            employee.append(0)
                            is_arrange = True
                            break
        fix.append(employee)
    return work, fix, CURRENT_DEMAND
