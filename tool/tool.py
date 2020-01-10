# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar, os
import pandas as pd
import numpy as np
from datetime import datetime, date

"""======================================================
目前發現的問題：上月末日為假日時，斷頭周晚班計算錯誤

======================================================"""

#測試檔案檔名 - 沒有要測試時請留空白
global EmployeeTest, AssignTest, NeedTest, U_ttest
EmployeeTest = ""
AssignTest = ""
NeedTest = ""
U_ttest = ""

"""================================================================================================================
    globle參數
================================================================================================================"""
# 讀檔基本資料
ENCODING = 'utf-8-sig'                  #讀檔格式
DIR = '../data'                         #預設總資料夾檔案路徑
DIR_PER_MONTH = '../data/per_month/'    #每月改變的資料(per_MONTH)的檔案路徑
DIR_PARA = '../data/parameters/'        #parameters的檔案路徑

# 紀錄檔案
RECORD_FILE = './tool/record.log'      #運行紀錄檔案
with open(RECORD_FILE, 'w', encoding='utf-8-sig') as f:      #用with一次性完成open、close檔案
    f.write('tool.py 開始執行：'+str(datetime.now())+'\n\n')

YEAR = 2019
MONTH = 4
TIME_LIMIT = 300
P = [100,0,0,0,0]       #權重，P0是缺工人數

# 各項目總數
nE = 0                  #總員工人數
nD = 0                  #總工作日數
nK = 0                  #班別種類數
nT = 24                 #總時段數
nR = 0                  #午休種類數
nW = 0                  #總週數
mDAY = 0                #本月總日數


# List
# -------對照用的-------#
NAME_list   = []        #員工中文名字
ID_list     = []        #員工ID
DATE_list   = []        #日期
CLASS_list  = []        #班別名稱
BREAK_list  = []        #午休時段名稱(時間)
# -------其他-------#
AH_list     = []        #days after holiday
NAH_list    = []        #不屬於AH_list的日子
POSI_list   = []        #職位高低(低到高)
WEEK_list   = []        #每天各是哪一周
LastWEEK_night = []     #上個月底斷頭周晚班次數
LastDAY_night  = []     #上個月最後一個工作天是否晚班


# Set
# -------員工集合-------#
E_POSI_set    = {}      #某職位以上的員工集合，預設值= '任意':range(nE)
E_SENIOR_set  = {}      #某年資以上的員工集合，無預設值
E_SKILL_set   = {}      #擁有特定技能的員工集合，無預設值
# -------日子集合-------#
D_WEEK_set    = []                                                                #每周有哪些天(Tran後)
D_WDAY_set    = {'Mon':[],'Tue':[],'Wed':[],'Thu':[],'Fri':[],'Sat':[],'Sun':[]}  #周幾有哪些天
# -------班別集合-------#
K_CLASS_set   = {'all':[], 'night':['N1','W6','M1'], 'phone':[]}    #班別分類(只有phone內的班別能減少缺工)
K_BREAK_set   = []                                                  #有哪些午休時段


# 表格資料
# -------一般-------#
Employee_t  = pd.DataFrame()
ClassTime_t = pd.DataFrame()
ASSIGN  = []            #ASSIGN_ijk - 員工i指定第j天須排班別k，形式為 [(i,j,k)]
DEMAND  = []            #DEMAND_jt - 日子j於時段t的需求人數
CONTAIN = []            #CONTAIN_kt - 1表示班別k包含時段t，0則否
# -------限制式相關-------#
LOWER   = []
UPPER   = []
PERCENT = []
NOTPHONE_CLASS = []
NOTPHONE_CLASS_special = []
Upper_shift = []


"""================================================================================================================
工具函式
==============================================================================================================="""
# print到記錄檔
def PRINT(text):
    print(text)
    with open(RECORD_FILE,'a', encoding='utf-8-sig') as f:      #用with一次性完成open、close檔案
        f.write(text+'\n')

# 回報錯誤、儲存錯誤檔案並結束程式
def ERROR(error_text):
    print('\n\n= ! = '+error_text+'\n\n')
    with open('./ERROR.log','w', encoding='utf-8-sig') as f:    #用with一次性完成open、close檔案
        f.write(error_text)
    sys.exit()

# 讀檔：try/except是為了因應條件全空時。 讀檔預設值：空的DataFrame
def readFile(dir, default=pd.DataFrame(), acceptNoFile=False, \
             header_=None,skiprows_=None,index_col_=None,encoding_=ENCODING):
    try:
        t = pd.read_csv(dir, header=header_,skiprows=skiprows_,index_col=index_col_,\
                        encoding=encoding_,engine='python')
        return t
    except FileNotFoundError:
        if acceptNoFile:
            return default
        else:
            ERROR('找不到檔案：'+dir)
    except:
        #encoding='utf-8-sig',
        return default  #有檔案但是讀不了:多半是沒有限制式，使skiprow後為空。 一律用預設值

