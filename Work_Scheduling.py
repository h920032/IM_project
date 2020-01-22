# !/usr/bin/env python3OA
# -*- coding: utf-8 -*-
from   gurobipy import *
import numpy as np
import pandas as pd
from tool.final_score import final_score
import tool.tool as tl
import random as rd
"""
0101更新
    上限改為可以指定某CSR（限制式10)
    新增午休表格fix_resttime.csv
    S_break及午休種類改為可以彈性調整
    tool.py Ktype直接刪除，皆改為直接由主程式碼代入function
    nightCount取晚班最大值時有考慮到係數（限制式14)
0110更新
    輸入輸出
0112檢測完畢
0113又出錯了
"""
"""
# Indexs 都從0開始

# i 員工 i
# j 日子 j，代表一個月中的需要排班的第 j 個日子
# k 班別 k，代表每天可選擇的不同上班別態
# t 工作時段 t，表示某日的第 t 個上班的小時
# w 週次 w，代表一個月中的第 w 週
# r 午休方式r，每個班別有不同的午休方式
"""

# =============================================================================#
# Parameters
# =============================================================================#
# -------number-------#
nEMPLOYEE = tl.nE                  #總員工人數
nDAY      = tl.nD                  #總日數
nK        = tl.nK                  #班別種類數
nT        = tl.nT                  #總時段數
nR        = tl.nR                  #午休種類數
nW        = tl.nW                  #總週數
mDAY      = tl.mDAY

# -----基礎項目---------#
P0, P1, P2, P3, P4 = tl.P          #目標式中的調整權重(lack, surplus, nightCount, breakCount, noonCount)
timelimit     = tl.TIME_LIMIT
Posi       = tl.POSI_list

# -------表格---------#
CONTAIN = tl.CONTAIN               #CONTAIN_kt - 1表示班別k包含時段t，0則否
DEMAND = tl.DEMAND                 #DEMAND_jt - 日子j於時段t的需求人數
ASSIGN = tl.ASSIGN                 #ASSIGN_ijk - 員工i指定第j天須排班別k，形式為 [(i,j,k)]
EMPLOYEE_t = tl.Employee_t

# -------list---------#
LMNIGHT  = tl.LastWEEK_night       #LMNIGHT_i - 表示員工i在上月終未滿一週的日子中曾排幾次晚班
FRINIGHT = tl.LastDAY_night        #FRINIGHT_i - 1表示員工i在上月最後一工作日排晚班，0則否
nightdaylimit = EMPLOYEE_t['night_perWeek']
Shift_name = tl.CLASS_list

# -----排班特殊限制-----#
LOWER = tl.LOWER                   #LOWER - 日期j，班別集合ks，職位p，上班人數下限
UPPER = tl.UPPER                   #UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
PERCENT = tl.PERCENT               #PERCENT - 日子集合，班別集合，要求占比，年資分界線

# -----新  特殊班別一定人數--------------#
NOTPHONE_CLASS = tl.NOTPHONE_CLASS                     # 特殊班別每天人數相同
NOTPHONE_CLASS_special = tl.NOTPHONE_CLASS_special     # 特殊班別假日後一天人數不同
Upper_shift = tl.Upper_shift                           # 特殊班別每人排班上限


# =============================================================================#
# Sets
# =============================================================================#
EMPLOYEE = [tmp for tmp in range(nEMPLOYEE)]    #EMPLOYEE - 員工集合，I=0,…,nI 
DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
TIME = [tmp for tmp in range(nT)]               #TIME - 工作時段集合，T=1,…,nT
BREAK = [tmp for tmp in range(nR)]              #BREAK - 午休方式，R=1,…,nR
WEEK = [tmp for tmp in range(nW)]               #WEEK - 週次集合，W=1,…,nW
SHIFT = [tmp for tmp in range(nK)]              #SHIFT - 班別種類集合，K=1,…,nK ;0代表休假
 
