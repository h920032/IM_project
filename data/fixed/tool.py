# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ting
"""
import math, re
import pandas as pd
from datetime import datetime, date





#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# import data
# 要輸出的東西：
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#

#=============================================================================#
#def function
#=============================================================================#
#讀檔：try/except是為了因應條件全空時
def readFile(dir, header_=None, skiprows_=[0], index_col_=None):
    try:
        t = pd.read_csv(dir, header=header_,skiprows=skiprows_,index_col=index_col_,encoding='utf-8-sig',engine='python')
    except:
        t = pd.DataFrame()
    return t



#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# 資料前處理
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#


"""===========================================
	nJ, nW
==========================================="""
#nW
def get_nW(year,month):
	startDay = date(year,month,1).weekday()	#Mon=0,Tue=1...
	totalDay = (date(year,month+1,1) - date(year,month,1)).days if month<12 else 31
	return math.ceil( (totalDay+startDay) / 7 )

#nJ
def get_nDAY(year,month):
	totalDay = (date(year,month+1,1) - date(year,month,1)).days if month<12 else 31
	ans = 0
	for i in range(totalDay):
		ans += (date(year,month,i+1).weekday()<5)
	return ans

#start day
def get_startD(year,month):
	d = date(year,month,1).weekday()
	return (d if d<5 else 0) 

"""===========================================
	Set DAY Functions
==========================================="""
#JW 第w周包含的日子集合，參數：第一天上班是星期幾,共幾天,共幾週,日子集合,日期集合
def SetDAYW(day, total_day, total_week, DAY, DATE):  
    ans = []
    count  = 1
    for i in range(total_week): #對每一周
        tmp = []
        if(i == 0): #第一周(很可能不完整)
            for j in range(8-day):  #對星期日~一
                for k in DAY:
                    if count == DATE[k]:   #該天有上班
                        tmp.append(k)
                        break
                count+=1
        else:
            for j in range(7):
                for k in DAY:
                    if count == DATE[k]:   #該天有上班
                        tmp.append(k)       #加入
                        break
                count+=1
                if count == total_day + 1:
                    break
        ans.append(tmp)
    return ans

def SetWEEKD(D_WEEK, total_week):  
    ans = []
    for i in range(total_week):
        for j in D_WEEK[i]:
            ans.append(i)
    return ans

#JW_fri 第w周的星期五與下周一的集合
#JW_fri 無國定假日的話
def SetDAYW_fri(JWset, total_week):   #JW日子集合/幾週
    ans = []
    for i in range(total_week-1):
        tmp = []
        tmp.append(JWset[i][-1])
        tmp.append(JWset[i+1][0])
        ans.append(tmp)
    return ans

#Jset 通用日子集合
def SetDAY(day, total_day, DATE):   #第一天上班是星期幾/幾天
    set = {'all':list(range(total_day))}
    set['Mon']=[]; set['Tue']=[]; set['Wed']=[]
    set['Thu']=[]; set['Fri']=[]
    # 所有周一，所有週二，所有週三...
    w = ['Mon','Tue','Wed','Thu','Fri']
    for i in range(total_day):
        set[ w[(DATE[i]-1)%7] ].append(i)
    return set

#VACnextdayset 假日後或週一的集合
def SetVACnext(month_start, nDAY, DATES):
    ans = []
    ans2 = []
    #第一天不是1 / 第一天是1
    if DATES[0]!=1:
        ans.append(0)
    elif (month_start == 0 and DATES[0]==1):
        ans.append(0)
    else:
        ans2.append(0)
    
    
    for i,day in enumerate(DATES):
        if i==0:
            continue
        else:
            #我的前一天不是我的數字-1(代表前一天放假)
            if(day-1!=DATES[i-1]):
                ans.append(i)
            else:
                ans2.append(i)
    return ans, ans2
        



"""===========================================
	Set Const Functions