"""===========================================
index與實際數值轉換
==========================================="""
# text to index
def Tran_t2n(text, aList) -> int:
    try:
        ans = aList.index(text)     #找出 text 在 aList 中的 index，並回傳
    except:
        print('Tran_t2n():', text, 'not in', aList[0:3], '...')
        ans = None
    return ans

# index to text
def Tran_n2t(index:int, aList):
    try:
        ans = aList[index]     #回傳 aList[index] 的值
    except:
        print('Tran_n2t(): index['+str(index)+'] out of range '+\
            '(len of', aList[0:3], '=',len(aList),')')
        ans = None
    return ans



"""================================================================================================================
資料前處理
================================================================================================================"""
"""===========================================
nJ, nW
==========================================="""
#nW
def get_nW(YEAR,MONTH):
	startDay = date(YEAR,MONTH,1).weekday()	#Mon=0,Tue=1...
	totalDay = (date(YEAR,MONTH+1,1) - date(YEAR,MONTH,1)).days if MONTH<12 else 31
	return math.ceil( (totalDay+startDay) / 7 )

#nJ
def get_nDAY(YEAR,MONTH):
	totalDay = (date(YEAR,MONTH+1,1) - date(YEAR,MONTH,1)).days if MONTH<12 else 31
	ans = 0
	for i in range(totalDay):
		ans += (date(YEAR,MONTH,i+1).weekday()<5)
	return ans

