# !/usr/bin/env python3OA
# -*- coding: utf-8 -*-
from   gurobipy import *
import numpy as np
import pandas as pd
import data.fixed.tool as tl
import datetime, calendar, sys
from   data.fixed.score import score
#import fixed.tool_test as tl2
"""
0101更新
上限改為可以指定某CSR（限制式10)
新增午休表格fix_resttime.csv
S_break及午休種類改為可以彈性調整
tool.py Ktype直接刪除，皆改為直接由主程式碼代入function
nightCount取晚班最大值時有考慮到係數（限制式14)
"""
#測試檔案檔名 - 沒有要測試時請將TestPath留空白
# TestPath = ""
EmployeeTest = "_20191230"
AssignTest = "_20191230"
NeedTest = ""
U_ttest = "_20191230"


#=============================================================================#
#=============================================================================#
#=============================================================================#
# import data
#=============================================================================#
#=============================================================================#
#=============================================================================#
#讀檔路徑import data
try:
    f = open('path.txt', "r")
    dir_name = f.read().replace('\n', '')
except:
    dir_name = './data/'   #預設資料路徑：./data/

# 測試用
# if TestPath != "":
#     dir_name = TestPath
#     parameters_dir = TestPath
# else:
#     dir_name = './data/'
#     EmployeeTest = ""
#     AssignTest = ""
#     NeedTest = ""
#=============================================================================#
#每月更改的資料
#=============================================================================#
#year/month
date  = pd.read_csv(dir_name + 'per_month/Date.csv', header = None, index_col = 0)
year  = int(date.iloc[0,0])
month = int(date.iloc[1,0])

#指定排班
#M_t = tl.readFile(dir_name + 'per_month/Assign.csv')
M_t = tl.readFile(dir_name + 'per_month/Assign'+AssignTest+'.csv')
M_t[0] = [ str(x) for x in M_t[0] ]           #強制將ID設為string
#進線需求預估
#DEMAND_t = pd.read_csv(dir_name+"per_month/Need.csv", header = 0, index_col = 0).T
DEMAND_t = pd.read_csv(dir_name+"per_month/Need"+NeedTest+".csv", header = 0, index_col = 0, engine='python').T
DATES = [ int(x) for x in DEMAND_t.index ]    #所有的日期 - 對照用

#employees data
#EMPLOYEE_t = pd.read_csv(dir_name+"per_month/Employee.csv", header = 0, engine='python')
EMPLOYEE_t = pd.read_csv(dir_name+"per_month/Employee"+EmployeeTest+".csv", header = 0, engine='python') 
E_NAME     = list(EMPLOYEE_t['Name_English'])       #E_NAME - 對照名字與員工index時使用
E_ID       = [ str(x) for x in EMPLOYEE_t['ID'] ]     #E_ID - 對照ID與員工index時使用
E_SENIOR_t = EMPLOYEE_t['Senior']
E_POSI_t   = EMPLOYEE_t['Position']
E_SKILL_t  = EMPLOYEE_t[ list(filter(lambda x: re.match('skill-',x), EMPLOYEE_t.columns)) ]   #抓出員工技能表

#=============================================================================#
####NM 及 NW 從人壽提供之上個月的班表裡面計算
if month>1:
	lastmonth = pd.read_csv(dir_name + 'per_month/Schedule_'+str(year)+'_'+str(month-1)+'.csv', engine='python')
else:
	lastmonth = pd.read_csv(dir_name + 'per_month/Schedule_'+str(year-1)+'_12.csv', engine='python')

lastday_column  = len(lastmonth.columns)
lastday_row     = lastmonth.shape[0]
lastday_ofmonth = lastmonth.iloc[0,(lastday_column-1)]
nEMPLOYEE       = EMPLOYEE_t.shape[0]

#上個月的最後一天是週五，且有排晚班者，有則是1，沒有則是0
tl.calculate_NW (EMPLOYEE_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEMPLOYEE)

#上個月為斷頭週，並計算該週總共排了幾次晚班
tl.calculate_NM (EMPLOYEE_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEMPLOYEE)
NM_t = EMPLOYEE_t['NM']
NW_t = EMPLOYEE_t['NW']
#####