==========================================="""
#SKILL 每個技能的員工組合
def SetSKILL(matrix):
    ans = {}
    for s in matrix.columns:
        alist = matrix[s]
        ss = re.sub('skill-', '', s)
        ans[ss] = []
        for i in range(len(alist)):
            if alist[i]==1:
                ans[ss].append(i)
    return ans

#POSI 每個職位的員工組合
def SetPOSI(alist, order):
    n = len(alist)
    s = {'任意':list(range(n))}  #預設職位：任意(包含所有人)
    #登錄所有職位
    for i,p in enumerate(order):
        s[p] = []
        poslist = []
        for j in range(i, len(order)):
            poslist.append(order[j])
        for i in range(n):
            if alist[i] in poslist:
                s[p].append(i)
    return s

#SENIOR 超過特定年資的員工組合
def SetSENIOR(alist, bp):
	s = []
	for i in range(len(alist)):
		if alist[i] >= bp:
			s.append(i)
	return s


"""===========================================
	Text-numberID translate function
==========================================="""
def Tran_t2n(text, names):
    try:
        c = names.index(text)
    except:
        print('Tran_t2n():',text,"not in ",end='')
        print(names[0:3],end='')
        print('...')
        c = None
    return c


"""
Calculation of NW & NM from last month 
"""
def calculate_NW (EMPLOYEE_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEMPLOYEE):	
        for i in range (lastday_row):	
            if(lastmonth.iloc[i,(lastday_column-1)] == "N1" or lastmonth.iloc[i,(lastday_column-1)] == "M1" or lastmonth.iloc[i,(lastday_column-1)] == "W6") :
                temp_name = str(lastmonth.iloc[i,0])

                for i in range (nEMPLOYEE):			
                        if (temp_name == str(EMPLOYEE_t.loc[i,'id'])) :
                                EMPLOYEE_t.at[i,'NW'] = 1
#    print (EMPLOYEE_t["NW"]) 
    
def calculate_NM (EMPLOYEE_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEMPLOYEE):  
    if (lastday_ofmonth != "Fri") :
        if (lastday_ofmonth == "Thu") :
                   
            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-4 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
            
            for i in range(lastday_row) :     
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                   
                        temp_name = str(temp_dataframe.iloc[i,0])

                        for k in range (nEMPLOYEE) :
                            if (temp_name == str(EMPLOYEE_t.loc[k,'id'])) : 
                                EMPLOYEE_t.at[k,'NM'] = int(EMPLOYEE_t.iloc[k,9]) + 1    
        
        elif (lastday_ofmonth == "Wed") :

            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-3 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
         
            for i in range(lastday_row) :
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                   
                        temp_name = str(temp_dataframe.iloc[i,0])
                   
                        for k in range (nEMPLOYEE) :
                            if (temp_name == str(EMPLOYEE_t.loc[k,'id'])) : 
                                EMPLOYEE_t.at[k,'NM'] = int(EMPLOYEE_t.iloc[k,9]) + 1

        elif (lastday_ofmonth == "Tue") :
         
            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-2 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
        
            for i in range(lastday_row) :
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                  
                        temp_name = str(temp_dataframe.iloc[i,0])
                   
                        for k in range (nEMPLOYEE) :
                            if (temp_name == str(EMPLOYEE_t.loc[k,'id'])) : 
                                EMPLOYEE_t.at[k,'NM'] = int(EMPLOYEE_t.iloc[k,9]) + 1
        
        elif (lastday_ofmonth == "Mon") : 
        
            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-1 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
        
            for i in range (lastday_row):
                for j in range (len(temp_dataframe.columns)) :
                    if(temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                    
                       temp_name = str(temp_dataframe.iloc[i,0])
                    
                       for k in range (nEMPLOYEE) :
                           if (temp_name == str(EMPLOYEE_t.loc[k,'id'])) : 
                               EMPLOYEE_t.at[k,'NM'] = int(EMPLOYEE_t.iloc[k,9]) + 1



#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# 輸出
# csv:班表、缺工冗員表
# 其他資訊：xlsx檔
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#








#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# 其他工具
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#

"""===========================================
    Text-numberID translate function
==========================================="""
def Tran_t2n(text, names):
    try:
        c = names.index(text)
    except:
        print('Tran_t2n():',text,"not in ",names[0:3],'...')
        c = None
    return c