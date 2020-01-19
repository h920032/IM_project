import numpy as np
import pandas as pd
import os
import tool.tool as tl
import datetime, calendar

def score(df_x,fixed_dir = tl.DIR_PARA+'fixed/'):
    
    main = "./tool/c++/score "

    A_t = pd.read_csv(fixed_dir + 'fix_class_time.csv', header = 0, index_col = 0)
    EMPLOYEE_t = tl.Employee_t
    
    Shift_name = tl.CLASS_list
    nightdaylimit = EMPLOYEE_t['night_perWeek']

    year  = tl.YEAR
    month = tl.MONTH

    nEMPLOYEE = tl.nE
    nDAY = tl.nD
    nK = tl.nK
    nT = tl.nT
    nR = tl.nR
    nW = tl.nW
    mDAY = tl.mDAY
    DEMAND = tl.DEMAND

    P0, P1, P2, P3, P4 = tl.P

    SHIFTset = tl.K_CLASS_set
    s_break = tl.K_BREAK_set 
    
    DAY = [tmp for tmp in range(nDAY)]              #DAY - 日子集合，J=0,…,nJ-1
    DATES = tl.DATE_list    #所有的日期 - 對照用
    D_WEEK = tl.D_WEEK_set  	#D_WEEK - 第 w 週中所包含的日子集合
    WEEK_of_DAY = tl.WEEK_list #WEEK_of_DAY - 日子j所屬的那一週\

    #1
    A_t_s = ""
    for i in A_t.values.tolist():
        for j in i:
            A_t_s += str(j)
            A_t_s += ","
        A_t_s += "!"
    main += A_t_s
    main += " "

    #2
    Shift_name_s = ""
    for i in Shift_name:
        Shift_name_s += i
        Shift_name_s += ","
    main += Shift_name_s
    main += " "

    #3
    nightdaylimit_s = ""
    for i in nightdaylimit.values.tolist():
        nightdaylimit_s += str(i)
        nightdaylimit_s += ","
    main += nightdaylimit_s
    main += " "

    #4
    year_s = str(year)
    month_s = str(month)
    nEMPLOYEE_s = str(nEMPLOYEE)
    nDAY_s = str(nDAY)
    nK_s = str(nK)
    nT_s = str(nT)
    nR_s = str(nR)
    nW_s = str(nW)
    mDAY_s = str(mDAY)
    
    main += year_s
    main += " "
    main += month_s
    main += " "
    main += nEMPLOYEE_s
    main += " "
    main += nDAY_s
    main += " "
    main += nK_s
    main += " "
    main += nT_s
    main += " "
    main += nR_s
    main += " "
    main += nW_s
    main += " "
    main += mDAY_s
    main += " "

    #13
    DEMAND_s = ""
    for i in DEMAND:
        for j in i:
            DEMAND_s += str(j)
            DEMAND_s += ","
        DEMAND_s += "!"
    main += DEMAND_s
    main += " "
    
    #14
    P0_s = str(P0)
    P1_s = str(P1)
    P2_s = str(P2)
    P3_s = str(P3)
    P4_s = str(P4)

    main += P0_s
    main += " "
    main += P1_s
    main += " "
    main += P2_s
    main += " "
    main += P3_s
    main += " "
    main += P4_s
    main += " "

    #19
    all_s = ""
    morning_s = ""
    noon_s = ""
    night_s = ""
    phone_s = ""
    other_s = ""
    for i in SHIFTset['all']:
        all_s += str(i)
        all_s += ","
    for i in SHIFTset['morning']:
        morning_s += str(i)
        morning_s += ","
    for i in SHIFTset['noon']:
        noon_s += str(i)
        noon_s += ","
    for i in SHIFTset['night']:
        night_s += str(i)
        night_s += ","
    for i in SHIFTset['phone']:
        phone_s += str(i)
        phone_s += ","
    for i in SHIFTset['other']:
        other_s += str(i)
        other_s += ","
    
    main += all_s
    main += " "
    main += morning_s
    main += " "
    main += noon_s
    main += " "
    main += night_s
    main += " "
    main += phone_s
    main += " "
    main += other_s
    main += " "

    #25
    s_break_s = ""
    for i in s_break:
        for j in i:
            s_break_s += str(j)
            s_break_s += ","
        s_break_s += "!"
    
    main += s_break_s
    main += " "
    
    #26
    DAY_s = ""
    for i in DAY:
        DAY_s += str(i)
        DAY_s += ","

    main += DAY_s
    main += " "
    
    #27
    DATES_s = ""
    for i in DATES:
        DATES_s += str(i)
        DATES_s += ","

    main += DATES_s
    main += " "

    #28
    D_WEEK_s = ""
    for i in D_WEEK:
        for j in i:
            D_WEEK_s += str(j)
            D_WEEK_s += ","
        D_WEEK_s += "!"

    main += D_WEEK_s
    main += " "

    #29
    WEEK_of_DAY_s = ""
    for i in WEEK_of_DAY:
        WEEK_of_DAY_s += str(i)
        WEEK_of_DAY_s += ","

    main += WEEK_of_DAY_s
    main += " "

    #30
    df_x_s = ""
    for i in df_x.values:
        for j in i:
            df_x_s += str(j)
            df_x_s += ","
        df_x_s += "!"

    main += df_x_s
    main += " "

    # print(df_x_s)
    f = os.popen(main)
    data = f.readlines()
    f.close()
    #os.system(main)
    #print(data)
    return int(data[0])