#start day
def get_startD(YEAR,MONTH):
	d = date(YEAR,MONTH,1).weekday()
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
def SetVACnext(MONTH_start, nDAY, DATE_list):
    ans = []
    ans2 = []
    #第一天不是1 / 第一天是1
    if DATE_list[0]!=1:
        ans.append(0)
    elif (MONTH_start == 0 and DATE_list[0]==1):
        ans.append(0)
    else:
        ans2.append(0)
    
    
    for i,day in enumerate(DATE_list):
        if i==0:
            continue
        else:
            #我的前一天不是我的數字-1(代表前一天放假)
            if(day-1!=DATE_list[i-1]):
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
Calculation of NW & NM from last MONTH 
"""
def calculate_NW(lastM_Schedule):   
    global K_CLASS_set, ID_list, nE                     #K_CLASS_set是為了取得晚班列表

    lastday_column = -1                                 #最後一行(上月末日)
    for c in range(len(lastM_Schedule.columns)-1,2,-1): #從最後一天倒數(2是為了去掉開頭index、ID、名字三行)
        if lastM_Schedule[c][1] != 'X':                 #如果這一天不是假日的全'X'行，就取之為上月末日
            lastday_column = c
            break
    if lastday_column == -1:
        ERROR('上個月的班表有錯誤，找不到上個月最後一個上班日')

    lastM_ID = lastM_Schedule[0]
    lastday_list = lastM_Schedule[lastday_column]

    ansList = [0] * nE                                  #對應到本月員工的數量
    for i,ID in enumerate(lastM_ID):                    #上月第i人的ID
        c = Tran_t2n(lastday_list[i], CLASS_list)       #取出此人上月末日的班別index
        if c in K_CLASS_set['night']:                   #如果上月末日是晚班，更改回傳值中對應的項
            try:                                        #(找不到人就算了)
                ansList[ Tran_t2n(ID, ID_list) ] = 1                
            except:
                pass    #do nothing
    return ansList
    
def calculate_NM (Employee_t,lastday_ofMONTH,lastday_row,lastday_column,lastMONTH,nEmployee):  
    if (lastday_ofMONTH != "Fri") :
        if (lastday_ofMONTH == "Thu") :
                   
            temp_part1 = lastMONTH.iloc[:, 0]
            temp_part2 = lastMONTH.iloc[:, lastday_column-4 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
            
            for i in range(lastday_row) :     
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                   
                        temp_name = str(temp_dataframe.iloc[i,0])

                        for k in range (nEmployee) :
                            if (temp_name == str(Employee_t.loc[k,'id'])) : 
                                Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1    
        
        elif (lastday_ofMONTH == "Wed") :

            temp_part1 = lastMONTH.iloc[:, 0]
            temp_part2 = lastMONTH.iloc[:, lastday_column-3 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
         
            for i in range(lastday_row) :
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                   
                        temp_name = str(temp_dataframe.iloc[i,0])
                   
                        for k in range (nEmployee) :
                            if (temp_name == str(Employee_t.loc[k,'id'])) : 
                                Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1

        elif (lastday_ofMONTH == "Tue") :
         
            temp_part1 = lastMONTH.iloc[:, 0]
            temp_part2 = lastMONTH.iloc[:, lastday_column-2 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
        
            for i in range(lastday_row) :
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                  
                        temp_name = str(temp_dataframe.iloc[i,0])
                   
                        for k in range (nEmployee) :
                            if (temp_name == str(Employee_t.loc[k,'id'])) : 
                                Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1
        
        elif (lastday_ofMONTH == "Mon") : 
        
            temp_part1 = lastMONTH.iloc[:, 0]
            temp_part2 = lastMONTH.iloc[:, lastday_column-1 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
        
            for i in range (lastday_row):
                for j in range (len(temp_dataframe.columns)) :
                    if(temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                    
                       temp_name = str(temp_dataframe.iloc[i,0])
                    
                       for k in range (nEmployee) :
                           if (temp_name == str(Employee_t.loc[k,'id'])) : 
                               Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1
    return Employee_t




"""================================================================================================================
import data
================================================================================================================"""
# 清除舊的報錯檔案
def _deleteError():
    if os.path.isfile('./ERROR.log'):
        try:
            os.remove('./ERROR.log')
            PRINT('已移除舊的錯誤紀錄檔')
        except:
            PRINT('無法刪除舊的紀錄檔')
    else:
        PRINT('沒有找到舊的錯誤紀錄檔')
    PRINT('tool.py開始讀檔')
_deleteError()

# 讀檔路徑 path.txt
def READ_path():
    global DIR, DIR_PARA, DIR_PER_MONTH
    try:
        with open('./path.txt','r') as f:  #用with一次性完成open、close檔案
            DIR = f.read().replace('\n', '')
    except FileNotFoundError:
        PRINT('找不到path.txt檔案，使用預設路徑')
        DIR = '../data/'   #預設資料路徑：./data/
    except:
        PRINT('打不開path.txt，使用預設路徑')
        DIR = './data/'   #預設資料路徑：./data/
    DIR_PER_MONTH = DIR+'per_month/'
    DIR_PARA = DIR+'parameters/'
    PRINT('Read file from '+DIR_PER_MONTH+' & '+DIR_PARA)
    return None
READ_path()

#=============================================================================#
# 讀取參數
#=============================================================================#
# 讀取參數
def READ_parameters(path=DIR_PARA):
    global P, TIME_LIMIT,   nK, nR,   BREAK_list, CLASS_list, POSI_list
    global K_CLASS_set, K_BREAK_set,   CONTAIN, ClassTime_t

    # weight p1~4
    Weight_t    = readFile(path+'weight_p.csv', index_col_=0)        #權重
    P[1]        = Weight_t[1]['P1']             #目標式中的調整權重(surplus)
    P[2]        = Weight_t[1]['P2']             #目標式中的調整權重(nightCount)
    P[3]        = Weight_t[1]['P3']             #目標式中的調整權重(breakCount)
    P[4]        = Weight_t[1]['P4']             #目標式中的調整權重(noonCount)

    # class time
    ClassTime_t = readFile(path+'fixed/fix_class_time.csv', header_=0, index_col_=[0])  #class-time table
    CLASS_list  = list(ClassTime_t.index)
    nK = len(CLASS_list)                        #班別種類數
    CONTAIN = ClassTime_t.values.tolist()       #CONTAIN_kt - 1表示班別k包含時段t，0則否

    # class set
    KSet_t      = readFile(path+'fixed/fix_classes.csv', index_col_=[0])                    #class set
    for ki in range(len(KSet_t)):               #將檔案中的班別集合登錄成dict
        K_CLASS_set[KSet_t.index[ki]] = [ Tran_t2n(x, CLASS_list) for x in KSet_t.iloc[ki].dropna().values ]
    for ki in range(nK):
        K_CLASS_set[CLASS_list[ki]] = [ki]      #每個班別自身也都是獨立的(單一元素)集合

    # rest set
    RSet_t      = readFile(path+'fixed/fix_resttime.csv', index_col_=[0])               #rest set
    nR = RSet_t.shape[0]         #午休種類數
    for ki in range(nR):
        BREAK_list.append( str(RSet_t.index[ki]) )
        K_BREAK_set.append( [ Tran_t2n(x, CLASS_list) for x in RSet_t.iloc[ki].dropna().values ] )

    # position
    POSI_list   = readFile(path+'fixed/position.csv').iloc[0].tolist()  #職位高低(低到高)
    
    # time limit
    try:
        TIME_LIMIT = readFile(path+'time_limit.csv', header_=0)
    except:
        print('\n無法讀取time_limit.csv，改用預設時間限制\n')
READ_parameters()

#=============================================================================#
# 讀取 per_MONTH
#=============================================================================#
def READ_per_MONTH(path=DIR_PER_MONTH):
    #要改的
    global YEAR, MONTH,   nW, mDAY, nE
    global NAME_list, ID_list,   LastWEEK_night, LastDAY_night,   AH_list, NAH_list, WEEK_list
    global D_WDAY_set, D_WEEK_set,   E_SKILL_set, E_POSI_set
    global ASSIGN, DEMAND, Employee_t
    #要用的
    global nD, DATE_list, CLASS_list
    

    # Date
    Date_t = readFile(path+'Date.csv', index_col_ = 0)
    try:
        YEAR = int(Date_t.iloc[0,0])
        MONTH = int(Date_t.iloc[1,0])
        PRINT('讀取 '+str(YEAR)+' 年 '+str(MONTH)+' 月資料\n')
    except:
        ERROR('日期不能為空值，請確認 Date.csv 檔案')
    nW = get_nW(YEAR,MONTH)                         #總週數
    mDAY = int(calendar.monthrange(YEAR,MONTH)[1])  #本月總日數

    
    # Employee
    Employee_t  = readFile(path+'Employee'+EmployeeTest+'.csv', header_ = 0)
    Employee_t['ID'] = [ str(x) for x in Employee_t['ID'] ]           

    nE          = Employee_t.shape[0]
    NAME_list   = list(Employee_t['Name_Chinese'])                                  #對照名字與員工index用
    ID_list     = list(Employee_t['ID'])                                            #對照ID與員工index用

    SKILL_NAME  = list(filter(lambda x: re.match('skill-',x), Employee_t.columns))  #自動讀取技能名稱
    E_SKILL_set = SetSKILL(Employee_t[ SKILL_NAME ])                                #特定技能的員工集合

    E_POSI_set  = SetPOSI(Employee_t['Position'], POSI_list)                        #某職稱以上的員工集合      
    

    # Schedule (NM 及 NW 從人壽提供之上個月的班表裡面計算)
    if MONTH>1:
        Schedule_t = readFile(path+'Schedule_'+str(YEAR)+'_'+str(MONTH-1)+'.csv', skiprows_=[0])
    else:
        Schedule_t = readFile(path+'Schedule_'+str(YEAR-1)+'_12.csv', skiprows_=[0])
    Schedule_t[0] = [ str(x) for x in Schedule_t[0] ]   #強制將ID設為string
    
    lastday_column = len(Schedule_t.columns)            #最後一行(上月末日)
    lastday_ofMONTH = Schedule_t.iloc[0, lastday_column-1]
    lastday_row     = Schedule_t.shape[0]   
    #上個月的最後一天有排晚班者是1，沒有則是0
    # Employee_t['NW'] = 
    LastDAY_night  = calculate_NW(Schedule_t)     #上月末日
    #!!!!!計算上月底晚班狀況!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Employee_t = calculate_NW(Employee_t,lastday_ofMONTH,lastday_row,lastday_column,Schedule_t,nE)
    #上月底的斷頭週，計算該斷頭週總共排了幾次晚班
    Employee_t['NM'] = pd.DataFrame([0] * nE)
    calculate_NM(Employee_t,lastday_ofMONTH,lastday_row,lastday_column,Schedule_t,nE)
    LastWEEK_night = list(Employee_t['NM'].values)     #上月底斷頭周


    # Need
    Need_t = readFile(path+'Need'+NeedTest+'.csv', header_=0, index_col_=0).T
    DATE_list = [ int(x) for x in Need_t.index ]                    #所有的日期 - 對照用
    nD = len(DATE_list)                                             #總工作日數
    DEMAND = [list(map(int,l)) for l in Need_t.values.tolist()]     #DEMAND_jt - 日子j於時段t的需求人數(int)

    MONTH_start = get_startD(YEAR,MONTH)                            #本月第一天是禮拜幾 (Mon=0, Tue=1..)
    AH_list, NAH_list = SetVACnext(MONTH_start, nD, DATE_list)      #VACnextdayset - 假期後或週一的日子集合
    D_WEEK_set  = SetDAYW(MONTH_start+1,mDAY,nW, list(range(nD)), DATE_list)    #第 w 週包含的日期集合
    D_WDAY_set  = SetDAY(MONTH_start, nD, DATE_list)                #DAYset - 通用日子集合 [all,Mon,Tue...]
    WEEK_list   = SetWEEKD(D_WEEK_set, nW)                          #WEEK_list - 日子j所屬的那一週 


    # Assign
    Assign_t = readFile(path+'Assign'+AssignTest+'.csv', skiprows_=[0])
    Assign_t[0] = [ str(x) for x in Assign_t[0] ]                   #強制將ID設為string
    Assign_t[1] = [ int(x) for x in Assign_t[1] ]                   #強制將日期設為int
    Assign_t[2] = [ str(x) for x in Assign_t[2] ]                   #強制將班別設為string
    for c in range(Assign_t.shape[0]):
        e = Tran_t2n(Assign_t.iloc[c,0], ID_list)
        d = Tran_t2n(Assign_t.iloc[c,1], DATE_list)
        k = Tran_t2n(Assign_t.iloc[c,2], CLASS_list)
        #回報錯誤:轉換出來為None
        if e!=e:    #若為None，則自身會不相等
            ERROR('指定排班表中發現不明ID：',Assign_t.iloc[c,0],\
                '不在員工資料的ID列表中，請再次確認ID正確性（包含大小寫、空格、換行）')
        if d!=d:
            ERROR('指定排班的日期錯誤：',Assign_t.iloc[c,1],\
                '不是上班日（上班日指有進線預測資料的日子）')
        if k!=k:
            ERROR('指定排班中發現不明班別：',Assign_t.iloc[c,2],\
                '不在登錄的班別中，請指定班別列表中的一個班別（注意大小寫）')
        ASSIGN.append( (e, d, k) )
READ_per_MONTH()

#=============================================================================#
# 讀取限制式
#=============================================================================#
def READ_limits(path=DIR_PARA):
    #要改的
    global E_SENIOR_set,   LOWER, UPPER, PERCENT,   NOTPHONE_CLASS, NOTPHONE_CLASS_special, Upper_shift
    #要用的
    global Employee_t 
    # -------讀取限制式-------#
    # lower
    LOWER = readFile(path+'lower_limit.csv',skiprows_=[0]).values.tolist()     #日期j，班別集合ks，職位p，上班人數下限
    for i in range(len(LOWER)):
        d = Tran_t2n( LOWER[i][0], DATE_list)
        LOWER[i][0] = d
    

    # upper
    Upper_t     = readFile(path+'upper_limit'+U_ttest+'.csv', skiprows_=[0])   #指定星期幾、班別，人數上限
    Upper_t[0]  = [ str(x) for x in Upper_t[0] ]                    #強制將ID設為string
    #UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
    for c in range(Upper_t.shape[0]):
        e = Tran_t2n(Upper_t.iloc[c,0], ID_list)
        #回報錯誤
        if e==None:
            print('指定排班表中發現不明ID：',Upper_t.iloc[c,0],\
                '不在員工資料的ID列表中，請再次確認ID正確性（包含大小寫、空格、換行）')
        UPPER.append( [e, Upper_t.iloc[c,1], Upper_t.iloc[c,2], Upper_t.iloc[c,3]] )


    # senior
    Senior_t    = readFile(path+'senior_limit.csv', skiprows_=[0])
    PERCENT = Senior_t.values.tolist()   #PERCENT - 日子集合，班別集合，要求占比，年資分界線      
    try:   #為了因應條件全空時
        SENIOR_bp = Senior_t[3]
    except:
        SENIOR_bp = []
    E_SENIOR_set = [SetSENIOR(Employee_t['Senior'],tmp) for tmp in SENIOR_bp] #達到特定年資的員工集合


    # skill lower limit
    SKset_t     = readFile(path+'skill_class_limit.csv',header_=0)            #class set for skills
    NOTPHONE_CLASS = []                 # 特殊班別每天人數相同
    NOTPHONE_CLASS_special = []         # 特殊班別假日後一天人數不同
    for i in range(SKset_t.shape[0]):
        if(SKset_t['Special'][i]==1):
            tmp = SKset_t.iloc[i].values.tolist()
            del tmp[3]
            NOTPHONE_CLASS_special.append(tmp)
        else:
            tmp = SKset_t.iloc[i].values.tolist()
            del tmp[3]
            del tmp[3]
            NOTPHONE_CLASS.append(tmp)

    # skill upper limit
    Upper_shift = readFile(path+'class_upperlimit.csv', skiprows_=[0]).values.tolist()
READ_limits()





"""================================================================================================================
輸出
    csv:班表、缺工冗員表
    其他資訊：xlsx檔