#=============================================================================#
#半固定參數
#=============================================================================#
P_t     = pd.read_csv(dir_name + 'parameters/weight_p.csv', header = None, index_col = 0, engine = 'python') #權重
L_t     = pd.read_csv(dir_name + "parameters/lower_limit.csv", engine = 'python')                          #指定日期、班別、職位，人數下限
U_t     = tl.readFile(dir_name + "parameters/upper_limit"+U_ttest+".csv")                      #指定星期幾、班別，人數上限
U_t[0] = [ str(x) for x in U_t[0] ]           #強制將ID設為string
Ratio_t = tl.readFile(dir_name + "parameters/senior_limit.csv")                     #指定年資、星期幾、班別，要占多少比例以上


SKset_t = pd.read_csv(dir_name + 'parameters/skill_class_limit.csv', engine='python')  #class set for skills
U_Kset = pd.read_csv(dir_name + 'parameters/class_upperlimit.csv', engine='python')  #upper bound for class per month


try:              # 下面的try/except都是為了因應條件全空時
	SENIOR_bp = Ratio_t[3]
except:
	SENIOR_bp = []
try:
    timelimit     = pd.read_csv(dir_name + "parameters/time_limit.csv", header = 0)
except:
    print('\n無法讀取time_limit.csv，改用預設時間限制\n')
    timelimit     = 300	#預設跑五分鐘

nightdaylimit = EMPLOYEE_t['night_perWeek']


#=============================================================================#
#固定參數：班別總數與時間
#=============================================================================#
Kset_t = pd.read_csv(dir_name + 'fixed/fix_classes.csv', header = None, index_col = 0) #class set
A_t    = pd.read_csv(dir_name + 'fixed/fix_class_time.csv', header = 0, index_col = 0)
Rset_t = pd.read_csv(dir_name + 'fixed/fix_resttime.csv', header = None, index_col = 0) #rest set

#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
Posi       = pd.read_csv(dir_name + 'fixed/position.csv', header = None, engine='python').iloc[0].tolist()
Shift_name = Kset_t.iloc[0].tolist()

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
nEMPLOYEE = EMPLOYEE_t.shape[0]     #總員工人數
nDAY      = len(DEMAND_t.index)          #總日數
nK        = A_t.shape[0]                   #班別種類數
nT        = 24                             #總時段數
nR        = Rset_t.shape[0]                #午休種類數
nW        = tl.get_nW(year,month)          #總週數
mDAY      = int(calendar.monthrange(year,month)[1])

# -------Basic-------#
CONTAIN = A_t.values.tolist()      #CONTAIN_kt - 1表示班別k包含時段t，0則否
DEMAND = DEMAND_t.values.tolist()  #DEMAND_jt - 日子j於時段t的需求人數
ASSIGN = []                        #ASSIGN_ijk - 員工i指定第j天須排班別k，形式為 [(i,j,k)]

for c in range(M_t.shape[0]):
    e = tl.Tran_t2n(M_t.iloc[c,0], E_ID)
    d = tl.Tran_t2n(M_t.iloc[c,1], DATES)
    k = tl.Tran_t2n( str(M_t.iloc[c,2]), Shift_name)
    #回報錯誤
    if e!=e:
        print('指定排班表中發現不明ID：',M_t.iloc[c,0],'不在員工資料的ID列表中，請再次確認ID正確性（包含大小寫、空格、換行）')
    if d!=d:
        print('指定排班的日期錯誤：',M_t.iloc[c,1],'不是上班日（上班日指有進線預測資料的日子）')
    if k!=k:
        print('指定排班中發現不明班別：',M_t.iloc[c,2],'不在登錄的班別中，請指定班別列表中的一個班別（注意大小寫）')
    ASSIGN.append( (e, d, k) )

LMNIGHT  = NM_t.values            #LMNIGHT_i - 表示員工i在上月終未滿一週的日子中曾排幾次晚班
FRINIGHT = NW_t.values           #FRINIGHT_i - 1表示員工i在上月最後一日且為週五的日子排晚班，0則否

# -------調整權重-------#
P0       = 100                      #目標式中的調整權重(lack)
P1       = P_t[1]['P1']             #目標式中的調整權重(surplus)
P2       = P_t[1]['P2']             #目標式中的調整權重(nightCount)
P3       = P_t[1]['P3']             #目標式中的調整權重(breakCount)
P4       = P_t[1]['P4']             #目標式中的調整權重(noonCount)

# -----排班特殊限制-----#
LOWER = L_t.values.tolist()       	#LOWER - 日期j，班別集合ks，職位p，上班人數下限
for i in range(len(LOWER)):
    d = tl.Tran_t2n( LOWER[i][0], DATES)
    LOWER[i][0] = d
