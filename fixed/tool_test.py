# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, re, sys, calendar
import pandas as pd
from datetime import datetime, date

"""======================================================
@author: 林亭
這是為測試不同的case而準備的，不影響主程式，
請不要理這個檔案，也不要亂動！


目前發現的問題：
    上月末日為假日時，晚班計算錯誤
    D_WEEK_set 格式為 list

======================================================"""

"""================================================================================================================
    globle參數
================================================================================================================"""
# 基本資料
DIR = '../data'                         #預設總資料夾檔案路徑
DIR_PER_MONTH = '../data/per_month/'    #每月改變的資料(per_month)的檔案路徑
DIR_PARA = '../data/parameters/'        #parameters的檔案路徑
RECORD_FILE = open('record.log', 'w', encoding='utf-8-sig')   #運行紀錄檔案

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
NAME_list   = []        #員工英文名字
ID_list     = []        #員工ID
DATE_list   = []        #日期
CLASS_list  = []        #班別名稱
# -------其他-------#
AH_list     = []        #days after holiday
NAH_list    = []        #不屬於AH_list的日子
POSI_list   = []        #職位高低(低到高)
LastWEEK_night = []     #上個月底斷頭周晚班次數
LastDAY_night  = []     #上個月最後一個工作天是否晚班


# Set
# -------員工集合-------#
E_POSI_set    = {}      #某職位以上的員工集合，預設值= '任意':range(nE)
E_SENIOR_set  = {}      #某年資以上的員工集合，無預設值
E_SKILL_set   = {}      #擁有特定技能的員工集合，無預設值
# -------日子集合-------#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! D_WEEK_set 實際上是週號的list !!!!
D_WEEK_set    = {}                                                                #每周有哪些天(Tran後)
D_WDAY_set    = {'Mon':[],'Tue':[],'Wed':[],'Thu':[],'Fri':[],'Sat':[],'Sun':[]}  #周幾有哪些天
# -------班別集合-------#
K_CLASS_set   = {'all':[], 'night':['N1','W6','M1'], 'phone':[]}    #班別分類(只有phone內的班別能減少缺工)
K_BREAK_set   = {}                                                  #有哪些午休時段(時段:此時段的班別index)


# 表格資料
# -------一般-------#
Employee_t = pd.DataFrame()
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
    (全大寫為內部函式)
==============================================================================================================="""
"""===========================================
    Error Handling
==========================================="""
# print到記錄檔
def PRINT(text):
    print(text)
    RECORD_FILE.write(text+'\n')

# 回報錯誤、儲存錯誤檔案並結束程式
def ERROR(error_text):
    PRINT('\n\n= ! = '+error_text+'\n\n')
    sys.exit()

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

"""===========================================
    讀檔工具
