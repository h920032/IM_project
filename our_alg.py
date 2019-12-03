#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import data.fixed.tool as tl
import data.fixed.gene_alg as gen
# import datetime, calendar, sys
"""============================================================================#
12/3
	- 建立主架構
============================================================================#"""

#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# 請大家把自己的函數放在 data/fixed/ (和tool.py同一個位置)
# 再將自己的函數引進這裡 (這樣主程式的版本比較好控管)
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#


#=============================================================================#
# import data
f = open('path.txt', "r")
dir_name = f.read().replace('\n', '')
result_x = './排班結果_'+str(year)+'_'+str(month)+'.csv'
result_y = './冗員與缺工人數_'+str(year)+'_'+str(month)+'.csv'
result = './其他資訊_'+str(year)+'_'+str(month)+'.xlsx'
#basic
A_t = pd.read_csv(dir_name + 'fixed/fix_class_time.csv', header = 0, index_col = 0)
DEMAND_t = pd.read_csv(dir_name+"進線人力.csv", header = 0, index_col = 0, engine='python').T
DATES = [ int(x) for x in DEMAND_t.index ]    #所有的日期 - 對照用
print('DATES = ',end='')
print(DATES)
#employees data
EMPLOYEE_t = pd.read_csv(dir_name+"EMPLOYEE.csv", header = 0) 



####NM 及 NW 從人壽提供之上個月的班表裡面計算
if month>1:
	lastmonth = pd.read_csv(dir_name + '排班結果_'+str(year)+'_'+str(month-1)+'.csv', engine='python')
else:
	lastmonth = pd.read_csv(dir_name + '排班結果_'+str(year-1)+'_1.csv', engine='python')
lastday_column = len(lastmonth.columns) 
lastday_row = lastmonth.shape[0]
lastday_ofmonth = lastmonth.iloc[0,(lastday_column-1)]
nEMPLOYEE = EMPLOYEE_t.shape[0]

#上個月的最後一天是週五，且有排晚班者，有則是1，沒有則是0

tl.calculate_NW (EMPLOYEE_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEMPLOYEE)

#上個月為斷頭週，並計算該週總共排了幾次晚班

tl.calculate_NM (EMPLOYEE_t,lastday_ofmonth,lastday_row,lastday_column,lastmonth,nEMPLOYEE)
NM_t = EMPLOYEE_t['NM']
NW_t = EMPLOYEE_t['NW']
#####

E_NAME = list(EMPLOYEE_t['Name_English'])       #E_NAME - 對照名字與員工index時使用
E_ID = [ str(x) for x in EMPLOYEE_t['ID'] ]   	#E_ID - 對照ID與員工index時使用
E_SENIOR_t = EMPLOYEE_t['Senior']
E_POSI_t = EMPLOYEE_t['Position']
E_SKILL_t = EMPLOYEE_t[['skill-phone','skill-CD','skill-chat','skill-outbound']]
SKILL_NAME = list(E_SKILL_t.columns)        #SKILL_NAME - 找員工組合、班別組合時使用

P_t = pd.read_csv(dir_name + 'parameters/軟限制權重.csv', header = None, index_col = 0, engine='python') 

#const
Kset_t = pd.read_csv(dir_name + 'fixed/fix_classes.csv', header = None, index_col = 0) #class set
SKset_t = pd.read_csv(dir_name + 'parameters/skills_classes.csv', header = None, index_col = 0) #class set for skills
# 下面的try/except都是為了因應條件全空時
try:
	M_t = pd.read_csv(dir_name + "特定班別、休假.csv", header = None, skiprows=[0])
except:
	M_t = pd.DataFrame()
try:
	L_t = pd.read_csv(dir_name + "parameters/下限.csv", header = None, skiprows=[0])
except:
	L_t = pd.DataFrame()
try:
	U_t = pd.read_csv(dir_name + "parameters/上限.csv", header = None, skiprows=[0])
except:
	U_t = pd.DataFrame()
try:
	Ratio_t = pd.read_csv(dir_name + "parameters/CSR年資占比.csv",header = None, skiprows=[0])
	SENIOR_bp = Ratio_t[3]
