import pandas as pd

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

"""

#schedule為班表二維list

def confirm(schedule, assign, S_NIGHT, D_WEEK, nightdaylimit, LOWER, SHIFTset, E_POSITION, UPPER, weekdaylist, PERCENT, E_SENIOR):
    

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
    #需要參數:班表(schedule) 晚班集合(S_NIGHT)  第 w 週中所包含的日子集合(D_WEEK)) 每位員工每周能排的晚班次數(nightdaylimit) 
    
    night_bool = True
    night_err =''
    

    for i in range(len(schedule)):
        nightdaylimit_int = int(nightdaylimit[i])
        #第j周
        for j in range(len(D_WEEK)):
            
            night_count = 0
            night=[]
            #第j周的第k天
            for k in D_WEEK[j]:
                night_flag = False
                for r in range(len(S_NIGHT)):
                    
                    if schedule[i][k] == S_NIGHT[r]:
                        night_count+=1
                        night_flag = True
                      
                        break
                night.append(night_flag)
            #連續晚班
            for k in range(len(D_WEEK[j])):
                if k != (len(D_WEEK[j]) - 1):
                    if night[k] == True & night[k+1] == True:
                        night_bool = False
                        night_err += str(i)
                        night_err += 'th employee'
                        night_err += 'has been assigned night class continuously at '
                        night_err += str(j)
                        night_err += 'th week'
                        break
            
            
            #晚班次數超過上限
            if night_count > nightdaylimit_int and night_err=='':
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
                    break

            if count >= l_limit:
                break
        
        if count < l_limit:
            l_limit_bool= False
            l_limit_err +='There are not enough '
            l_limit_err +=position
            l_limit_err +=' for '
            l_limit_err +=class_type
            l_limit_err +=' class at '
            l_limit_err +=str(i)
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
        day = UPPER[i][0]
        require_day = weekdaylist[day]
        class_type = UPPER[i][1]
        require_type = SHIFTset[class_type]
        u_limit = UPPER[i][2]
       
        for j in range(len(schedule)):
            count = 0
            for k in require_day:
                for r in range(len(require_type)):
                    if schedule[j][k] == require_type[r]:
                        count+=1
                        break
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
    #(6)有特定技能之員工排特定班別
    #需要參數: schedule, E_SKILL, K_skill
    #

    # c_phone = K_skill['phone']
    # c_CD=K_skill['CD']
    # c_chat=K_skill['chat']
    # c_outbound=K_skill['outbound']
    # e_phone = E_SKILL['phone']
    # e_CD=E_SKILL['CD']
    # e_chat=E_SKILL['chat']
    # e_outbound=E_SKILL['outbound']
    # if len(c_phone) != 0:
    #     for i in c_phone:
            
    
    
    
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
            for i in E_SENIOR[n]:       #E_SENIOR[n]是一組員工集合(i)，不是班別集合(k)        
                
                for r in range(len(require_type)):
                      if schedule[i][j] == require_type[r]:   #報錯：list index out of range
                        skilled_people_in_class += 1
                        break
            for i in range(len(schedule)):
                for r in range(len(require_type)):
                    if schedule[i][j] == require_type[r]:
                        people_in_class += 1
                        break
        
        if skilled_people_in_class/people_in_class < ratio:     #若年資足夠者少於指定比例，顯示錯誤
            senior_bool = False
            senior_err = 'There is a lack of employee who has been in the career more than ' + str(PERCENT[n][3]) +  ' years on ' + str(day)
    
    if senior_bool == False:
        return senior_err
    


    success_mes = 'All constraints are met.'
    return success_mes