# -------員工集合-------#
E_POSITION  = tl.E_POSI_set                    #E_POSITION - 擁有特定職稱的員工集合，POSI=1,…,nPOSI
E_SKILL     = tl.E_SKILL_set                   #E_SKILL - 擁有特定技能的員工集合，SKILL=1,…,nSKILL
E_SENIOR    = tl.E_SENIOR_set                  #E_SENIOR - 達到特定年資的員工集合    

# -------日子集合-------#
DAYset = tl.D_WDAY_set                         #DAYset - 通用日子集合 [all,Mon,Tue...]
D_WEEK = tl.D_WEEK_set
VACnextdayset = tl.AH_list                     #VACnextdayset - 假期後或週一的日子集合
NOT_VACnextdayset = tl.NAH_list 

# -------班別集合-------#
SHIFTset= tl.K_CLASS_set                       #SHIFTset - 通用的班別集合，S=1,…,nS
S_NIGHT = SHIFTset['night']                     #S_NIGHT - 所有的晚班
S_NOON = SHIFTset['noon']                       #S_NOON - 所有的午班
S_BREAK =tl.K_BREAK_set



#=======================================================================as ms o to a parameter#
assign_par = []
for i in range(nEMPLOYEE):
    ass_j = []
    for j in range(nDAY):
        ass_k =[]
        for k in range(nK):
            
            onair = False
            for c in ASSIGN:
                if (c[0] == i) and (c[1] == j) and (c[2] == k):
                    onair = True 
                    break

            if onair == True:
                ass_k.append(1)
            else:
                ass_k.append(0)
        ass_j.append(ass_k)
        
    assign_par.append(ass_j)  



# =============================================================================#
# =============================================================================#
# =============================================================================#
# Create a new model
# =============================================================================#
# =============================================================================#
# =============================================================================#

m = Model("first")

#============================================================================#
#Variables
#GRB.BINARY/GRB.INTEGER/GRB.CONTINUOUS
#============================================================================#

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
#============================================================================#

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


#AS MS O to A

for i in EMPLOYEE:
    for j in DAY:
        for k in [0,5,6]:
            m.addConstr(work[i,j,k] <=  assign_par[i][j][k], "c22")

#============================================================================#
#process
m.params.LogFile = './tool/gurobi.log'         #設定gurobi記錄檔的存放位置與檔名 不知為何有時沒有效果
try:
    m.params.TimeLimit = timelimit.loc[0][0]    #設定最多跑多久
except:
    if type(timelimit)=='int':
        m.params.TimeLimit = timelimit
    else:
        m.params.TimeLimit = 300                #預設跑五分鐘
m.optimize()
#============================================================================#


#============================================================================#
# 輸出
result = tl.OUTPUT(work, isALG=False)           #建立一個專門用來輸出的class物件
df, df_lack = result.printAll(makeFile=True)    
""" result.printAll()
    輸出：tuple (班表, 缺工冗員表)
    參數：makefile, makeFile=True會將班表、缺工冗員表另外存成csv，False則只有xlsx檔
"""
print('\n\n\n\n=============== 班表 ===============\n', df)
print('\n\n\n\n============= 缺工冗員表 ============\n', df_lack)

#============================================================================#


#只有score需要的參數
year  = tl.YEAR
month = tl.MONTH
A_t = tl.ClassTime_t           #班別-時段對照表的原始檔案
WEEK_of_DAY = tl.WEEK_list     #WEEK_of_DAY - 日子j所屬的那一週
df_x = result.Schedule

score = final_score(A_t, nEMPLOYEE, nDAY, nW, nK, nT, nR, DEMAND, P0, P1, P2, P3, P4, SHIFTset, WEEK_of_DAY, nightdaylimit, S_BREAK, df_x.values.tolist())

print('score:',score)

# 下面這個現在在 tool 裡面檢查過了
# if cutoff == True:
#     print('\ngurobi運行被強迫中斷，因此以A2班填入空班別，目標式值可能較高。')


