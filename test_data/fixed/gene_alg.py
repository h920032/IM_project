import numpy as np
import pandas as pd
import random
from data.fixed.score import score

K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
K_type_dict = {0:'O',1:'A2',2:'A3',3:'A4',4:'A5',5:'MS',6:'AS',7:'P2',8:'P3',9:'P4',10:'P5',11:'N1',12:'M1',13:'W6',14:'CD',15:'C2',16:'C3',17:'C4',18:'OB'}

#def score(input):
#    return random.randint(1,10000)

def alg(score_liz, nDAY,nW, nEMPLOYEE,year,month,per_month_dir='./data/per_month/',AssignTest='',NeedTest='',EmployeeTest=''):
    sort = sorted(score_liz, key = lambda s: s[2],reverse = True)
    for i in range(len(score_liz)):
        print('\n\n   alg() #### i =',i,'#### range =',len(score_liz))
        for j in range(len(score_liz)):
            if i != j:
                print(j, end=' ')
                union = np.logical_or(score_liz[i][1], score_liz[j][1])
                one_not_avb = union * score_liz[i][0]
                one_avb = score_liz[i][0] - one_not_avb
                two_not_avb = union * score_liz[j][0]
                two_avb = score_liz[j][0] - two_not_avb
                #隨機決定切分點
                sp_row = random.randint(0,nDAY-1)
                sp_col = random.randint(0,nEMPLOYEE-1)
                #第一組：依據員工、日期切分
                one_col_left = one_avb[:sp_col]
                one_col_right = one_avb[sp_col:]
                one_row_up = one_avb.T[:sp_row].T
                one_row_down = one_avb.T[sp_row:].T
                #第二組：的切分
                two_col_left = two_avb[:sp_col]
                two_col_right = two_avb[sp_col:]
                two_row_up = two_avb.T[:sp_row].T
                two_row_down = two_avb.T[sp_row:].T
                #將對應的一、二組片段重新組合
                a_one_one_two = np.concatenate((one_row_up, two_row_down), axis=1) + one_not_avb
                a_two_one_two = np.concatenate((one_row_up, two_row_down), axis=1) + two_not_avb
                a_one_two_one = np.concatenate((two_row_up, one_row_down), axis=1) + one_not_avb
                a_two_two_one = np.concatenate((two_row_up, one_row_down), axis=1) + two_not_avb
                b_one_one_two = np.concatenate((one_col_left, two_col_right), axis=0) + one_not_avb
                b_two_one_two = np.concatenate((one_col_left, two_col_right), axis=0) + two_not_avb
                b_one_two_one = np.concatenate((two_col_left, one_col_right), axis=0) + one_not_avb
                b_two_two_one = np.concatenate((two_col_left, one_col_right), axis=0) + two_not_avb
                sort.append((a_one_one_two,score_liz[i][1],score(a_one_one_two.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((a_two_one_two,score_liz[j][1],score(a_two_one_two.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((a_one_two_one,score_liz[i][1],score(a_one_two_one.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((a_two_two_one,score_liz[j][1],score(a_two_two_one.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((b_one_one_two,score_liz[i][1],score(b_one_one_two.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((b_two_one_two,score_liz[j][1],score(b_two_one_two.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((b_one_two_one,score_liz[i][1],score(b_one_two_one.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
                sort.append((b_two_two_one,score_liz[j][1],score(b_two_two_one.tolist(),nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
    # sort = sorted(sort, key = lambda s: s[2],reverse = True)
    sort = sorted(sort, key = lambda s: s[2])
    sort = sort[:100]
    return sort

def gene_alg(avaliable_sol, fix, nDAY,nW, nEMPLOYEE, gen,year,month,per_month_dir='./data/per_month/',AssignTest='',NeedTest='',EmployeeTest=''): #avaliavle_sol 可行解列表 fix 不能移動的列表
    i_nb = []
    
    for p in range(len(avaliable_sol)):
        #i_nb.append(np.vectorize({v: k for k, v in K_type_dict.items()}.get)(np.array(avaliable_sol[p])).tolist())
        i_nb.append(avaliable_sol[p])
        
    score_liz = []
    for i ,j in zip(i_nb,fix):
        score_liz.append((i,j, score(i,nDAY,nW,year=year,month=month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)))
    # for i in range(gen):    #重複親代數量那麼多次
    #     score_liz = alg(score_liz, nDAY,nW, nEMPLOYEE,year,month)
    score_liz = alg(score_liz, nDAY,nW, nEMPLOYEE,year,month,per_month_dir=per_month_dir,AssignTest=AssignTest,NeedTest=NeedTest,EmployeeTest=EmployeeTest)
    #上面是為求跑得完而做的修改
    result = np.vectorize(K_type_dict.get)(score_liz[0][0])
    print('\n\n基因演算法最佳解：',score_liz[0][2])
    return result