==========================================="""
# 讀檔：try/except是為了因應條件全空時
def readFile(dir, header_=None, skiprows_=None, index_col_=None):
    # PRINT('Read '+dir)
    try:
        t = pd.read_csv(dir, header=header_,skiprows=skiprows_,index_col=index_col_,\
            encoding='utf-8-sig',engine='python')
    except FileNotFoundError:
        ERROR('找不到檔案：'+dir)
    except:
        t = pd.DataFrame()
    return t



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
def calculate_NW (Employee_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEmployee):	
    global K_CLASS_set  #為了取得晚班列表
    for i in range (lastday_row):
        c = lastmonth.iloc[i, lastday_column]
        if c in K_CLASS_set['night']:     #偵測到上月末日的晚班
        # if( c == "N1" or c == "M1" or c == "W6") :  #偵測到上月末日的晚班
        # if(lastmonth.iloc[i,(lastday_column-1)] == "N1" or lastmonth.iloc[i,(lastday_column-1)] == "M1" or lastmonth.iloc[i,(lastday_column-1)] == "W6") :
            temp_name = str(lastmonth.iloc[i,0])    #取出值晚班之人的名字

            for i in range (nEmployee):			
                if (temp_name == str(Employee_t.loc[i,'ID'])) :     #到員工表找出此人名字
                    Employee_t.at[i,'NW'] = 1
    return Employee_t
    
def calculate_NM (Employee_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEmployee):  
    if (lastday_ofmonth != "Fri") :
        if (lastday_ofmonth == "Thu") :
                   
            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-4 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
            
            for i in range(lastday_row) :     
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                   
                        temp_name = str(temp_dataframe.iloc[i,0])

                        for k in range (nEmployee) :
                            if (temp_name == str(Employee_t.loc[k,'id'])) : 
                                Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1    
        
        elif (lastday_ofmonth == "Wed") :

            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-3 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
         
            for i in range(lastday_row) :
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                   
                        temp_name = str(temp_dataframe.iloc[i,0])
                   
                        for k in range (nEmployee) :
                            if (temp_name == str(Employee_t.loc[k,'id'])) : 
                                Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1

        elif (lastday_ofmonth == "Tue") :
         
            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-2 : lastday_column]
            temp_dataframe = pd.concat([temp_part1, temp_part2], axis =1 )
        
            for i in range(lastday_row) :
                for j in range (len(temp_dataframe.columns)) :
                    if (temp_dataframe.iloc[i,j] == "N1" or temp_dataframe.iloc[i,j] == "M1" or temp_dataframe.iloc[i,j] == "W6") :
                  
                        temp_name = str(temp_dataframe.iloc[i,0])
                   
                        for k in range (nEmployee) :
                            if (temp_name == str(Employee_t.loc[k,'id'])) : 
                                Employee_t.at[k,'NM'] = int(Employee_t.iloc[k,9]) + 1
        
        elif (lastday_ofmonth == "Mon") : 
        
            temp_part1 = lastmonth.iloc[:, 0]
            temp_part2 = lastmonth.iloc[:, lastday_column-1 : lastday_column]
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
# 讀取半固定參數
#=============================================================================#
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

# 讀取參數
def READ_parameters(path=DIR_PARA):
    global P, TIME_LIMIT,   nK, nR,   CLASS_list, POSI_list,   K_CLASS_set, K_BREAK_set,   CONTAIN

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
        K_BREAK_set[RSet_t.index[ki]] = [ Tran_t2n(x, CLASS_list) for x in RSet_t.iloc[ki].dropna().values ]

    # position
    POSI_list   = readFile(path+'fixed/position.csv').iloc[0].tolist()  #職位高低(低到高)

    # time limit
    try:
        TIME_LIMIT = readFile(path+'time_limit.csv', header_=0)
    except:
        print('\n無法讀取time_limit.csv，改用預設時間限制\n')
READ_parameters()



#=============================================================================#
# 讀取 per_month
#=============================================================================#
def READ_per_month(path=DIR_PER_MONTH):
    #要改的
    global YEAR, MONTH,   nW, mDAY, nE
    global NAME_list, ID_list,   LastWEEK_night, LastDAY_night,   AH_list, NAH_list
    global D_WDAY_set, D_WEEK_set,   E_SKILL_set, E_POSI_set
    global ASSIGN, DEMAND, Employee_t
    #要用的
    global nD, DATE_list, CLASS_list


    # Date
    Date_t = readFile(path+'Date.csv', index_col_ = 0)
    try:
        YEAR = int(Date_t.iloc[0,0])
        MONTH = int(Date_t.iloc[1,0])
        PRINT('讀取 '+str(YEAR)+' 年 '+str(MONTH)+' 月 當月份資料')
    except:
        ERROR('日期不能為空值，請確認 Date.csv 檔案')
    nW = get_nW(YEAR,MONTH)                         #總週數
    mDAY = int(calendar.monthrange(YEAR,MONTH)[1])  #本月總日數


    # Employee
    Employee_t  = readFile(path+"Employee.csv", header_ = 0)
    Employee_t['ID'] = [ str(x) for x in Employee_t['ID'] ]           #強制將ID設為string

    nE          = Employee_t.shape[0]
    NAME_list = list(Employee_t['Name_English'])                                  #對照名字與員工index用
    ID_list   = [ str(x) for x in Employee_t['ID'] ]                              #對照ID與員工index用

    SKILL_NAME  = list(filter(lambda x: re.match('skill-',x), Employee_t.columns))  #自動讀取技能名稱
    E_SKILL_set = SetSKILL(Employee_t[ SKILL_NAME ])                                #特定技能的員工集合

    E_POSI_set = SetPOSI(Employee_t['Position'], POSI_list)                         #某職稱以上的員工集合      


    # Schedule (NM 及 NW 從人壽提供之上個月的班表裡面計算)
    if MONTH>1:
        Schedule_t = readFile(path+'Schedule_'+str(YEAR)+'_'+str(MONTH-1)+'.csv', skiprows_=[0])
    else:
        Schedule_t = readFile(path+'Schedule_'+str(YEAR-1)+'_12.csv', skiprows_=[0])
    Schedule_t[0] = [ str(x) for x in Schedule_t[0] ]   #強制將ID設為string

    #!!!!!計算上月底晚班狀況!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    lastday_column = len(Schedule_t.columns)            #最後一行(上月末日)
    lastday_column = -1
    for c in range(len(Schedule_t.columns)-1,2,-1):     #從最後一天開始數(2是為了去掉開頭index、ID、名字三行)
        if Schedule_t[c][1] != 'X':         #如果這一天不是假日的全'X'行，就取之為上月末日
            lastday_column = c
            break
    if lastday_column == -1:
        ERROR('上個月的班表有錯誤，找不到上個月最後一個上班日')
    lastday_ofmonth = Schedule_t.iloc[0,lastday_column]
    lastday_row     = Schedule_t.shape[0]
    #預設值：全無晚班
    Employee_t['NM'] = [0] * Employee_t.shape[0]
    Employee_t['NW'] = [0] * Employee_t.shape[0]
    #上個月的最後一天有排晚班者是1，沒有則是0
    Employee_t = calculate_NW(Employee_t,lastday_ofmonth,lastday_row,lastday_column,Schedule_t,nE)
    #上月底的斷頭週，計算該斷頭週總共排了幾次晚班
    calculate_NM(Employee_t,lastday_ofmonth,lastday_row,lastday_column,Schedule_t,nE)
    LastWEEK_night = Employee_t['NM'].values     #上月底斷頭周
    LastDAY_night  = Employee_t['NW'].values     #上月末日


    # Need
    Need_t = readFile(path+"Need.csv", header_=0, index_col_=0).T
    DATE_list = [ int(x) for x in Need_t.index ]            #所有的日期 - 對照用
    nD = len(DATE_list)                                     #總工作日數

    month_start = get_startD(YEAR,MONTH)                        #本月第一天是禮拜幾 (Mon=0, Tue=1..)
    AH_list, NAH_list = SetVACnext(month_start, nD, DATE_list)  #VACnextdayset - 假期後或週一的日子集合
    DW          = SetDAYW(month_start+1,mDAY,nW, list(range(nD)), DATE_list)    #第 w 週包含的日期集合
    D_WDAY_set  = SetDAY(month_start, nD, DATE_list)            #DAYset - 通用日子集合 [all,Mon,Tue...]
    D_WEEK_set  = SetWEEKD(DW, nW)                              #WEEK_of_DAY - 日子j所屬的那一週 


    # Assign
    Assign_t = readFile(path+'Assign.csv', skiprows_=[0])
    Assign_t[0] = [ str(x) for x in Assign_t[0] ]           #強制將ID設為string
    Assign_t[1] = [ int(x) for x in Assign_t[1] ]           #強制將日期設為int
    Assign_t[2] = [ str(x) for x in Assign_t[2] ]           #強制將班別設為string
    for c in range(Assign_t.shape[0]):
        e = Tran_t2n(Assign_t.iloc[c,0], ID_list)
        d = Tran_t2n(Assign_t.iloc[c,1], DATE_list)
        k = Tran_t2n(Assign_t.iloc[c,2], CLASS_list)
        #回報錯誤
        if e!=e:
            ERROR('指定排班表中發現不明ID：',Assign_t.iloc[c,0],\
                '不在員工資料的ID列表中，請再次確認ID正確性（包含大小寫、空格、換行）')
        if d!=d:
            ERROR('指定排班的日期錯誤：',Assign_t.iloc[c,1],\
                '不是上班日（上班日指有進線預測資料的日子）')
        if k!=k:
            ERROR('指定排班中發現不明班別：',Assign_t.iloc[c,2],\
                '不在登錄的班別中，請指定班別列表中的一個班別（注意大小寫）')
        ASSIGN.append( (e, d, k) )
READ_per_month()



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
    LOWER = readFile(path+'lower_limit.csv').values.tolist()         #LOWER - 日期j，班別集合ks，職位p，上班人數下限
    for i in range(len(LOWER)):
        d = Tran_t2n( LOWER[i][0], DATE_list)
        LOWER[i][0] = d


    # upper
    Upper_t     = readFile(path+'upper_limit.csv', skiprows_=[0])   #指定星期幾、班別，人數上限
    Upper_t[0]  = [ str(x) for x in Upper_t[0] ]                    #強制將ID設為string
    #UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
    for c in range(Upper_t.shape[0]):
        e = Tran_t2n(Upper_t.iloc[c,0], ID_list)
        #回報錯誤
        if e==None:
            print('指定排班表中發現不明ID：',Upper_t.iloc[c,0],\
                '不在員工資料的ID列表中，請再次確認ID正確性（包含大小寫、空格、換行）')
        UPPER.append( (e, Upper_t.iloc[c,1], Upper_t.iloc[c,2], Upper_t.iloc[c,3]) )


    # senior
    Senior_t    = readFile(path+'senior_limit.csv', skiprows_=[0])
    PERCENT = Senior_t.values.tolist()   #PERCENT - 日子集合，班別集合，要求占比，年資分界線      
    try:   #為了因應條件全空時
        SENIOR_bp = Senior_t[3]
    except:
        SENIOR_bp = []
    E_SENIOR_set = [SetSENIOR(Employee_t['Senior'],tmp) for tmp in SENIOR_bp]   #達到特定年資的員工集合


    # skill lower limit
    SKset_t     = readFile(path+'skill_class_limit.csv')            #class set for skills
    # 特殊班別每天人數相同
    NOTPHONE_CLASS = []
    # 特殊班別假日後一天人數不同
    NOTPHONE_CLASS_special = []
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
    Upper_shift = readFile(path+'class_upperlimit.csv').values.tolist()
READ_limits()





"""================================================================================================================
    輸出
        csv:班表、缺工冗員表
        其他資訊：xlsx檔