UPPER = []                          #UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
for c in range(U_t.shape[0]):
    e = tl.Tran_t2n(U_t.iloc[c,0], E_ID)
    #回報錯誤
    if e==None:
        print('指定排班表中發現不明ID：',U_t.iloc[c,0],'不在員工資料的ID列表中，請再次確認ID正確性（包含大小寫、空格、換行）')
    UPPER.append( (e, U_t.iloc[c,1], U_t.iloc[c,2], U_t.iloc[c,3]) )
PERCENT = Ratio_t.values.tolist()	#PERCENT - 日子集合，班別集合，要求占比，年資分界線


# ----------------新-----------------#
# 特殊班別一定人數
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

# 特殊班別每人排班上限
Upper_shift = U_Kset.values.tolist()

# =============================================================================#
# Sets
EMPLOYEE = [tmp for tmp in range(nEMPLOYEE)]    #EMPLOYEE - 員工集合，I=0,…,nI 
DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
TIME = [tmp for tmp in range(nT)]               #TIME - 工作時段集合，T=1,…,nT
BREAK = [tmp for tmp in range(nR)]              #BREAK - 午休方式，R=1,…,nR
WEEK = [tmp for tmp in range(nW)]               #WEEK - 週次集合，W=1,…,nW
SHIFT = [tmp for tmp in range(nK)]              #SHIFT - 班別種類集合，K=1,…,nK ;0代表休假
 
# -------員工集合-------#
E_POSITION = tl.SetPOSI(E_POSI_t, Posi)                          #E_POSITION - 擁有特定職稱的員工集合，POSI=1,…,nPOSI
E_SKILL = tl.SetSKILL(E_SKILL_t)                                 #E_SKILL - 擁有特定技能的員工集合，SKILL=1,…,nSKILL
E_SENIOR = [tl.SetSENIOR(E_SENIOR_t,tmp) for tmp in SENIOR_bp]   #E_SENIOR - 達到特定年資的員工集合    

# -------日子集合-------#
month_start = tl.get_startD(year,month)         #本月第一天是禮拜幾 (Mon=0, Tue=1..)
D_WEEK = tl.SetDAYW(month_start+1,mDAY,nW, DAY, DATES)  	#D_WEEK - 第 w 週中所包含的日子集合
DAYset = tl.SetDAY(month_start, nDAY, DATES)     		#DAYset - 通用日子集合 [all,Mon,Tue...]
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


#============================================================================#
#Variables
#GRB.BINARY/GRB.INTEGER/GRB.CONTINUOUS

work = {}  #work_ijk - 1表示員工i於日子j值班別為k的工作，0 則否 ;workij0=1 代表員工i在日子j休假
for i in range(nEMPLOYEE):
    for j in range(nDAY):
        for k in range(nK):
            work[i, j, k] = m.addVar(vtype=GRB.BINARY)
              
            
lack = {}  #y_jt - 代表第j天中時段t的缺工人數
for j in range(nDAY):
    for t in range(nT):
        lack[j, t] = m.addVar(lb=0, vtype=GRB.CONTINUOUS)
        
surplus = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name="surplus") #每天每個時段人數與需求人數的差距中的最大值
nightCount = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name="nightCount") #員工中每人排晚班總次數的最大值

breakCount = {}  #breakCount_iwr - 1表示員工i在第w周中在午休時段r有午休，0則否
for i in range(nEMPLOYEE):
    for w in range(nW):
        for r in range(nR):
            breakCount[i, w, r] = m.addVar(vtype=GRB.BINARY)

noonCount = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name="noonCount") #員工中每人排午班總次數的最大值

m.update()
# ============================================================================#
# Objective

m.setObjective(P0 * quicksum(lack[j,t] for t in TIME for j in DAY) +  P1 * surplus + P2 * nightCount + \
    P3 * quicksum(breakCount[i,w,r] for i in EMPLOYEE for w in WEEK for r in BREAK) + \
    P4 * noonCount , GRB.MINIMIZE)

# ============================================================================#


# =======================================================================================================#
# ====================================================================================================#
# =================================================================================================#
# Constraints
# =================================================================================================#
# ====================================================================================================#
# =======================================================================================================#
# 2 每人每天只能排一種班別
for i in EMPLOYEE:
    for j in DAY:
        m.addConstr(quicksum(work[i,j,k] for k in SHIFT) == 1, "c2")
#4 指定日子排指定班別
for c in ASSIGN:
    m.addConstr(work[c[0],c[1],c[2]] == 1, "c4")

