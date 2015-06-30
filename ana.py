# -*- coding: utf-8 -*-

import re
import numpy as np

def getdata(string):
    data = []
    begin = -1
    for i,j in enumerate(string):
        if j == '"':
            if begin == -1:
                begin = i
            else:
                data.append(string[begin+1:i])
                begin = -1
    return data

def readData(fname='new.csv'):
    f = open(fname,'r',encoding='utf-8')
    keys = f.readline().split(',')
    data = []
    while(1):
        tmp = f.readline()
        if tmp == '':
            break
        data.append(getdata(tmp))
    return(keys,data)