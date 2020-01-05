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
================================================================================================================"""
# 基本資料
DIR = '../data'                         #預設總資料夾檔案路徑
DIR_PER_MONTH = '../data/per_month/'    #每月改變的資料(per_month)的檔案路徑
DIR_PARA = '../data/parameters/'        #parameters的檔案路徑
RECORD_FILE = open('record.log', 'w', encoding='utf-8-sig')   #運行紀錄檔案
YEAR = 2019
MONTH = 4
TIME_LIMIT = 300

# 權重
P = [100,0,0,0,0]  #P0是缺工人數

# 各項目總數
nE = 0      #總員工人數
nD = 0      #總日數
nK = 0      #班別種類數
nT = 24     #總時段數
nR = 0      #午休種類數
nW = 0      #總週數
mDAY = 0    #本月總日數
# nE = Employee_t.shape[0]     #總員工人數
# nD = len(DEMAND_t.index)     #總日數
# nK = A_t.shape[0]            #班別種類數
# nT = 24                      #總時段數
# nR = Rset_t.shape[0]         #午休種類數
# nW = tl.get_nW(year,month)   #總週數
# mDAY = int(calendar.monthrange(YEAR,MONTH)[1]) #本月總日數

# List
# -------對照用的-------#
NAME_list   = []    #員工英文名字
ID_list     = []    #員工ID
DATE_list   = []    #日期
CLASS_list  = []    #班別名稱
# -------其他-------#
AH_list     = []    #days after holiday
POSI_list   = []    #職位高低(低到高)

# Set
# -------員工集合-------#
POSI_set    = {}    #某職位以上的員工集合，預設值= '任意':range(nE)
SENIOR_set  = {}    #某年資以上的員工集合，無預設值
SKILL_set   = {}    #擁有特定技能的員工集合，無預設值
# -------日子集合-------#
WEEK_set    = {}                                                                #每周有哪些天(Tran後)
WDAY_set    = {'Mon':[],'Tue':[],'Wed':[],'Thu':[],'Fri':[],'Sat':[],'Sun':[]}  #周幾有哪些天
# -------班別集合-------#
CLASS_set   = {'all':[], 'night':['N1','W6','M1'], 'phone':[]}    #班別分類(只有phone內的班別能減少缺工)
BREAK_set   = {}                                    #有哪些午休時段(時段:此時段的班別index)
"""
# -------員工集合-------#
E_POSITION = tl.SetPOSI(E_POSI_t, Posi)                          #E_POSITION - 擁有特定職稱的員工集合，POSI=1,…,nPOSI
E_SKILL = tl.SetSKILL(E_SKILL_t)                                 #E_SKILL - 擁有特定技能的員工集合，SKILL=1,…,nSKILL
E_SENIOR = [tl.SetSENIOR(E_SENIOR_t,tmp) for tmp in SENIOR_bp]   #E_SENIOR - 達到特定年資的員工集合    

# -------日子集合-------#
month_start = tl.get_startD(year,month)         #本月第一天是禮拜幾 (Mon=0, Tue=1..)
D_WEEK = tl.SetDAYW(month_start+1,mDAY,nW, DAY, DATES)      #D_WEEK - 第 w 週中所包含的日子集合
DAYset = tl.SetDAY(month_start, nDAY, DATES)            #DAYset - 通用日子集合 [all,Mon,Tue...]
WEEK_of_DAY = tl.SetWEEKD(D_WEEK, nW) #WEEK_of_DAY - 日子j所屬的那一週
VACnextdayset, NOT_VACnextdayset = tl.SetVACnext(month_start, nDAY, DATES) #VACnextdayset - 假期後或週一的日子集合

# -------班別集合-------#
SHIFTset= {}                                                    #SHIFTset - 通用的班別集合，S=1,…,nS
for ki in range(len(Kset_t)):
    SHIFTset[Kset_t.index[ki]] = [ tl.Tran_t2n(x, Shift_name) for x in Kset_t.iloc[ki].dropna().values ]
for ki in range(len(Shift_name)):
    SHIFTset[Shift_name[ki]] = [ki]
S_NIGHT = SHIFTset['night']                                     #S_NIGHT - 所有的晚班
S_NOON = SHIFTset['noon']                                       #S_NOON - 所有的午班
S_BREAK =[]
for ki in range(len(Rset_t)):
    S_BREAK.append([ tl.Tran_t2n(x, Shift_name) for x in Rset_t.iloc[ki].dropna().values ])