#5 除第一周外，每周最多n次晚班
no_week1 = WEEK.copy()
no_week1.remove(0)            
for i in EMPLOYEE:
    for w in no_week1:
        m.addConstr(quicksum(work[i,j,k] for j in D_WEEK[w] for k in S_NIGHT) <= nightdaylimit[i], "c5")
                    
#6 上月斷頭周+本月第一周 只能n次晚班
for i in EMPLOYEE:
    m.addConstr(quicksum(work[i,j,k] for j in D_WEEK[0] for k in S_NIGHT) <= nightdaylimit[i] - LMNIGHT[i], "c6")

#7 連續天只能一次晚班
#最後一天天刪除（因為他沒有後一天）
less_one_day = DAY.copy()       
less_one_day.pop()
for i in EMPLOYEE:
    for j in less_one_day:
        m.addConstr(quicksum((work[i,j,k]+work[i,j+1,k]) for k in S_NIGHT) <= 1, "c7")
      
#8 上月末日為週五且晚班，則本月初日不能晚班 
for i in EMPLOYEE:
    m.addConstr(quicksum(work[i,0,k] for k in S_NIGHT) <= 1 - FRINIGHT[i], "c8")        

#9 限制職等的人數下限：每一個特定日子，特定班別、特定職等以上的合計人數 >= 下限
for item in LOWER:
    m.addConstr(quicksum(work[i,j,k] for i in E_POSITION[item[2]] for j in [item[0]] for k in SHIFTset[item[1]]) >= item[3],"c9")

#10 排班次數上限：某個特定員工在特定日子、特定班別，排班不能超過多少次
for item in UPPER:	
    m.addConstr(quicksum(work[item[0],j,k] for j in DAYset[item[1]] for k in SHIFTset[item[2]]) <= item[3], "c10")  

       
#11 計算缺工人數
for j in DAY:
    for t in TIME:    
        m.addConstr(lack[j,t] >= -(quicksum(CONTAIN[k][t] * work[i,j,k] for k in SHIFTset['phone'] for i in EMPLOYEE) - DEMAND[j][t]), "c11")         

#13 避免冗員
for j in DAY:
    for t in TIME:
        m.addConstr(surplus >= quicksum(CONTAIN[k][t] * work[i,j,k] for k in SHIFTset['phone'] for i in EMPLOYEE) - DEMAND[j][t], "c13")        

#14 平均每人的晚班數
for i in EMPLOYEE:
    if (nightdaylimit[i]>0):
        m.addConstr(nightCount >= quicksum(work[i,j,k]  for k in S_NIGHT for j in DAY)/nightdaylimit[i], "c14")


#15 同一人同一周休息時間盡量相同
for i in EMPLOYEE:
    for w in WEEK:
        for r in BREAK:
             m.addConstr(5*breakCount[i,w,r] >= quicksum(work[i,j,k]  for k in S_BREAK[r] for j in D_WEEK[w]), "c15") 


#16 指定技能班別一定要排幾人
for item in NOTPHONE_CLASS:
    for j in DAY:
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for i in EMPLOYEE) == item[1], "c16_1")
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for i in E_SKILL[item[2]]) == item[1], "c16_2")

for item in NOTPHONE_CLASS_special:
    for j in NOT_VACnextdayset:
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for i in EMPLOYEE) == item[1], "c16_3")
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for i in E_SKILL[item[2]]) == item[1], "c16_4")
    for j in VACnextdayset:
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for i in EMPLOYEE) == item[3], "c16_5")
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for i in E_SKILL[item[2]]) == item[3], "c16_6")


             
#17 晚班年資2年以上人數需佔 50% 以上
for ix,item in enumerate(PERCENT):
    for j in DAYset[item[0]]:
        for k in SHIFTset[item[1]]:
            m.addConstr(quicksum(work[i,j,k] for i in E_SENIOR[ix]) >= item[2]*quicksum(work[i,j,k] for i in EMPLOYEE),"c17")

#12,18,19 已在variable限制   

#20 特別班別排班次數上限：員工整月特定班別，排班不能超過多少次
for item in Upper＿shift:
    for i in EMPLOYEE:	
        m.addConstr(quicksum(work[i,j,Shift_name.index(item[0])] for j in DAYset['all']) <= item[1], "c20")     

#21 平均每人的午班數
for i in EMPLOYEE:
    m.addConstr(noonCount >= quicksum(work[i,j,k]  for k in S_NOON for j in DAY), "c21")


#============================================================================#
#process
m.params.LogFile = './data/fixed/gurobi.log'    #設定gurobi記錄檔的存放位置與檔名
try:
    m.params.TimeLimit = timelimit.loc[0][0]    #設定最多跑多久
