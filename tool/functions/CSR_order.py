#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd 

def CSR_ORDER(which_way,what_order,CSR_List,EMPLOYEE, Posi, nightbound):
    EMPLOYEE_t = EMPLOYEE.copy()
    ## 以員工技能少、年資低、職位低為優先        
    if (what_order == "lower"):
        nEMPLOYEE = EMPLOYEE_t.shape[0]
        available_CSR = len(CSR_List)
        
        index = range(0,1)
        small_dataframe = pd.DataFrame(index=index,columns=['Name_English','Senior','Position','skill-phone','skill-CD','skill-chat','skill-outbound','night_perWeek'])
        ## 把職位轉為數字以便排優先順序        
        for i in range (nEMPLOYEE) :
            if nightbound == True:
                EMPLOYEE_t.at[i,'night_perWeek'] = 7 - EMPLOYEE_t.iloc[i,9]
            for j in range(len(Posi)):
                if (EMPLOYEE_t.iloc[i,4] == Posi[j]):                
                    EMPLOYEE_t.at[i,'Position'] = j
                    break
                               
        temp_dataframe = EMPLOYEE_t.iloc[:,[0,3,4,5,6,7,8,9]]
        
        for i in range (nEMPLOYEE) :            
            for j in range (available_CSR):                
                if (CSR_List[j] == int(temp_dataframe.index.values[i])): 
                    small_dataframe = pd.concat([temp_dataframe.iloc[[i],:],small_dataframe],sort = False)
        
        small_dataframe = small_dataframe.dropna(thresh=2)
        sorted_dataframe = small_dataframe.sort_values(['skill-chat','skill-outbound','skill-CD','skill-phone','night_perWeek','Senior','Position'],ascending = True)
        
        
        newCSR_List = list()
        for i in range (len(sorted_dataframe)):           
            newCSR_List.append(int(sorted_dataframe.index.values[i]))
  
  ## 隨機再生出五個CRS_list提供挑選，交換最不重要的幾個人的順序            
        if(which_way == "a"):
            order_a = newCSR_List.copy()
            return (order_a)
        elif (which_way == "b"):
            order_b = newCSR_List.copy()
            order_b[0],order_b[2] = order_b[2], order_b[0]
            return (order_b)
        elif (which_way == "c"):
            order_c = newCSR_List.copy()
            order_c[1],order_c[2] = order_c[2], order_c[1]
            return (order_c)
        elif (which_way == "d"):
            order_d = newCSR_List.copy()
            order_d[0],order_d[1] = order_d[1],order_d[0]
            return (order_d)
        elif (which_way == "e"):
            order_e = newCSR_List.copy()
            order_e[0],order_e[1] = order_e[1],order_e[0]
            order_e[0],order_e[2] = order_e[2],order_e[0]
            return (order_e)            
        return (newCSR_List)
    ## 以技能少、職位低、年資低為優先 
    elif (what_order == "ratio"):
        nEMPLOYEE = EMPLOYEE_t.shape[0]
        available_CSR = len(CSR_List)
        
        for i in range (nEMPLOYEE) :
            if nightbound == True:
                EMPLOYEE_t.at[i,'night_perWeek'] = 7 - EMPLOYEE_t.iloc[i,9]
        temp_dataframe = EMPLOYEE_t.iloc[:,[0,3,4,5,6,7,8,9]]
        
        index = range(0,1)
        small_dataframe = pd.DataFrame(index=index,columns=['Name_English','Senior','Position','skill-phone','skill-CD','skill-chat','skill-outbound','night_perWeek'])
        
        for i in range (nEMPLOYEE) :            
            for j in range (available_CSR):                
                if (CSR_List[j] == int(temp_dataframe.index.values[i])): 
                    small_dataframe = pd.concat([temp_dataframe.iloc[[i],:],small_dataframe],sort = False)
        
        small_dataframe = small_dataframe.dropna(thresh=2)
        sorted_dataframe = small_dataframe.sort_values(['skill-chat','skill-outbound','skill-CD','skill-phone','night_perWeek','Position','Senior'],ascending = True)
        
        
        newCSR_List = list()
        for i in range (len(sorted_dataframe)):           
            newCSR_List.append(int(sorted_dataframe.index.values[i]))
           
        if(which_way == "a"):
            order_a = newCSR_List.copy()
            return (order_a)
        elif (which_way == "b"):
            order_b = newCSR_List.copy()
            order_b[0],order_b[2] = order_b[2], order_b[0]
            return (order_b)
        elif (which_way == "c"):
            order_c = newCSR_List.copy()
            order_c[1],order_c[2] = order_c[2], order_c[1]
            return (order_c)
        elif (which_way == "d"):
            order_d = newCSR_List.copy()
            order_d[0],order_d[1] = order_d[1],order_d[0]
            return (order_d)
        elif (which_way == "e"):
            order_e = newCSR_List.copy()
            order_e[0],order_e[1] = order_e[1],order_e[0]
            order_e[0],order_e[2] = order_e[2],order_e[0]
            return (order_e)            
        
        return (newCSR_List)
    ## 技能員工當中先排年資淺再排職位低的員工      
    elif (what_order == "skill" or what_order == "skill_special"):
        nEMPLOYEE = EMPLOYEE_t.shape[0]
        available_CSR = len(CSR_List)
        
        #temp_dataframe = EMPLOYEE_t.iloc[:,[0,3]]
        
        index = range(0,1)
        small_dataframe = pd.DataFrame(index=index,columns=['Name_English','Senior','Position','skill-CD','skill-chat','skill-outbound','night_perWeek'])
        ## 把職位轉為數字以便排優先順序        
        for i in range (nEMPLOYEE) :
            #if nightbound == True:
            #   EMPLOYEE_t.at[i,'night_perWeek'] = 7 - EMPLOYEE_t.iloc[i,9]
            for j in range(len(Posi)):
                if (EMPLOYEE_t.iloc[i,4] == Posi[j]):                
                    EMPLOYEE_t.at[i,'Position'] = j
                    break
                                
        temp_dataframe = EMPLOYEE_t.iloc[:,[0,3,4,6,7,8,9]]

        for i in range (nEMPLOYEE) :            
            for j in range (available_CSR):                
                if (CSR_List[j] == int(temp_dataframe.index.values[i])): 
                    small_dataframe = pd.concat([temp_dataframe.iloc[[i],:],small_dataframe],sort = False)
        
        small_dataframe = small_dataframe.dropna(thresh=2)
        sorted_dataframe = small_dataframe.sort_values(['Position','Senior','night_perWeek'],ascending = True)
        
        newCSR_List = list()
        for i in range (len(sorted_dataframe)):           
            newCSR_List.append(int(sorted_dataframe.index.values[i]))  
  ## 隨機再生出五個CRS_list提供挑選，交換最不重要的幾個人的順序            
        if(which_way == "a"):
            order_a = newCSR_List.copy()
            return (order_a)
        elif (which_way == "b"):
            order_b = newCSR_List.copy()
            order_b[0],order_b[2] = order_b[2], order_b[0]
            return (order_b)
        elif (which_way == "c"):
            order_c = newCSR_List.copy()
            order_c[1],order_c[2] = order_c[2], order_c[1]
            return (order_c)
        elif (which_way == "d"):
            order_d = newCSR_List.copy()
            order_d[0],order_d[1] = order_d[1],order_d[0]
            return (order_d)
        elif (which_way == "e"):
            order_e = newCSR_List.copy()
            order_e[0],order_e[1] = order_e[1],order_e[0]
            order_e[0],order_e[2] = order_e[2],order_e[0]
            return (order_e)            
        return (newCSR_List)