================================================================================================================"""
# 輸出檔名
Schedule_FileName = 'Schedule_'+str(YEAR)+'_'+str(MONTH)+'.csv'
LackOver_FileName = 'lack_'+str(YEAR)+'_'+str(MONTH)+'.csv'

# 輸出函式
def OUTPUT(matrix_ijk):     #參數：三層的list，分別為 員工、日子、班別，內容為bool (某員工某日是否值此班別)
    return True



# ================================================================================================================
# 確認
print('\n\n=== 參數確認 ===')
print('nE=',nE, ',nD=',nD, ',nK=',nK, ',nT=',nT, ',nR=',nR, ',nW=',nW, ',mDAY=',mDAY,'\n')
print('DATE_list=',DATE_list)
print('CLASS_list=',CLASS_list)
print('AH_list=',AH_list)
print('POSI_list=',POSI_list,'\n')
print('E_POSI_set=',E_POSI_set)
print('E_SENIOR_set=',E_SENIOR_set)
print('E_SKILL_set=',E_SKILL_set,'\n')
print('D_WEEK_set=',D_WEEK_set)
print('D_WDAY_set=',D_WDAY_set,'\n')
print('K_CLASS_set=',K_CLASS_set)
print('K_BREAK_set=',K_BREAK_set)


# 關閉紀錄檔
PRINT('\ntool_test.py import successfully\n')
RECORD_FILE.close()


"""
# ================================================================================================================
# 主程式中的檔案指派：


