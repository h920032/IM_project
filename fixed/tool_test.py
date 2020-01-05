# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys
import pandas as pd
from datetime import datetime, date

"""======================================================
@author: 林亭
這是為測試不同的case而準備的，不影響主程式，
請不要理這個檔案，也不要亂動！

======================================================"""

"""================================================================================================================
    globle參數

    讀檔：
        per_month / Date, Schedule, Need, Employee, Assign
            =>      參數
        para /  class_time, class_kind, class_skill    
    表格：
================================================================================================================"""

# 基本資料
RECORD_FILE = open('record.log', 'w')   #運行紀錄檔案
YEAR = 0
MONTH = 0

# 各項目總數
nE = 0      #總員工人數
nD = 0      #總日數
nK = 0      #班別種類數
nT = 24     #總時段數
nR = 0      #午休種類數
nW = 0      #總週數
mDAY = 0    #本月總日數
# nE = EMPLOYEE_t.shape[0]     #總員工人數
# nD = len(DEMAND_t.index)     #總日數
# nK = A_t.shape[0]            #班別種類數
# nT = 24                      #總時段數
# nR = Rset_t.shape[0]         #午休種類數
# nW = tl.get_nW(year,month)   #總週數
# mDAY = int(calendar.monthrange(YEAR,MONTH)[1]) #本月總日數

# 對照用的list
NAME_list   = []
ID_list     = []
DATE_list   = []
CLASS_list  = []
# K_type = Kset_t.iloc[0].tolist()

# 輸出檔名
Schedule_FileName = 'Schedule_'+str(YEAR)+'_'+str(MONTH)+'.csv'
LackOver_FileName = 'lack_'+str(YEAR)+'_'+str(MONTH)+'.csv'

# 資料






"""================================================================================================================
    工具函式
    (全大寫為內部函式)
==============================================================================================================="""
"""===========================================
    Error Handling
==========================================="""
# print到記錄檔
def PRINT(text):
    print(text)
    RECORD_FILE.write(text)

# 回報錯誤、儲存錯誤檔案並結束程式
def ERROR(error_text):
    PRINT('\n\n= ! = '+error_text+'\n\n')
    sys.exit()

"""===========================================
    index與實際數值轉換
==========================================="""
# text to index
def Tran_t2n(text, aList):
    try:
        ans = aList.index(text)     #找出 text 在 aList 中的 index，並回傳
    except:
        print('Tran_t2n():', text, 'not in', aList[0:3], '...')
        ans = None
    return ans

# index to text
def Tran_n2t(index, aList):
    try:
        ans = aList[index]     #回傳 aList[index] 的值
    except:
        print('Tran_n2t(): index['+str(index)+'] out of range '+\
            '(len of', aList[0:3], '=',len(aList),')')
        ans = None
    return ans


"""===========================================
    讀檔相關
==========================================="""
# 讀檔：try/except是為了因應條件全空時
def readFile(dir, header_=None, skiprows_=[0], index_col_=None):
    try:
        t = pd.read_csv(dir, header=header_,skiprows=skiprows_,index_col=index_col_,\
            encoding='utf-8-sig',engine='python')
    except:
        t = pd.DataFrame()
    return t





"""================================================================================================================
    import data
        要讀的檔案：
            per_month/  Date, Need, Employee, 上月排班(Scheduling_年_月), Assign
                              | 儲存日期list
                                    | 儲存員工名字、ID list
                                    | 用ijk的len()開大表格
                                               | 計算 上月末日、上月斷尾周 的晚班數
                                                                         | Assign一邊讀一邊填入
                                                                         | 防呆：指定排班與晚班數量衝突
================================================================================================================"""



#=============================================================================#
#file path
#=============================================================================#
#讀檔路徑import data
try:
    f = open('../../path.txt', "r")
    dir_name = '../../'+f.read().replace('\n', '')
except:
    dir_name = './data/'   #預設資料路徑：./data/

print('Read file from',dir_name)


#=============================================================================#
#每月更改的資料
#=============================================================================#
# year/month
date = pd.read_csv(dir_name + 'per_month/Date.csv', header = None, index_col = 0)
year = int(date.iloc[0,0])
month = int(date.iloc[1,0])

#指定排班
# M_t = readFile(dir_name + 'per_month/Assign.csv')
M_t = readFile(dir_name + 'per_month/Assign'+AssignTest+'.csv')
M_t[0] = [ str(x) for x in M_t[0] ]           #強制將ID設為string
#進線需求預估
# DEMAND_t = pd.read_csv(dir_name+"per_month/Need.csv", header = 0, index_col = 0, engine='python').T
DEMAND_t = pd.read_csv(dir_name+"per_month/Need"+NeedTest+".csv", header = 0, index_col = 0, engine='python').T
DATES = [ int(x) for x in DEMAND_t.index ]    #所有的日期 - 對照用

#employees data
# EMPLOYEE_t = pd.read_csv(dir_name+"per_month/Employee.csv", header = 0) 
EMPLOYEE_t = pd.read_csv(dir_name+"per_month/Employee"+EmployeeTest+".csv", header = 0) 
E_NAME = list(EMPLOYEE_t['Name_English'])       #E_NAME - 對照名字與員工index時使用
E_ID = [ str(x) for x in EMPLOYEE_t['ID'] ]     #E_ID - 對照ID與員工index時使用
E_SENIOR_t = EMPLOYEE_t['Senior']
E_POSI_t = EMPLOYEE_t['Position']
SKILL_NAME = list(filter(lambda x: re.match('skill-',x), EMPLOYEE_t.columns)) #自動讀取技能名稱
E_SKILL_t = EMPLOYEE_t[ SKILL_NAME ]            #員工技能表

"""
#=============================================================================#
#半固定參數
#=============================================================================#
P_t = pd.read_csv(dir_name + 'parameters/weight_p1-4.csv', header = None, index_col = 0, engine='python') #權重
SKset_t = pd.read_csv(dir_name + 'parameters/skills_classes.csv', header = None, index_col = 0)  #class set for skills
L_t = readFile(dir_name + "parameters/lower_limit.csv")                          #指定日期、班別、職位，人數下限
U_t = readFile(dir_name + "parameters/upper_limit.csv")                          #指定星期幾、班別，人數上限
Ratio_t = readFile(dir_name + "parameters/senior_limit.csv")                     #指定年資、星期幾、班別，要占多少比例以上
try:    # 下面的try/except都是為了因應條件全空時
    SENIOR_bp = Ratio_t[3]
except:
    SENIOR_bp = []
try:
    timelimit = pd.read_csv(dir_name + "parameters/time_limit.csv", header = 0, engine='python')
except:
    timelimit = 300 #預設跑五分鐘
nightdaylimit = EMPLOYEE_t['night_perWeek']


#=============================================================================#
#固定參數：班別總數與時間
#=============================================================================#
Kset_t = pd.read_csv(dir_name + 'fixed/fix_classes.csv', header = None, index_col = 0) #class set
A_t = pd.read_csv(dir_name + 'fixed/fix_class_time.csv', header = 0, index_col = 0)

"""





"""================================================================================================================
    資料前處理
================================================================================================================"""


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



"""================================================================================================================
    輸出
        csv:班表、缺工冗員表
        其他資訊：xlsx檔
================================================================================================================"""





# ================================================================================================================
 
# 寫入 This is a testing! 到檔案
print >>fp, "This is a testing!"
 
# 關閉檔案
RECORD_FILE.close()
print('tool_test.py import successfully\n')
sys.exit()