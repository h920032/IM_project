#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
For caculate weekdays
@author: Ting
"""
import math
import pandas as pd
from datetime import datetime, date

K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']


"""===========================================
	nJ, nW
==========================================="""
# get weekday of 1st date and total days
# startDay = date(year,month,1).weekday()	#Mon=0,Tue=1...
# totalDay = (date(year,month+1,1) - date(year,month,1)).days if month<12 else 31
# print(year,'/',month,' start in weekday',startDay,', total= ',totalDay,' days')

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
#JW 第w周包含的日子集合
#JW 無國定假日的話
def SetDAYW(day, total_day, total_week):   #第一天上班是星期幾/幾天/幾週
    ans = []
    count  = 0
    for i in range(total_week):
        tmp = []
        if(i == 0):
            for j in range(6-day):
                tmp.append(count)
                count+=1
        else:
            for j in range(5):
                tmp.append(count)
                count+=1
                if count == total_day:
                    ans.append(tmp)
                    break
        ans.append(tmp)
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
def SetDAY(day, total_day):   #第一天上班是星期幾/幾天
    set = {'all':list(range(total_day))}
    set['Mon']=[]; set['Tue']=[]; set['Wed']=[]
    set['Tru']=[]; set['Fri']=[]
    # 所有周一，所有週二，所有週三...
    w = ['Mon','Tue','Wed','Tru','Fri']
    for i in range(total_day):
        set[ w[(i+day)%5] ].append(i)
    return set


"""===========================================
	Set Const Functions
==========================================="""
#SKILL 每個技能的員工組合
def SetSKILL(matrix):
	skills = ['phone','CD','chat','outbound']
	ans = {}
	for s in skills:
		alist = matrix['skill-'+s]
		ans[s] = []
		for i in range(len(alist)):
			if alist[i]==1:
				ans[s].append(i)
	return ans

#POSI 每個職位的員工組合
def SetPOSI(alist):
	n = len(alist)
	s = {'任意':list(range(n)),'專員':[],'襄理':[],'副理':[],'主任':[]}
	for i in range(n):
		s[ alist[i] ].append(i)
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
def TranK_t2n(text):
	K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
	try:
		c = K_type.index(text)
	except:
		print('class indexr to class name code:',text,"-> ?")
		c = None
	return  c

def TranName_t2n(text, names):
	try:
		c = names.index(text)
	except:
		print('index to name:',text,"-> ?")
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
    
#    print (EMPLOYEE_t["NM"])