except:
    if type(timelimit)=='int':
        m.params.TimeLimit = timelimit
    else:
        m.params.TimeLimit = 300                #預設跑五分鐘
m.optimize()
#============================================================================#


#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# print out
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#

#輸出檔名
result_x = './Schedule_'+str(year)+'_'+str(month)+'.csv'
result_y = './lack&over_'+str(year)+'_'+str(month)+'.csv'
result = './schedule_data_'+str(year)+'_'+str(month)+'.xlsx'


#Dataframe_x
K_type = Shift_name
cutoff = False

employee_name = E_NAME
which_worktime = []
for i in EMPLOYEE:
    tmp = []
    for j in DAY:
        for k in SHIFT:
            if(work[i,j,k].x==1):
                tmp.append(K_type[k])
                break
        else:
            tmp.append(K_type[1])
            cutoff = True
            #print('CSR ',E_NAME[i],' 在',DATES[j],'號的排班發生錯誤。')
            #print('請嘗試讓程式運行更多時間，或是減少限制條件。\n')
    which_worktime.append(tmp)
        

df_x = pd.DataFrame(which_worktime, index = employee_name, columns = DATES)


#Dataframe_y
T_type = ['09:00','09:30','10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30'
        ,'15:00','15:30','16:00','16:30','17:00','17:30','18:00','18:30','19:00','19:30','20:00','20:30']

lesspeople_count = []
for j in DAY:
    tmp = []
    for t in TIME:
        tmp.append(int(lack[j,t].x))
    lesspeople_count.append(tmp)


df_y = pd.DataFrame(lesspeople_count, index = DATES, columns = T_type) #which_day , columns = T_type)

#計算總和
df_y['SUM_per_day'] = df_y.sum(axis=1)
df_y.loc['SUM_per_time'] = df_y.sum()

#計算需求
demand_day = DEMAND_t.sum(axis=1).values
demand_time = DEMAND_t.sum().values
#計算缺工比例
less_percent_day = (df_y['SUM_per_day'].drop(['SUM_per_time']).values)/demand_day
less_percent_time = (df_y.loc['SUM_per_time'].drop(['SUM_per_day']).values)/demand_time
df_percent_day = pd.DataFrame(less_percent_day, index = DATES, columns = ["Percentage"]) #which_day , columns = ["Percentage"])
df_percent_time = pd.DataFrame(less_percent_time, index = T_type , columns = ["Percentage"])


#h1h2
print("\n所有天每個時段人數與需求人數的差距中的最大值 = "+str(int(surplus.x))+"\n")



#晚班次數dataframe
night_work_total = []
for i in EMPLOYEE:
    count = 0
    for j in DAY:
        for k in SHIFTset['night']:
            if(int(work[i,j,k].x)==1):
                count+=1
    night_work_total.append(count)


df_nightcount = pd.DataFrame(night_work_total, index = employee_name, columns = ['NightWork_count'])
print("\n員工中每人排晚班次數加權平均的最大值 = "+str(int(nightCount.x))+"\n")


#午班次數dataframe
noon_work_total = []
for i in EMPLOYEE:
    count = 0
    for j in DAY:
        for k in SHIFTset['noon']:
            if(int(work[i,j,k].x)==1):
                count+=1
    noon_work_total.append(count)


df_nooncount = pd.DataFrame(noon_work_total, index = employee_name, columns = ['NoonWork_count'])
print("\n員工中每人排午班總次數的最大值 = "+str(int(noonCount.x))+"\n")

      
#休息時間 Dataframe_z
R_type = ['11:30','12:00','12:30','13:00','13:30']     
which_week = [tmp+1 for tmp in WEEK] 
which_resttime = []     
for i in EMPLOYEE:
    tmp = []
    for w in WEEK:
        tmp2 = []
        for r in BREAK:
            if(breakCount[i,w,r].x==1):
                tmp2.append(R_type[r])
        tmp.append(tmp2)
    which_resttime.append(tmp)


df_resttime = pd.DataFrame(which_resttime, index=employee_name, columns=which_week)


print("Final MIP gap value: %f" % m.MIPGap)
print("\n目標值 = "+str(m.objVal) + "\n")


