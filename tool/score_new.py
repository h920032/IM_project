import numpy as np
import pandas as pd
import os, sys
import tool.tool as tl
import datetime, calendar
import subprocess


def score(df_x,main):
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
    #f = subprocess.Popen(main,shell=True, stdout=subprocess.PIPE).communicate()
    #print(f)
    data = f.readlines()
    f.close()
    #os.system(main)
    #print(data)
    return float(data[0])