"""



# 表格資料






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
    PRINT('Read '+dir)
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
    for i in range (lastday_row):
        c = lastmonth.iloc[i, lastday_column]
        if c in CLASS_set['night']:     #偵測到上月末日的晚班
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
# 讀檔路徑 path.txt
def READ_path():
    try:
        with open('../path.txt','r') as f:  #用with一次性完成open、close檔案
            DIR = '../' + f.read().replace('\n', '')
    except FileNotFoundError:
        ERROR('找不到檔案path.txt檔案')
    except:
        PRINT('打不開path.txt，使用預設路徑')
        DIR = '../data/'   #預設資料路徑：./data/
    DIR_PER_MONTH = DIR+'per_month/'
    DIR_PARA = DIR+'parameters/'
    PRINT('Read file from '+DIR_PER_MONTH+' & '+DIR_PARA)
    return None
READ_path()


#=============================================================================#
# 讀取半固定參數
#=============================================================================#
def READ_parameters(path=DIR_PARA):
    # weight p1~4
    Weight_t    = readFile(path+'weight_p.csv', index_col_=0)        #權重
    P[1]        = Weight_t[1]['P1']             #目標式中的調整權重(surplus)
    P[2]        = Weight_t[1]['P2']             #目標式中的調整權重(nightCount)
    P[3]        = Weight_t[1]['P3']             #目標式中的調整權重(breakCount)
    P[4]        = Weight_t[1]['P4']             #目標式中的調整權重(noonCount)

    # class time
    ClassTime_t = readFile(path+'fixed/fix_class_time.csv', header_=0, index_col_=[0])  #class-time table
    CLASS_list  = list(ClassTime_t.index)

    # class set
    KSet_t      = readFile(path+'fixed/fix_classes.csv', index_col_=[0])                    #class set
    for ki in range(len(KSet_t)):           #將檔案中的班別集合登錄成dict
        CLASS_set[KSet_t.index[ki]] = [ Tran_t2n(x, CLASS_list) for x in KSet_t.iloc[ki].dropna().values ]
    for ki in range(len(CLASS_list)):
        CLASS_set[CLASS_list[ki]] = [ki]    #每個班別自身也都是獨立的(單一元素)集合

    # rest set
    Rset_t      = readFile(path+'fixed/fix_resttime.csv', index_col_=[0])               #rest set
    for ki in range(len(Rset_t)):
        BREAK_set[RSet_t.index[ki]] = [ Tran_t2n(x, CLASS_list) for x in Rset_t.iloc[ki].dropna().values ]

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
    # Date
    Date_t = readFile(path+'Date.csv', index_col_ = 0)
    try:
        YEAR = int(Date_t.iloc[0,0])
        MONTH = int(Date_t.iloc[1,0])
        PRINT('讀檔 年/月：'+str(YEAR)+'/'+str(MONTH))
    except:
        ERROR('日期不能為空值，請確認 Date.csv 檔案')

    # Employee
    Employee_t  = readFile(path+"Employee.csv", header_ = 0)
    Employee_t['ID'] = [ str(x) for x in Employee_t['ID'] ]           #強制將ID設為string
    nE          = Employee_t.shape[0]
    NAME_list   = list(Employee_t['Name_English'])                                  #對照名字與員工index用
    ID_list     = [ str(x) for x in Employee_t['ID'] ]                              #對照ID與員工index用
    SKILL_NAME  = list(filter(lambda x: re.match('skill-',x), Employee_t.columns))  #自動讀取技能名稱
    E_SENIOR_t = Employee_t['Senior']               #年資的行
    E_POSI_t = Employee_t['Position']               #職位的行
    E_NperW_t = Employee_t['night_perWeek']         #每周晚班上限的行
    E_SKILL_t = Employee_t[ SKILL_NAME ]            #員工技能表

    # Schedule (NM 及 NW 從人壽提供之上個月的班表裡面計算)
    if MONTH>1:
        Schedule_t = readFile(path+'Schedule_'+str(YEAR)+'_'+str(MONTH-1)+'.csv', skiprows_=[0])
    else:
        Schedule_t = readFile(path+'Schedule_'+str(YEAR-1)+'_12.csv', skiprows_=[0])
    Schedule_t[0] = [ str(x) for x in Schedule_t[0] ]   #強制將ID設為string
    #計算上月底晚班狀況
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
    print('last day of last month:',lastday_ofmonth)
    #預設值：全無晚班
    Employee_t['NM'] = [0] * Employee_t.shape[0]
    Employee_t['NW'] = [0] * Employee_t.shape[0]
    #上個月的最後一天有排晚班者是1，沒有則是0
    Employee_t = calculate_NW(Employee_t,lastday_ofmonth,lastday_row,lastday_column,Schedule_t,nE)
    #上月底的斷頭週，計算該斷頭週總共排了幾次晚班
    calculate_NM(Employee_t,lastday_ofmonth,lastday_row,lastday_column,Schedule_t,nE)
    NM_t = Employee_t['NM']     #上月底斷頭周
    NW_t = Employee_t['NW']     #上月末日
    print(Employee_t)

    # Assign
    Assign_t = readFile(path+'Assign.csv', skiprows_=[0])
    Assign_t[0] = [ str(x) for x in Assign_t[0] ]           #強制將ID設為string

    # Need
    Need_t = readFile(path+"Need.csv", header_=0, index_col_=0).T
    DATE_list = [ int(x) for x in Need_t.index ]    #所有的日期 - 對照用
READ_per_month()


#=============================================================================#
# 讀取限制式
#=============================================================================#
def READ_limits(path=DIR_PARA):
    # -------讀取限制式-------#
    # lower
    Lower_t     = readFile(path+'lower_limit.csv')                  #指定日期、班別、職位，人數下限

    # upper
    Upper_t     = readFile(path+'upper_limit.csv', skiprows_=[0])   #指定星期幾、班別，人數上限
    Upper_t[0]  = [ str(x) for x in Upper_t[0] ]                    #強制將ID設為string

    # senior
    Senior_t    = readFile(path+'senior_limit.csv', skiprows_=[0])  #指定年資、星期幾、班別，要占多少比例以上
    try:              # 下面的try/except都是為了因應條件全空時
        SENIOR_bp = Ratio_t[3]
    except:
        SENIOR_bp = []

    # class
    SKset_t     = readFile(path+'skill_class_limit.csv')            #class set for skills
    U_Kset      = readFile(path+'class_upperlimit.csv')             #upper bound for class per month
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
# 關閉檔案
PRINT('\ntool_test.py import successfully\n')
RECORD_FILE.close()
# 結束程式
sys.exit()