================================================================================================================"""
class OUTPUT:
    def __init__(self, table, year=YEAR, month=MONTH):
        PRINT('\n'+str(datetime.now())+'  開始輸出班表\n')

        #-------運算用-------#
        self.year = year
        self.month = month
        self.mDAY = int(calendar.monthrange(YEAR,MONTH)[1])         #本月總日數
        self.WorkList, self.Schedule = self._calculateClass(table)  #數字工作列表 & 文字的班表(不計假日)
        self.LackOverList = self._calculateLackAndOver()            #缺工冗員表(不計假日)

        #-------輸出文字用-------#
        ym = '_'+str(self.year)+'_'+str(self.month)
        self.outputName = {             #輸出檔名
            'main': './Schedule'+ym+'.csv',
            'sub':  './lack&over'+ym+'.csv',
            'all':  './schedule_data'+ym+'.xlsx',
            }
        self.T_type = ['09:00','09:30','10:00','10:30','11:00','11:30','12:00','12:30',\
                       '13:00','13:30','14:00','14:30','15:00','15:30','16:00','16:30',\
                       '17:00','17:30','18:00','18:30','19:00','19:30','20:00','20:30']
        self.date_name = []             #產生日期清單
        for i in range(1, mDAY+1): 
            date    = datetime(self.year, self.month, i)
            weekday = Tran_n2t(date.weekday(), list('一二三四五六日'))
            self.date_name.append(date.strftime("%m/%d")+' ('+weekday+')')
    
    #============================================================================#
    # 內部函數
    #============================================================================#
    #依據不同的傳入table型態，使用不同的判定式
    def _isT(item, item2=None):
        if isinstance( item2, (int,float,bool) ):
            v = item2           #gurobi接到的會是item=<某位址> item2=bool值
        else:
            v = item2.x         #gurobi接到的會是item=<某位址> item2=<gurobi.Var (value 1.0)>
        if v==1 or v:
            return True
        else:
            return False

    # 計算誰哪天值哪個班，輸出：(數字班表[i,j]，文字班表[i,j])
    def _calculateClass(self, table):   #前加底線能讓函式在簡單import時被忽略(似private效果)
        global nE, nD, nK, ID_list, DATE_list
        
        try:
            table[0,0,0].x      #如果table[0,0,0]是gurobi var,這行就能執行；否則報錯
            PRINT('＊輸出 gurobi solver 結果')
        except:
            PRINT('＊輸出 基因演算法 結果')
        #計算
        work_list = []                                  #員工值的班別(數字)
        work_text = []                                  #員工值的班別(文字)  
        error = 0                                       #發生錯誤的個數      
        for i in range(nE):
            tmp_i = []                                  #每個員工本月的班(數字)
            tmp_t = []                                  #每個員工本月的班(文字)
            for j in range(nD):
                OK = False                              #判斷是否有找到班別
                for k in range(nK):
                    if self._isT(table[i,j,k]):         #找到班別了
                        tmp_i.append(k)
                        tmp_t.append(CLASS_list[k])
                        OK = True
                        break
                if not OK:                              #沒找到班別，填入預設值
                    if error < 5:
                        tmp_i.append(1)
                        tmp_t.append(CLASS_list[1])
                        PRINT(ID_list[i]+' 在 '+str(DATE_list[j])+' 號的排班發生錯誤。')
                        error += 1
                    else:
                        ERROR('無法排出班表，請確認限制式是否衝突')  #錯誤過多就視為沒救了
            work_list.append(tmp_i)
            work_text.append(tmp_t)
        if error > 0: 
            PRINT('\n= ! = 部分班表尚未排完，目前已使用預設班別('+CLASS_list[1]+')補上。\n'+\
                  '      建議將 time_limit 調高後，重新執行程式。\n')
        #回傳
        return (work_list, pd.DataFrame(work_text, index = ID_list, columns = DATE_list) )
    
    # 計算缺工(-)冗員(+)人數
    def _calculateLackAndOver(self):
        global nE, nD, nT, DEMAND, K_CLASS_set, ClassTime_t
        #計算實際人數與需求的差距
        people = np.zeros((nD,nT), dtype=np.int)        #空表格預設填0(int)
        for i in range(nE):
            for j in range(nD):
                c = self.WorkList[i][j]                 #此人此日上哪個班別(index)
                if c in K_CLASS_set['phone']:
                    people[j] += ClassTime_t.values[c]  #list(逐項)相加
        output_people = (people - DEMAND).tolist()      #矩陣(逐項)相減
        return output_people

    # 假日補'X'，輸出：補好的DatFrame
    def _addHoliday(self, table, index_list:list, index_name='', fill='X'):
        global mDay, DATE_list
        if isinstance(table,list):                      #isinstance()才能把多層list判斷成list
            Holiday = [fill] * len(table[0])            #假日填入預設值
        else:
            table.columns = range(table.shape[1])       #將table的column name弄成流水號
            Holiday = [fill] * table.shape[0]           #假日填入預設值
        df = pd.DataFrame({index_name: index_list})
        df.set_index(index_name, inplace=True)
        j = 0
        for i in range(0,mDAY):                     #本月所有日期
            if (i+1) not in DATE_list:              #不是上班日，就填X
                df[self.date_name[i]] = Holiday
            else:
                df[self.date_name[i]] = table[j]
                j += 1
        return df

    # 午晚班次數，輸出：([未加權次數]，[加權次數])
    def _classCount(self, classSet='night', weightList=[1]*nE):
        global ID_list, NAME_list, K_CLASS_set
        #指定班型月總計次數
        work_total = []                             # 每人本月排此種班型的次數(未加權)
        countList  = []                             # 每人本月排此種班型的次數(加權)
        for i,c in enumerate(self.WorkList):        # i = 誰(index), c = 此人本月班表(list)
            count   = 0                             # 本月指定班型值班次數，初始值=0
            w_count = 0                             # 本月指定班型值班次數(加權)，初始值=0
            if (weightList[i]>0):                   # 權重 > 0 才拿來除 (實際意義：此人每周值班上限>0)
                for j in c:                         # j = 此人本日的班表
                    if j in K_CLASS_set[classSet]:  # 若此人此日值指定班型，本月值班次數+1
                        count = count + 1
                w_count = count / weightList[i]     #計算本月(加權)總計，預設加權值=1
            countList.append(w_count)               #總表加入此人的本月總計(即使加權值=0也要加)
            work_total.append(count)                #work_total加上本月值班次數(未加權)
        #輸出
        maxCount = max(countList)                   #值指定班型最多(加權值)的人的次數
        PRINT('值 '+classSet+' 班型的加權次數最高者，本月共值： '+str(maxCount)+' 次(加權後)')
        return (work_total, countList)
    
    # 純缺工表，輸出DataFrame：(純缺工，日百分比，時段百分比)
    def _printLack(self):
        global nD, DEMAND, DATE_list

        #-------缺工------#
        lesspeople_count = []
        for j in range(nD):
            tmp = []
            for x in self.LackOverList[j]:
                tmp.append( (-1*x if x<0 else 0) )  #有冗員時，缺工人數計為0
            lesspeople_count.append(tmp)
        df_lack = pd.DataFrame(lesspeople_count, index=DATE_list, columns=self.T_type)

        #----缺工總和----#
        df_lack['日總和'] = df_lack.sum(axis=1)
        df_lack.loc['時段總和'] = df_lack.sum()

        #----缺工比例----#
        demand_day  = pd.DataFrame(DEMAND).sum(axis=1).values     #每日總需求
        demand_time = pd.DataFrame(DEMAND).sum().values           #時段總需求
        less_percent_day  = (df_lack['日總和'].drop(['時段總和']).values) / demand_day
        less_percent_time = (df_lack.loc['時段總和'].drop(['日總和']).values) / demand_time
        df_percent_day    = pd.DataFrame(less_percent_day,  index= DATE_list,   columns=["Percentage"])
        df_percent_time   = pd.DataFrame(less_percent_time, index= self.T_type, columns=["Percentage"])

        #----缺工冗員最大值----#
        surplus = 0
        for i in self.LackOverList:
            for j in i:
                if j > surplus:
                    surplus = j
        PRINT("\n所有天每個時段人數與需求人數的差距中的最大值 = "+str(int(surplus))+"\n")

        #輸出
        return (df_lack, df_percent_day, df_percent_time)

    # 每周休息時間，輸出：DataFrame
    def _breakCount(self):
        global nE, nD, nW, NAME_list, BREAK_list, WEEK_list
        breakCount = np.zeros((nE,nW,5), dtype=np.int)      #建立空表格
        for i in range(nE):
            for j in range(nD):
                w_d = WEEK_list[j]
                for r,l in enumerate(K_BREAK_set):          #對每一種休息時間
                    if self.WorkList[i][j] in l:            #如果此人此天的班別屬於此種休息時間
                        breakCount[i][w_d][r] = 1           #就把休息時間的項目紀錄為1，並跳出
                        break
        breakcount = int(sum(sum(sum(breakCount))))
        which_week = [tmp+1 for tmp in range(nW)] 
        which_resttime = []     
        for i in range(nE):
            tmp = []
            for w in range(nW):
                tmp2 = []
                for r in range(nR):
                    if(breakCount[i][w][r]==1):
                        tmp2.append(BREAK_list[r])
                tmp.append(tmp2)
            which_resttime.append(tmp)
        df_resttime = pd.DataFrame(which_resttime, index=NAME_list, columns=which_week)
        #輸出
        return df_resttime


    #============================================================================#
    # 輸出
    #============================================================================#
    # 輸出班表檔案
    def printSchedule(self, makeFile=True):
        global NAME_list, ID_list
        df = self._addHoliday(self.Schedule, ID_list, 'ID')   #假日補X
        df.insert(0, 'Name', NAME_list)                       #加上員工名字
        if makeFile: df.to_csv(self.outputName['main'], encoding="utf-8_sig")
        return df

    # 輸出冗員與缺工人數表
    def printLackAndOver(self, makeFile=True):
        new_2 = self._addHoliday(self.LackOverList, self.T_type, 'time')    #假日補X
        if makeFile: new_2.to_csv(self.outputName['sub'], encoding="utf-8_sig")
        return new_2
    
    # 輸出綜合資訊
    def printAll(self, makeFile=False):
        global nE, nD, nW, DEMAND, DATE_list, Employee_t, BREAK_list, WEEK_list

        # 缺工
        df_lack, df_L_pDay, df_L_pTime = self._printLack()  #三個DataFrame:(純缺工，日百分比，時段百分比)

        # 午、晚班次數
        noon, noonWeight   = self._classCount(classSet='noon')
        night, nightWeight = self._classCount(classSet='night', weightList=Employee_t['night_perWeek'])
        df_classCount = pd.DataFrame({'ID':ID_list, 'Name':NAME_list, '午班次數':noon, '晚班次數':night})
        df_classCount.set_index('ID', inplace=True)

        # 休息時間種類
        df_rest = self._breakCount()

        # 輸出
        df = self.printSchedule(makeFile=makeFile)
        df_lackover = self.printLackAndOver(makeFile=makeFile)
        with pd.ExcelWriter(self.outputName['all']) as writer:
            df.to_excel(writer, sheet_name="班表")
            df_lackover.to_excel(writer, sheet_name="缺工冗員表")
            df_lack.to_excel(writer, sheet_name="缺工人數")           
            df_L_pDay.to_excel(writer, sheet_name="每天缺工百分比")
            df_L_pTime.to_excel(writer, sheet_name="各時段缺工百分比")
            df_classCount.to_excel(writer, sheet_name="午、晚班次數")
            df_rest.to_excel(writer, sheet_name="每週休息時間")
        PRINT('\nOutput results has save as '+self.outputName['all']+'\n')
        return (df, df_lackover)
#end class OUTPUT





# ================================================================================================================
# 確認
def READ_CHECK():
    PRINT('\n\n=== 參數確認 ===')
    PRINT('nE='+str(nE)+', nD='+str(nD)+', nK='+str(nK)+', nT='+str(nT)+\
          ', nR='+str(nR)+', nW='+str(nW)+', mDAY='+str(mDAY)+'\n')
    print('DATE_list=',DATE_list)
    print('CLASS_list=',CLASS_list)
    print('ID_list=',ID_list)
    # print('NAME_list=',NAME_list)
    # print('AH_list=',AH_list)
    # print('POSI_list=',POSI_list)
    print('LastWEEK_night=',LastWEEK_night)
    print('LastDAY_night=',LastDAY_night)
    # print('\n')

    # -------Set-------#
    # print('E_POSI_set=',E_POSI_set)
    # print('E_SENIOR_set=',E_SENIOR_set)
    # print('E_SKILL_set=',E_SKILL_set)
    # print('D_WEEK_set=',D_WEEK_set)
    # print('D_WDAY_set=',D_WDAY_set)
    # print('K_CLASS_set=',K_CLASS_set)
    # print('K_BREAK_set=',K_BREAK_set)
    # print('\n\n')
    
    # -------表格-------#
    # print('CONTAIN=',CONTAIN,'\n')
    # print('Employee_t=',Employee_t,'\n')
    # print('DEMAND=',DEMAND,'\n')
    # print('ASSIGN=',ASSIGN)
    
    # -------限制式-------#
    # print('LOWER=', LOWER)
    # print('UPPER=', UPPER)
    # print('PERCENT=', PERCENT)
    # print('NOTPHONE_CLASS=', NOTPHONE_CLASS)
    # print('NOTPHONE_CLASS_special=', NOTPHONE_CLASS_special)
    # print('Upper_shift=', Upper_shift)
    PRINT('=== ======= ===')
READ_CHECK()

# 結束
PRINT('\n= tool_test.py import successfully =\n\n')