#=============================================================================#
#每月更改的資料
#=============================================================================#
#year/month
year  = int(date.iloc[0,0])
month = int(date.iloc[1,0])

#指定排班
DATES = tl2.DATE_list    #所有的日期 - 對照用

#employees data
EMPLOYEE_t = tl2.Employee_t
nightdaylimit = EMPLOYEE_t['night_perWeek']
E_NAME     = tl2.NAME_list
E_ID       = tl2.ID_list

#=============================================================================#
#半固定參數
#=============================================================================#
timelimit     = tl2.TIME_LIMIT

Posi       = tl2.POSI_list
Shift_name = tl2.CLASS_list

# =============================================================================#
# =============================================================================#
# =============================================================================#
# Create a new model
# =============================================================================#
# =============================================================================#
# =============================================================================#
# =============================================================================#

m = Model("first")

# ============================================================================#
# Indexs 都從0開始

# i 員工 i
# j 日子 j，代表一個月中的需要排班的第 j 個日子
# k 班別 k，代表每天可選擇的不同上班別態
# t 工作時段 t，表示某日的第 t 個上班的小時
# w 週次 w，代表一個月中的第 w 週
# r 午休方式r，每個班別有不同的午休方式

# 休假:0
# 早班-A2/A3/A4/A5/MS/AS:1~6
# 午班-P2/P3/P4/P5:7~10
# 晚班-N1/M1/W6:11~13
# 其他-CD/C2/C3/C4/OB:14~18