except:
	Ratio_t = pd.DataFrame()
	SENIOR_bp = []
try:
	timelimit = pd.read_csv(dir_name + "parameters/時間限制.csv", header = 0)
except:
	timelimit = 300	#預設跑五分鐘
nightdaylimit = EMPLOYEE_t['night_perWeek']

#============================================================================#
#Parameters
#-------number-------#
nEMPLOYEE = EMPLOYEE_t.shape[0]     #總員工人數
nDAY = len(DEMAND_t.index)          #總日數
nK = 19                             #班別種類數
nT = 24                             #總時段數
nR = 5                              #午休種類數
nW = tl.get_nW(year,month)          #總週數

nPOSI = 4                       	    #職稱數量 (=擁有特定職稱的總員工集合數
nSKILL = 4                          	#nVA技能數量 (=擁有特定技能的總員工集合數

#-------Basic-------#
CONTAIN = A_t.values.tolist()      #CONTAIN_kt - 1表示班別k包含時段t，0則否

DEMAND = DEMAND_t.values.tolist()  #DEMAND_jt - 日子j於時段t的需求人數
ASSIGN = []                        #ASSIGN_ijk - 員工i指定第j天須排班別k，形式為 [(i,j,k)]

for c in range(M_t.shape[0]):
    e = tl.TranName_t2n(M_t.iloc[c,0], E_ID)
    d = tl.TranName_t2n(M_t.iloc[c,1], DATES)
    k = tl.TranK_t2n( str(M_t.iloc[c,2]) )
    ASSIGN.append( (e, d, k) )

LMNIGHT = NM_t.values            #LMNIGHT_i - 表示員工i在上月終未滿一週的日子中曾排幾次晚班
FRINIGHT = NW_t.values           #FRINIGHT_i - 1表示員工i在上月最後一日且為週五的日子排晚班，0則否
# -------調整權重-------#
P0 = 100    					#目標式中的調整權重(lack)
P1 = P_t[1]['P1']    			#目標式中的調整權重(surplus)
P2 = P_t[1]['P2']   	    	#目標式中的調整權重(nightCount)
P3 = P_t[1]['P3']    	   		#目標式中的調整權重(breakCount)
P4 = P_t[1]['P4']    	 		#目標式中的調整權重(complement)

#-----排班特殊限制-----#
LOWER = L_t.values.tolist()       	#LOWER - 日期j，班別集合ks，職位p，上班人數下限
for i in range(len(LOWER)):
    d = tl.TranName_t2n( LOWER[i][0], DATES)
    LOWER[i][0] = d
UPPER = U_t.values.tolist()		   	#UPPER - 員工i，日子集合js，班別集合ks，排班次數上限
PERCENT = Ratio_t.values.tolist()	#PERCENT - 日子集合，班別集合，要求占比，年資分界線

#============================================================================#
#Sets
EMPLOYEE = [tmp for tmp in range(nEMPLOYEE)]    #EMPLOYEE - 員工集合，I=1,…,nI 
DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
TIME = [tmp for tmp in range(nT)]               #TIME - 工作時段集合，T=1,…,nT
BREAK = [tmp for tmp in range(nR)]              #BREAK - 午休方式，R=1,…,nR
WEEK = [tmp for tmp in range(nW)]               #WEEK - 週次集合，W=1,…,nW
SHIFT = [tmp for tmp in range(nK)]              #SHIFT - 班別種類集合，K=1,…,nK ;0代表休假
 
#-------員工集合-------#
E_POSITION = tl.SetPOSI(E_POSI_t)                                #E_POSITION - 擁有特定職稱的員工集合，POSI=1,…,nPOSI
E_SKILL = tl.SetSKILL(E_SKILL_t)                                 #E_SKILL - 擁有特定技能的員工集合，SKILL=1,…,nSKILL
E_SENIOR = [tl.SetSENIOR(E_SENIOR_t,tmp) for tmp in SENIOR_bp]   #E_SENIOR - 達到特定年資的員工集合    

