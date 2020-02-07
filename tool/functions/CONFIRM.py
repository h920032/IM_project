import pandas as pd
import tool.tool as tl

"""
To confiirm if schedule generated meets the necessary constraints
@author:Lien

necessary constraints:

(1)每天每位員工只能只能被指派一種班  ->  don't need to be checked

(2)滿足每位員工排指定特定班型  ->Assign.csv

(3)每位員工每週只能排指定天數的晚班，且不能連續 -> Employee.csv    

(4)在特定日子中的指定班別，針對特定職位的員工，有不上班人數上限 -> lower_limit.csv

(5)在每週特定日子每位員工排某些班別有次數上限 ->upper_limit.csv

(6)有特定技能之員工排特定班別 -> Employee.csv 

(7)在特定日子中數個指定班別，針對特定群組員工，必續佔總排班人數特定比例以上 senior_limit.csv

(8)針對特定技能的員工，有上班人數上限 ->class_upperlimit.csv

(9)若在非ASSIGN情況下不能排AS、MS、O班

(10)無特殊技能者不得排特殊技能班

"""

#schedule為班表二維list

def confirm(schedule):
    
    nE = tl.nE
    nDAY      = tl.nD
    LMNIGHT  = tl.LastWEEK_night 
    FRINIGHT = tl.LastDAY_night
    
    EMPLOYEE_t = tl.Employee_t
    assign = tl.ASSIGN
    SHIFTset= tl.K_CLASS_set
    SKILL_list = tl.SKILL_list
    SKILLset= tl.SK_CLASS_set           
    S_NIGHT = SHIFTset['night']                    
    D_WEEK = tl.D_WEEK_set
    nightdaylimit = EMPLOYEE_t['night_perWeek']
    EMPLOYEE = [tmp for tmp in range(nE)]
    E_POSITION  = tl.E_POSI_set
    E_SKILL     = tl.E_SKILL_set
    E_SENIOR    = tl.E_SENIOR_set
    LOWER = tl.LOWER
    UPPER = tl.UPPER
    Upper_shift = tl.Upper_shift
    weekdaylist = tl.D_WDAY_set
    PERCENT = tl.PERCENT
    NOTPHONE_CLASS = tl.NOTPHONE_CLASS
    NOTPHONE_CLASS_special = tl.NOTPHONE_CLASS_special
    VACnextdayset = tl.AH_list
    NOT_VACnextdayset = tl.NAH_list

    as_bool = True
    as_err=''
    
    #(2)滿足每位員工排指定特定班型
    #需要參數:班表(schedule) 指定排班(assign)
    for i in assign:  
        as_index = i[0]
        as_day = i[1]
        as_worktype = i[2]
        if schedule[as_index][as_day] != as_worktype:
            as_bool = False
            as_err +=str(as_index)
            as_err +='th employee'
            as_err +='is not successfully assigned to'
            as_err +=str(as_worktype)
            as_err +=' at '
            as_err +=str(as_day)
            as_err +='th'
            as_err +='working day.'
            break

    if as_bool == False:
         return as_err

    #=========================================================================================================================================================
    #(3)每位員工每週只能排指定天數的晚班，且不能連續
    #需要參數:班表(schedule) 晚班集合(S_NIGHT)  第 w 週中所包含的日子集合(D_WEEK)) 每位員工每周能排的晚班次數(nightdaylimit) (總日子數)nDAY FRINIGHT LMNIGHT
    
    night_bool = True
    night_err =''
    
    #連續晚班
    for i in range(len(schedule)):
        for k in range(nDAY):
            if k == 0:
                if FRINIGHT[i] == 1 and schedule[i][0] in S_NIGHT:
                    night_bool = False
                    night_err += str(i)
                    night_err += 'th employee'
                    night_err += ' can not be assigned to night class on the 0th day because he or she has been assigned night class on the last day of last month '
                    
            if k != (nDAY - 1):
                if schedule[i][k] in S_NIGHT and schedule[i][k+1] in S_NIGHT:
                    night_bool = False
                    night_err += str(i)
                    night_err += 'th employee'
                    night_err += 'has been assigned night class continuously in '
                    night_err += str(k)
                    night_err += 'th day and'
                    night_err += str(k+1)
                    night_err += 'th day'
                    break
        if night_bool == False:
            break

    if night_bool == False:
        return night_err

    for i in range(len(schedule)):
        nightdaylimit_int = int(nightdaylimit[i])
        #第j周
        for j in range(len(D_WEEK)):
            
            night_count = 0
            #第j周的第k天
            for k in D_WEEK[j]:
                for r in range(len(S_NIGHT)):
                    
                    if schedule[i][k] == S_NIGHT[r]:
                        night_count+=1
                      
                        break
            
            #晚班次數超過上限
            if j != 0:
                if night_count > nightdaylimit_int and night_err=='':
                    night_bool = False
                    night_err += str(i)
                    night_err += 'th employee '
                    night_err += ' has been assigned too many night class at '
                    night_err += str(j)
                    night_err += 'th week'
                    break
            else:
                if night_count + LMNIGHT[i] > nightdaylimit_int and night_err=='':
                    night_bool = False
                    night_err += str(i)
                    night_err += 'th employee '
                    night_err += ' has been assigned too many night class at '
                    night_err += str(j)
                    night_err += 'th week'
                    break
 
        
        if night_bool == False:
            break


    if night_bool == False:
        return night_err

    #=========================================================================================================================================================
    #(4)在特定日子中的指定班別，針對特定職位的員工，有不上班人數上限
    #需要參數:LOWER,  SHIFTset, E_POSITION, schedule
    l_limit_bool = True
    l_limit_err = ''

    for i in range(len(LOWER)):
        day = LOWER[i][0] 
        class_type = LOWER[i][1]
        require_type = SHIFTset[class_type]
        position = LOWER[i][2] 
        e_in_require_position = E_POSITION[position]
        l_limit = LOWER[i][3]
        count = 0
        for j in e_in_require_position:
            for k in range(len(require_type)):
                if schedule[j][day] == require_type[k]:
                    count+=1
            
            if count >= l_limit:
                break
        
        if count < l_limit:
            l_limit_bool= False
            l_limit_err +='There are not enough '
            l_limit_err +=position
            l_limit_err +=' 以上人員 for '
            l_limit_err +=class_type
            l_limit_err +=' class at '
            l_limit_err +=str(day)
            l_limit_err +='th working day '
            break
    if l_limit_bool == False:
        return l_limit_err
    

    #=========================================================================================================================================================
    #(5)在每週特定日子每位員工排某些班別有次數上限
    #需要參數:schedule, UPPER, weekdaylist,  SHIFTset
    #weekdaylist = {'Mon':[0,7,14,21], 'Tue':[1,8,15,22],...,.....}
    u_limit_bool = True
    u_limit_err =''
    for i in range(len(UPPER)):
        csr = UPPER[i][0]
        day = UPPER[i][1]
        require_day = weekdaylist[day]
        class_type = UPPER[i][2]
        require_type = SHIFTset[class_type]
        u_limit = UPPER[i][3]
       
        for j in [csr]:
            count = 0
            for k in require_day:
                for r in range(len(require_type)):
                    if schedule[j][k] == require_type[r]:
                        count+=1

                if count > u_limit:
                    u_limit_bool = False
                    break
            if count > u_limit:
                u_limit_bool = False
                u_limit_err +=str(i)
                u_limit_err +='th employee is assinged too many '
                u_limit_err +=class_type
                u_limit_err +=' class on every'
                u_limit_err +=day
                break

    if u_limit_bool ==False:
        return u_limit_err
    
    #=========================================================================================================================================================
    #(6)在特定日子中的指定班別，針對特定技能的員工，有上班人數規定
    #需要參數:schedule, NOTPHONE_CLASS, NOTPHONE_CLASS_special, weekdaylist, SHIFTset, E_SKILL, EMPLOYEE_t, VACnextdayset, NOT_VACnextdayset
    sk_limit_bool = True
    sk_limit_err = ''

    for i in range(len(NOTPHONE_CLASS)):
        require_day = weekdaylist['all'] 
        class_type = NOTPHONE_CLASS[i][0]
        require_type = SHIFTset[class_type]
        skill = NOTPHONE_CLASS[i][2] 
        e_in_require_skill = E_SKILL[skill]
        sk_limit = NOTPHONE_CLASS[i][1]
        
        day0 = -1
        day1 = -1
        day2 = -1
        for k in require_day:  
            for r in range(len(require_type)):
                count = 0
                other = 0
                for j in e_in_require_skill:
                    if schedule[j][k] == require_type[r]:
                        count+=1
                for j2 in EMPLOYEE:
                    if j2 not in e_in_require_skill:
                        if schedule[j2][k] == require_type[r]:
                            other+=1 

            if other > 0:
                day0 = k
                break
            if count == sk_limit:
                continue
            elif count < sk_limit:
                day1 = k
                break
            else:
                day2 = k
                break
        
        if count < sk_limit: 
            sk_limit_bool= False
            sk_limit_err +='There are not enough '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 for '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day1)
            sk_limit_err +='th working day '
            break
        elif count > sk_limit:
            sk_limit_bool= False
            sk_limit_err +='There are too many '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 for '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day2)
            sk_limit_err +='th working day '
        elif other > 0:
            sk_limit_bool= False
            sk_limit_err +='Someone who does not belong to '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 was assigned to '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day0)
            sk_limit_err +='th working day '
    if sk_limit_bool == False:
        return sk_limit_err
    


    for i in range(len(NOTPHONE_CLASS_special)):
        require_day1 = NOT_VACnextdayset
        require_day2 = VACnextdayset 
        class_type = NOTPHONE_CLASS_special[i][0]
        require_type = SHIFTset[class_type]
        skill = NOTPHONE_CLASS_special[i][2] 
        e_in_require_skill = E_SKILL[skill]
        sk_limit1 = NOTPHONE_CLASS_special[i][1]
        sk_limit2 = NOTPHONE_CLASS_special[i][3]
        
        day0 = -1
        day1 = -1
        day2 = -1
        for k in require_day1:    
            for r in range(len(require_type)):
                count = 0
                other = 0
                for j in e_in_require_skill:
                    if schedule[j][k] == require_type[r]:
                        count+=1
                for j2 in EMPLOYEE:
                    if j2 not in e_in_require_skill:
                        if schedule[j2][k] == require_type[r]:
                            other+=1

            if other > 0:
                day0 = k
                break
            if count == sk_limit1:
                continue
            elif count < sk_limit1:
                day1 = k
                break
            else:
                day2 = k
                break
        
        if count < sk_limit1: 
            sk_limit_bool= False
            sk_limit_err +='There are not enough '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 for '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day1)
            sk_limit_err +='th working day '
            break
        elif count > sk_limit1:
            sk_limit_bool= False
            sk_limit_err +='There are too many '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 for '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day2)
            sk_limit_err +='th working day '
        elif other > 0:
            sk_limit_bool= False
            sk_limit_err +='Someone who does not belong to '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 was assigned to '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day0)
            sk_limit_err +='th working day '
        
        for k in require_day2:    
            for r in range(len(require_type)):
                count = 0
                other = 0
                for j in e_in_require_skill:
                    if schedule[j][k] == require_type[r]:
                        count+=1
                for j2 in EMPLOYEE:
                    if j2 not in e_in_require_skill:
                        if schedule[j2][k] == require_type[r]:
                            other+=1
            
            if other > 0:
                day0 = k
                break
            if count == sk_limit2:
                continue
            elif count < sk_limit2:
                day1 = k
                break
            else:
                day2 = k
                break
        
        if count < sk_limit2: 
            sk_limit_bool= False
            sk_limit_err +='There are not enough '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 for '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day1)
            sk_limit_err +='th working day '
            break
        elif count > sk_limit2:
            sk_limit_bool= False
            sk_limit_err +='There are too many '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 for '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day2)
            sk_limit_err +='th working day '
        elif other > 0:
            sk_limit_bool= False
            sk_limit_err +='Someone who does not belong to '
            sk_limit_err +=skill
            sk_limit_err +=' 技能人員 was assigned to '
            sk_limit_err +=class_type
            sk_limit_err +=' class at '
            sk_limit_err +=str(day0)
            sk_limit_err +='th working day '
        
    if sk_limit_bool == False:
        return sk_limit_err
    
    
    #=========================================================================================================================================================
    #(7)在特定日子中數個指定班別，針對特定群組員工，必須佔總排班人數特定比例以上
    #需要參數: schedule, E_SENIOR(符合特定年資的員工集合) 
    #

    senior_bool = True
    senior_err =''
    
    for n in range(len(PERCENT)):
        day = PERCENT[n][0]
        require_day = weekdaylist[day]
        class_type = PERCENT[n][1]
        require_type = SHIFTset[class_type]
        ratio = PERCENT[n][2]
        people_in_class = 0
        skilled_people_in_class = 0
        for j in require_day:
            for r in range(len(require_type)):
                for i in E_SENIOR[n]:       #E_SENIOR[n]是一組員工集合(i)，不是班別集合(k)        
                    if schedule[i][j] == require_type[r]:   #報錯：list index out of range
                        skilled_people_in_class += 1

                for i in range(len(schedule)):
                    if schedule[i][j] == require_type[r]:
                        people_in_class += 1
                        
        
        if skilled_people_in_class/people_in_class < ratio:     #若年資足夠者少於指定比例，顯示錯誤
            senior_bool = False
            senior_err = 'There is a lack of employee who has been in the career more than ' + str(PERCENT[n][3]) +  ' years on ' + str(day)
        
    
    if senior_bool == False:
        return senior_err
    

    
    #=========================================================================================================================================================
    #(8)針對特定技能的員工，有上班人數上限
    #需要參數:schedule, Upper_shift, SHIFTset
    us_limit_bool = True
    us_limit_err =''
    for i in range(len(Upper_shift)):
        require_day = weekdaylist['all']
        class_type = Upper_shift[i][0]
        require_type = SHIFTset[class_type] 
        e_in_require_skill = E_SKILL['phone']
        us_limit = Upper_shift[i][1]
       
        for j in e_in_require_skill:
            count = 0
            day = 0
            for k in require_day:
                for r in range(len(require_type)):
                    if schedule[j][k] == require_type[r]:
                        count+=1
            
                if count > us_limit:
                    us_limit_bool = False
                    break
            if count > us_limit:
                us_limit_bool = False
                us_limit_err +=str(j)
                us_limit_err +='th employee is assinged too many '
                us_limit_err +=class_type
                us_limit_err +=' class in this month '
                break

    if us_limit_bool ==False:
        return us_limit_err
    
    #=========================================================================================================================================================
    #(9)若在非ASSIGN情況下不能排AS、MS、O班
    #需要參數:schedule, assign, SHIFTset
    not_assigned_bool = True
    not_assigned_err =''
    for i in range(len(schedule)):
        #找對i員工的assign 並存到 aasign_for_i
        assign_for_i =[]
        for q in range(len(assign)):
            as_index =  assign[q][0]  
            as_day = assign[q][1]
            as_class = assign[q][2]
            as_list = []
            
            if as_index == i:
                as_list.append(as_day)
                as_list.append(as_class)
                assign_for_i.append(as_list)
        
        #對第i個員工的日子j
        for j in range(len(schedule[i])):
            
            #AS、MS、O
            if schedule[i][j] in SHIFTset['not_assigned']:
                as_ok = False
                for q in range(len(assign_for_i)):

                    if (assign_for_i[q][0]  == j) and (assign_for_i[q][1] in SHIFTset['not_assigned']):
                        as_ok = True
                        break

                if as_ok != True:
                    not_assigned_bool = False
                    not_assigned_err +=str(i)
                    not_assigned_err +='th employee cannot be assinged to '
                    not_assigned_err +=str(schedule[i][j])
                    not_assigned_err +=' at '
                    not_assigned_err +=str(j)
                    not_assigned_err +='th'
                    not_assigned_err +='working day.'
                    break
        
        if not_assigned_bool == False:
            break
    
    if not_assigned_bool == False:
        return not_assigned_err
    
    #=========================================================================================================================================================
    #(10)無特殊技能者不得排特殊技能班
    #需要參數:schedule, SKILL_list, SKILLset
    not_skilled_bool = True
    not_skilled_err =''
    for i in range(len(schedule)):
        #對第i個員工的日子j
        for j in range(len(schedule[i])):
            for sk in SKILL_list:
                #other
                if schedule[i][j] in SKILLset[sk]:
                    sk_ok = False
                    if i in E_SKILL[sk]:
                        sk_ok = True

                    if sk_ok != True:
                        not_skilled_bool = False
                        not_skilled_err +=str(i)
                        not_skilled_err +='th employee does not have the skill in able to be assinged to '
                        not_skilled_err +=str(schedule[i][j])
                        not_skilled_err +=' at '
                        not_skilled_err +=str(j)
                        not_skilled_err +='th'
                        not_skilled_err +='working day.'
                        break
                    break
            if not_skilled_bool == False:
                break
        
        if not_skilled_bool == False:
            break
    
    if not_skilled_bool == False:
        return not_skilled_err


    success_mes = 'All constraints are met.'
    return success_mes