# =============================================================================#
# Parameters
# -------number-------#
nEMPLOYEE = tl2.nE                  #總員工人數
nDAY      = tl2.nD                  #總日數
nK        = tl2.nK                  #班別種類數
nT        = tl2.nT                  #總時段數
nR        = tls.nR                  #午休種類數
nW        = tl2.nW                  #總週數
mDAY      = tl2.mDAY

# -------Basic-------#
CONTAIN = tl2.CONTAIN               #CONTAIN_kt - 1表示班別k包含時段t，0則否
DEMAND = tl2.DEMAND                 #DEMAND_jt - 日子j於時段t的需求人數
ASSIGN = tl2.ASSIGN                 #ASSIGN_ijk - 員工i指定第j天須排班別k，形式為 [(i,j,k)]

LMNIGHT  = tl2.LastWEEK_night       #LMNIGHT_i - 表示員工i在上月終未滿一週的日子中曾排幾次晚班
FRINIGHT = tl2.LastDAY_night        #FRINIGHT_i - 1表示員工i在上月最後一日且為週五的日子排晚班，0則否

# -------調整權重-------#
P0       = 100                      #目標式中的調整權重(lack)
P1       = P_t[1]['P1']             #目標式中的調整權重(surplus)
P2       = P_t[1]['P2']             #目標式中的調整權重(nightCount)
P3       = P_t[1]['P3']             #目標式中的調整權重(breakCount)
P4       = P_t[1]['P4']             #目標式中的調整權重(noonCount)

# -----排班特殊限制-----#
LOWER = tl2.LOWER                   #LOWER - 日期j，班別集合ks，職位p，上班人數下限
UPPER = tl2.UPPER                   #UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
PERCENT = tl2.PERCENT               #PERCENT - 日子集合，班別集合，要求占比，年資分界線


# ----------------新-----------------#
# 特殊班別一定人數
# 特殊班別每天人數相同
NOTPHONE_CLASS = tl2.NOTPHONE_CLASS
# 特殊班別假日後一天人數不同
NOTPHONE_CLASS_special = tl2.NOTPHONE_CLASS_special

# 特殊班別每人排班上限
Upper_shift = tl2.Upper_shift

# =============================================================================#
# Sets
EMPLOYEE = [tmp for tmp in range(nEMPLOYEE)]    #EMPLOYEE - 員工集合，I=0,…,nI 
DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
TIME = [tmp for tmp in range(nT)]               #TIME - 工作時段集合，T=1,…,nT
BREAK = [tmp for tmp in range(nR)]              #BREAK - 午休方式，R=1,…,nR
WEEK = [tmp for tmp in range(nW)]               #WEEK - 週次集合，W=1,…,nW
SHIFT = [tmp for tmp in range(nK)]              #SHIFT - 班別種類集合，K=1,…,nK ;0代表休假
 
# -------員工集合-------#
E_POSITION = tl2.POSI_set                       #E_POSITION - 擁有特定職稱的員工集合，POSI=1,…,nPOSI
E_SKILL = tl2.SKILL_set                         #E_SKILL - 擁有特定技能的員工集合，SKILL=1,…,nSKILL
E_SENIOR = tl2.SENIOR_set                       #E_SENIOR - 達到特定年資的員工集合    

# -------日子集合-------#
DAYset = tl2.D_WDAY_set                         #DAYset - 通用日子集合 [all,Mon,Tue...]
WEEK_of_DAY = tl2.D_WEEK_set                    #WEEK_of_DAY - 日子j所屬的那一週
VACnextdayset = tl2.AH_list                     #VACnextdayset - 假期後或週一的日子集合
NOT_VACnextdayset = tl2.NAH_list 

# -------班別集合-------#
SHIFTset= tl2.K_CLASS_set                       #SHIFTset - 通用的班別集合，S=1,…,nS
S_NIGHT = SHIFTset['night']                         #S_NIGHT - 所有的晚班
S_NOON = SHIFTset['noon']                           #S_NOON - 所有的午班
S_BREAK =tl2.K_BREAK_set


#============================================================================#
#Variables
#GRB.BINARY/GRB.INTEGER/GRB.CONTINUOUS


# ================================================================================================================
"""