"""
  ## 以可排晚班次數為優先  
    if (what_order == "upper"):
        nEMPLOYEE = EMPLOYEE_t.shape[0]
        available_CSR = len(CSR_List)
  ## 只選CSR的名字以及想排順序的條件兩欄
        temp_dataframe = EMPLOYEE_t.iloc[:,[0,9]]
  ## 把這次要排優先的CSR從原本的EMPLOYEE_t中抽出來，再來排優先      
        index = range(0,1)
        small_dataframe = pd.DataFrame(index=index,columns=['night_perWeek','Senior'])

        for i in range (nEMPLOYEE) :            
            for j in range (available_CSR):                
                if (CSR_List[j] == int(temp_dataframe.index.values[i])): 
                    small_dataframe = pd.concat([temp_dataframe.iloc[[i],:],small_dataframe],sort = False)
            #print (small_dataframe)
  ## small_dataframe中會包含這次用到的csr資料，並且把沒用到的row刪除
        small_dataframe = small_dataframe.dropna(thresh=2)
        sorted_dataframe = small_dataframe.sort_values('night_perWeek',ascending = True)
  ## 創立一個新的list來代表本次的優先順序
        newCSR_List = list()
        for i in range (len(sorted_dataframe)):           
            newCSR_List.append(int(sorted_dataframe.index.values[i]))   
  ## 隨機再生出五個CRS_list提供挑選，交換最不重要的幾個人的順序
        if(which_way == "a"):
            order_a = newCSR_List.copy()
            return (order_a)
        elif (which_way == "b"):
            order_b = newCSR_List.copy()
            order_b[0],order_b[2] = order_b[2], order_b[0]
            return (order_b)
        elif (which_way == "c"):
            order_c = newCSR_List.copy()
            order_c[1],order_c[2] = order_c[2], order_c[1]
            return (order_c)
        elif (which_way == "d"):
            order_d = newCSR_List.copy()
            order_d[0],order_d[1] = order_d[1],order_d[0]
            return (order_d)
        elif (which_way == "e"):
            order_e = newCSR_List.copy()
            order_e[0],order_e[1] = order_e[1],order_e[0]
            order_e[0],order_e[2] = order_e[2],order_e[0]
            return (order_e)
        return(newCSR_List)
        """