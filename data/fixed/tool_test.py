# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: 林亭
"""
import math, re
import pandas as pd
from datetime import datetime, date

"""===========================================================
    參數：
        TestPath
    ======
    外部用函式：

    ======
    內部工具函式：
        readFiile(dir, header_, skiprows_,index_col_)
==========================================================="""

"""==========================================================================================================
globle參數
=========================================================================================================="""

# 日期相關
# Year = 0
# Month = 0

# 班別
K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB'] #這個得改掉

# 輸出檔名
# ScheduleFileName = 'Schedule_'+str(Year)+'_'+str(Month)+'.csv'
# LackFileName = 'lack_'+str(Year)+'_'+str(Month)+'.csv'

# 測試檔案檔名 - 沒有要測試時請將TestPath留空白
# TestPath = ""
TestPath = "../../test_data/"
EmployeeTest = "_30人"
AssignTest = "_30人各休一"
NeedTest = "_標準"





"""==========================================================================================================
import data
    要輸出的東西：
=========================================================================================================="""

"""===========================================
    def function
==========================================="""
#讀檔：try/except是為了因應條件全空時
def readFile(dir, header_=None, skiprows_=[0], index_col_=None):
    try:
        t = pd.read_csv(dir, header = header_, skiprows=skiprows_, index_col=index_col_, engine='python')
    except:
        t = pd.DataFrame()
    return t

"""===========================================
    read basic file
==========================================="""
#讀檔路徑import data
try:
    f = open('../../path.txt', "r")
    dir_name = '../../'+f.read().replace('\n', '')
except:
    dir_name = './data/'   #預設資料路徑：./data/

# 測試用，這些之後要刪掉
if TestPath != "":
    dir_name = TestPath
    parameters_dir = TestPath
else:
    EmployeeTest = ""
    AssignTest = ""
    NeedTest = ""

print('Read file from',dir_name)


# year/month
date = pd.read_csv(dir_name + 'per_month/Date.csv', header = None, index_col = 0)
year = int(date.iloc[0,0])
month = int(date.iloc[1,0])

"""===========================================
    read /per_month
==========================================="""
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

"""===========================================
    read /parameters
==========================================="""
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


"""===========================================
    read /fixed
==========================================="""
Kset_t = pd.read_csv(dir_name + 'fixed/fix_classes.csv', header = None, index_col = 0) #class set
A_t = pd.read_csv(dir_name + 'fixed/fix_class_time.csv', header = 0, index_col = 0)









"""==========================================================================================================
# 輸出
# csv:班表、缺工冗員表
# 其他資訊：xlsx檔
=========================================================================================================="""







"""==========================================================================================================
其他工具
=========================================================================================================="""

"""===========================================
    Text-numberID translate function
==========================================="""
def Tran_t2n(text, names=K_type):
    try:
        c = names.index(text)
    except:
        print('Tran_t2n():',text,"not in ",names[0:3],'...')
        c = None
    return c