#-------日子集合-------#
month_start = tl.get_startD(year,month)         #本月第一天是禮拜幾 (Mon=0, Tue=1..)
D_WEEK = tl.SetDAYW(month_start+1,nDAY,nW)  	#D_WEEK - 第 w 週中所包含的日子集合
DAYset = tl.SetDAY(month_start, nDAY)     		#DAYset - 通用日子集合 [all,Mon,Tue...]

#-------班別集合-------#
S_NIGHT = [11, 12, 13]                                          #S_NIGHT - 所有的晚班
S_BREAK = [[11,12],[1,7,14,15],[2,8,16,18],[3,9,17],[4,10]]     #Kr - 午休方式為 r 的班別 
SHIFTset= {}                                                    #SHIFTset - 通用的班別集合，S=1,…,nS
for ki in range(len(Kset_t)):
    SHIFTset[Kset_t.index[ki]] = [ tl.TranK_t2n(x) for x in Kset_t.iloc[ki].dropna().values ]
K_skill_not = []                                                #K_skill_not - 各技能的優先班別的補集
for ki in range(len(SKset_t)):
    sk = [ tl.TranK_t2n(x) for x in SKset_t.iloc[ki].dropna().values ]  #各個技能的優先班別
    K_skill_not.append( list( set(range(0,nK)).difference(set(sk)) ) )      #非優先的班別



"""============================================================================#
新變數
CAPACITY_WORK[i]: 員工i還能上班的日子數
CAPACITY_NIGHT[i,j]: 1表示員工i在日子j能排晚班，0則否
ALREADY[i,j]: 1表示員工i在日子j能排班，0則否
CURRENT_DEMAND[j,t]: 日子j時段t的剩餘需求人數
WEEK_of_DAY[j]: 日子j所屬的那一週
LIMIT_MATRIX[a]: LIMIT_ORDER函數所生成的matrix，預設5種排序
LIMIT_LIST[b]: LIMIT_MATRIX的第a種限制式排序的限制式順序
n_LIMIT_LIST: 人數硬限制式的個數
LIMIT: LIMIT_LIST的第b個限制式
CSR_LIST: CSR_ORDER函數所生成的list
BOUND: 人數下限

總表的資料結構：bool  x[i, j, k]	 	i=人, j=日子, k=班別

限制式的資料結構：
[	上限/下限/比例 (‘upper’/’lower’/’ratio’),
	人的組合, 
	工作日的組合, 
	班別的組合, 
	幾人/比例 
]
============================================================================#"""

#========================================================================#
# class
#========================================================================#
# public class Pool{
# 	df_x : 員工班表
# 	df_y: 缺工人數表
# 	df_percent_day: 每天缺工百分比表
# 	df_percent_time: 每個時段缺工百分比表
# 	df_nightcount: 員工本月晚班次數
# 	df_resttime: 員工休息時間表
# }

#========================================================================#
# Global Variables
#========================================================================#
year = 2019
month = 4

# 生成Initial pool的100個親代
# Pool INITIAL_POOL[100]

# 產生親代的迴圈數
parent = 100	# int


#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# 函數 (工作分配)
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#

#========================================================================#
# LIMIT_ORDER(): 生成多組限制式 matrix 的函數 (林亭)
#========================================================================#



#========================================================================#
# CSR_ORDER(): 排序員工沒用度的函數 (林亭)
#========================================================================#





#========================================================================#
# ABLE(i,j,k): 確認員工i在日子j是否可排班別k (嬿鎔)
#========================================================================#



#========================================================================#
# ARRANGEMENT(): 安排好空著的班別的函數 (嬿鎔)
#========================================================================#


#========================================================================#
# CONFIRM(): 確認解是否可行的函數 (學濂)
#========================================================================#




#========================================================================#
# GENE(): 切分並交配的函數 (星宇)
#========================================================================#
def GENE(avaliable_sol, fix, nDAY, nEMPLOYEE, gen):
	return gen.gene_alg(avaliable_sol, fix, nDAY, nEMPLOYEE, gen)



#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# main function
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#



#=======================================================================================================#
#====================================================================================================#
#=================================================================================================#
# 輸出
#=================================================================================================#
#====================================================================================================#
#=======================================================================================================#





#========================================================================#
# program end
#========================================================================#
print('\n\n*** Done ***')