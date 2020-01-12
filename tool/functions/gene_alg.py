import time
import numpy as np
import pandas as pd
import random
import tool.tool as tl
from tool.score import score
from tool.CONFIRM import confirm

#1.永遠只拿前幾名，抽兩個來交配
#2.用更好的子代取代親代
#3.加入突變（新班表必然突變掉隨機一個班，若成不可行解就一百萬）
#4.在gene中要做confirm，可能可能不用


#K_type = ['O','A2','A3','A4','A5','MS','AS','P2','P3','P4','P5','N1','M1','W6','CD','C2','C3','C4','OB']
#K_type_dict = {0:'O',1:'A2',2:'A3',3:'A4',4:'A5',5:'MS',6:'AS',7:'P2',8:'P3',9:'P4',10:'P5',11:'N1',12:'M1',13:'W6',14:'CD',15:'C2',16:'C3',17:'C4',18:'OB'}

#def score(input):
#    return random.randint(1,10000)

def alg(score_liz):

    nDAY      = tl.nD
    nEMPLOYEE = tl.nE
    sort = sorted(score_liz, key = lambda s: s[2]) #親代排名
    new = np.copy(sort[:int(len(score_liz)/3)]) #取出前1/3
    num_list = list(range(len(new)))
    random.shuffle(num_list)
    #print(num_list[0],num_list[1], end=' ')

    union = np.logical_or(new[num_list[0]][1], new[num_list[1]][1])
    one_not_avb = union * new[num_list[0]][0]
    one_avb = new[num_list[0]][0] - one_not_avb
    two_not_avb = union * new[num_list[1]][0]
    two_avb = new[num_list[1]][0] - two_not_avb
    one_org = np.array(new[num_list[0]][0]) #沒有fix的班表
    two_org = np.array(new[num_list[1]][0])

    #隨機決定切分點
    sp_row = random.randint(0,nDAY-1)
    sp_col = random.randint(0,nEMPLOYEE-1)

    #第一組：依據員工、日期切分
    one_col_left = one_avb[:sp_col]
    one_col_right = one_avb[sp_col:]
    one_row_up = one_avb.T[:sp_row].T
    one_row_down = one_avb.T[sp_row:].T
    one_org_col_left = one_org[:sp_col]
    one_org_col_right = one_org[sp_col:]
    one_org_row_up = one_org.T[:sp_row].T
    one_org_row_down = one_org.T[sp_row:].T

    #第二組：的切分
    two_col_left = two_avb[:sp_col]
    two_col_right = two_avb[sp_col:]
    two_row_up = two_avb.T[:sp_row].T
    two_row_down = two_avb.T[sp_row:].T
    two_org_col_left = two_org[:sp_col]
    two_org_col_right = two_org[sp_col:]
    two_org_row_up = two_org.T[:sp_row].T
    two_org_row_down = two_org.T[sp_row:].T
    
    #將對應的一、二組片段重新組合
    #上下黏合
    a_one_one_two = np.concatenate((one_row_up, two_row_down), axis=1) + one_not_avb
    a_two_one_two = np.concatenate((one_row_up, two_row_down), axis=1) + two_not_avb
    a_one_two_one = np.concatenate((two_row_up, one_row_down), axis=1) + one_not_avb
    a_two_two_one = np.concatenate((two_row_up, one_row_down), axis=1) + two_not_avb
    a_org_one_two = np.concatenate((one_org_row_up, two_org_row_down), axis=1)
    a_org_two_one = np.concatenate((two_org_row_up, one_org_row_down), axis=1)

    #左右黏合
    b_one_one_two = np.concatenate((one_col_left, two_col_right), axis=0) + one_not_avb
    b_two_one_two = np.concatenate((one_col_left, two_col_right), axis=0) + two_not_avb
    b_one_two_one = np.concatenate((two_col_left, one_col_right), axis=0) + one_not_avb
    b_two_two_one = np.concatenate((two_col_left, one_col_right), axis=0) + two_not_avb
    b_org_one_two = np.concatenate((one_org_col_left, two_org_col_right), axis=0)
    b_org_two_one = np.concatenate((two_org_col_left, one_org_col_right), axis=0)


    #突變
    if random.randint(0,19) == 0:
        a_one_one_two[random.randint(0,a_one_one_two.shape[0]-1)][random.randint(0,a_one_one_two.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        a_two_one_two[random.randint(0,a_two_one_two.shape[0]-1)][random.randint(0,a_two_one_two.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        a_one_two_one[random.randint(0,a_one_two_one.shape[0]-1)][random.randint(0,a_one_two_one.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        a_two_two_one[random.randint(0,a_two_two_one.shape[0]-1)][random.randint(0,a_two_two_one.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        a_org_one_two[random.randint(0,a_org_one_two.shape[0]-1)][random.randint(0,a_org_one_two.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        a_org_two_one[random.randint(0,a_org_two_one.shape[0]-1)][random.randint(0,a_org_two_one.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        b_one_one_two[random.randint(0,b_one_one_two.shape[0]-1)][random.randint(0,b_one_one_two.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        b_two_one_two[random.randint(0,b_two_one_two.shape[0]-1)][random.randint(0,b_two_one_two.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        b_one_two_one[random.randint(0,b_one_two_one.shape[0]-1)][random.randint(0,b_one_two_one.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        b_two_two_one[random.randint(0,b_two_two_one.shape[0]-1)][random.randint(0,b_two_two_one.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        b_org_one_two[random.randint(0,b_org_one_two.shape[0]-1)][random.randint(0,b_org_one_two.shape[1]-1)] = random.randint(0,18)
    if random.randint(0,19) == 0:
        b_org_two_one[random.randint(0,b_org_two_one.shape[0]-1)][random.randint(0,b_org_two_one.shape[1]-1)] = random.randint(0,18)
    
    #print(np.zeros(a_org_one_two.shape))
    #判斷是否符合
    if confirm(a_one_one_two) == 'All constraints are met.':
        sort.append((a_one_one_two,new[num_list[0]][1],score(a_one_one_two.tolist())))
       
    if confirm(a_two_one_two) == 'All constraints are met.':
        sort.append((a_two_one_two,new[num_list[1]][1],score(a_two_one_two.tolist())))
    
    if confirm(a_one_two_one) == 'All constraints are met.':
        sort.append((a_one_two_one,new[num_list[0]][1],score(a_one_two_one.tolist())))
    
    if confirm(a_two_two_one) == 'All constraints are met.':
        sort.append((a_two_two_one,new[num_list[1]][1],score(a_two_two_one.tolist())))
    
    if confirm(a_org_one_two) == 'All constraints are met.':
        sort.append((a_org_one_two,np.zeros(a_org_one_two.shape),score(a_org_one_two.tolist())))
    
    if confirm(a_org_two_one) == 'All constraints are met.':
        sort.append((a_org_two_one,np.zeros(a_org_two_one.shape),score(a_org_two_one.tolist())))
    
    if confirm(b_one_one_two) == 'All constraints are met.':
        sort.append((b_one_one_two,new[num_list[0]][1],score(b_one_one_two.tolist())))
    
    if confirm(b_two_one_two) == 'All constraints are met.':
        sort.append((b_two_one_two,new[num_list[1]][1],score(b_two_one_two.tolist())))
    
    if confirm(b_one_two_one) == 'All constraints are met.':
        sort.append((b_one_two_one,new[num_list[0]][1],score(b_one_two_one.tolist())))
    
    if confirm(b_two_two_one) == 'All constraints are met.':
        sort.append((b_two_two_one,new[num_list[1]][1],score(b_two_two_one.tolist())))

    if confirm(b_org_one_two) == 'All constraints are met.':
        sort.append((b_org_one_two,np.zeros(b_org_one_two.shape),score(b_org_one_two.tolist())))

    if confirm(b_org_two_one) == 'All constraints are met.':
        sort.append((b_org_two_one,np.zeros(b_org_two_one.shape),score(b_org_two_one.tolist())))
             
    # sort = sorted(sort, key = lambda s: s[2],reverse = True)
    sort = sorted(sort, key = lambda s: s[2])
    #print(len(sort))
    sort = sort[:len(score_liz)]
    #print(sort)
    #print(len(sort))
    return sort

def gene_alg(K_type_dict, timelimit,avaliable_sol,fix,gen,per_month_dir='./data/per_month/'): #avaliavle_sol 可行解列表 fix 不能移動的列表
    print('per_month_dir =',per_month_dir)
    i_nb = []
    tStart = time.time()    #紀錄演算法開始的時間
    for p in range(len(avaliable_sol)):
        #i_nb.append(np.vectorize({v: k for k, v in K_type_dict.items()}.get)(np.array(avaliable_sol[p])).tolist())
        i_nb.append(avaliable_sol[p])
        
    score_liz = []
    gene_log = []   
    for i ,j in zip(i_nb,fix):
        score_liz.append((i,j, score(i)))
    
    for i in range(gen):    #重複指定的次數
        if time.time() - tStart > timelimit:    #如果時間已到，就跳出
            print('限制時間已至，於第',i,'世代跳出')
            break
        score_liz = alg(score_liz)
        print('第',i+1,'世代最佳分數：',score_liz[0][2], ' Time: ', int(time.time() - tStart),'s')
        gene_log.append([i+1,score_liz[0][2]])
    gene_log = pd.DataFrame(np.array(gene_log))
    gene_log.to_csv('gene_log.csv')
    result = np.vectorize(K_type_dict.get)(score_liz[0][0])
    print('\n\n基因演算法最佳解：',score_liz[0][2])
    return result
