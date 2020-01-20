import numpy as np
import pandas as pd
import os
import tool.tool as tl
import datetime, calendar

def score(df_x,main,fixed_dir = tl.DIR_PARA+'fixed/'):
    #30
    df_x_s = ""
    for i in df_x: # .values:
        for j in i:
            df_x_s += str(j)
            df_x_s += ","
        df_x_s += "!"

    main += df_x_s
    main += " "
    #print(main)
    # print(df_x_s)
    f = os.popen(main)
    #print(f)
    data = f.readlines()
    f.close()
    #os.system(main)
    #print(data)
    return int(data[0])