# ============================================================================ #
# 輸出其他資訊
# ============================================================================ #
with pd.ExcelWriter(result) as writer:
    df_x.to_excel(writer, sheet_name="員工排班表")
    df_nightcount.to_excel(writer, sheet_name="員工本月晚班次數")
    df_percent_time.to_excel(writer, sheet_name="每個時段缺工百分比表")
    df_percent_day.to_excel(writer, sheet_name="每天缺工百分比表")
    df_nightcount.to_excel(writer, sheet_name="員工本月晚班次數")
    df_nooncount.to_excel(writer, sheet_name="員工本月午班次數")
    df_y.to_excel(writer, sheet_name="缺工人數表")
    df_resttime.to_excel(writer, sheet_name="員工每週有哪幾種休息時間")


#============================================================================#
#輸出班表
#============================================================================#
output_name = []
output_id = []
for i in range(0,nEMPLOYEE):
    output_id.append(str(EMPLOYEE_t.ID.values.tolist()[i]))
for i in range(0,nEMPLOYEE):
    output_name.append(EMPLOYEE_t.Name_Chinese.values.tolist()[i])
mDAY = int(calendar.monthrange(year,month)[1])
date_list = []
date_name = []
for i in range(1,mDAY+1): #產生日期清單
    weekday=""
    date = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+str(i), "%Y-%m-%d")
    date_list.append(date)
    if date.weekday()==5:
        weekday="六"
    elif date.weekday()==6:
        weekday="日"
    elif date.weekday()==0:
        weekday="一"
    elif date.weekday()==1:
        weekday="二"
    elif date.weekday()==2:
        weekday="三"
    elif date.weekday()==3:
        weekday="四"
    else:
        weekday="五"
    date_name.append(date.strftime("%Y-%m-%d")+' ('+weekday+')')

new = pd.DataFrame()
new['name'] = output_name
NO_WORK=[]
for i in range(0,nEMPLOYEE): #假日全部填X
    NO_WORK.append("X")

for i in range(0,mDAY):
    if (i+1) not in DATES:
        new[date_name[i]] = NO_WORK
    else:
        new[date_name[i]] = df_x[i+1].values.tolist()
print('check point 2\n')
new['id']=output_id
new.set_index("id",inplace=True)
new.to_csv(result_x, encoding="utf-8_sig")
print(new)

#============================================================================#
#輸出冗員與缺工人數表
#============================================================================#
K_type_dict= {}
K_type_dict= {0:None}
for ki in range(1,len(Shift_name)+1):
    K_type_dict[ki] =Shift_name[ki-1]
#K_type_dict = {0:'None',1:'O',2:'A2',3:'A3',4:'A4',5:'A5',6:'MS',7:'AS',8:'P2',9:'P3',10:'P4',11:'P5',12:'N1',13:'M1',14:'W6',15:'CD',16:'C2',17:'C3',18:'C4',19:'OB'}
try:
    x_nb = np.vectorize({v: k for k, v in K_type_dict.items()}.get)(np.array(which_worktime))
except:
    print('無法輸出缺工冗員表：排班班表不完整，請嘗試讓程式運行更多時間。')
    try:
        sys.exit(0)     #出錯的情況下，讓程式退出
    except:
        print('\n程式已結束。')
S_DEMAND = []
S_DEMAND.extend(SHIFTset['phone'])
for i in range(len(S_DEMAND)):
    S_DEMAND[i] += 1

people = np.zeros((nDAY,nT))
for i in range(nEMPLOYEE):
    for j in range(nDAY):
        for k in range(nT):
            if x_nb[i][j] in S_DEMAND:
                people[j][k] = people[j][k] + A_t.values[x_nb[i][j]-1][k]
output_people = (people - DEMAND).tolist()

NO_PEOPLE=[]
new_2=pd.DataFrame()
for i in range(0,24):
    NO_PEOPLE.append('X')
j = 0
for i in range(0,mDAY):
    if (i+1) not in DATES:
        new_2[date_name[i]]=NO_PEOPLE
    else:
        new_2[date_name[i]]= [ int(x) for x in output_people[j] ]
        j = j + 1
new_2['name']=T_type
new_2.set_index("name",inplace=True)
new_2.to_csv(result_y, encoding="utf-8_sig")
# print(new_2.T)

#============================================================================#

score = score(year, month, A_t, nEMPLOYEE, nDAY, nW, nK, nT, nR, DEMAND, P0, P1, P2, P3, P4, SHIFTset, Shift_name, WEEK_of_DAY, nightdaylimit, S_BREAK, df_x.values.tolist())

print('score:',score)

if cutoff == True:
    print('\ngurobi運行被強迫中斷，因此以A2班填入空班別，目標式值可能較高。')