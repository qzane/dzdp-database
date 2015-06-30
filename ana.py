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
    
def make_province(dd):
    p = set()
    for i in dd[:,3]:
        p.add(i)
    f = open('province.csv','w',encoding='utf-8')
    f.write('province\n')
    for i in p:
        f.write("%s\n"%i)
    f.close()
    
def make_city(dd):
    city = set()
    for i in dd[:,[5,4,3]]:
        city.add(tuple(i))
    f = open('city.csv','w',encoding='utf-8')
    f.write('city_i,city,province\n')
    for i in city:
        f.write("%s,%s,%s\n"%(i[0],i[1],i[2]))
    f.close()
    
def make_tags(dd):
    tags = set()
    for i in dd[:,15]:
        tmp = i.split(',')
        for j in tmp:
            tags.add(j)
    f = open('tags.csv','w',encoding='utf-8')
    f.write('tags\n')
    for i in tags:
        f.write("%s\n"%i)
    f.close()
def make_shopTags(dd):
    st = set()
    for i in dd[:,[0,15]]:
        tmp = i[1].split(',')
        for j in tmp:
            st.add((i[0],j))
    f = open('shopTags.csv','w',encoding='utf-8')
    f.write('shop_id,tag\n')
    for i in st:
        f.write("%s,%s\n"%(i[0],i[1]))
    f.close()
    
def make_recommended_dishes(dd):
    dish = set()
    for i in dd[:,[0,28]]:
        tmp = i[1].split(',')
        for j in tmp:
            dish.add((i[0],j))
    f = open('recommended_dishes.csv','w',encoding='utf-8')
    f.write('shop_id,dish\n')
    for i in dish:
        f.write("%s,%s\n"%(i[0],i[1]))
    f.close()
    
def make_groupon(dd):
    group = set()
    for i in dd[:,[0,30]]:
        tmp = i[1].split(';')
        for j in tmp:
            if j != '':
                group.add((i[0],j))
    f = open('groupon.csv','w',encoding='utf-8')
    f.write('shop_id,groupon\n')
    for i in group:
        f.write("%s,%s\n"%(i[0],i[1]))
    f.close()
    
def make_card(dd):
    card = set()
    for i in dd[:,[0,31]]:
        if i[1] != '':
            card.add((i[0],i[1]))
    f = open('card.csv','w',encoding='utf-8')
    f.write('shop_id,card\n')
    for i in card:
        f.write("%s,%s\n"%(i[0],i[1]))
    f.close()
    
def make_navigation(dd):
    na = {}
    for i in dd[:,18]:
        s = ''
        p = ''
        data = i.split('>>')
        for j in data:
            s = "%s>>%s"%(s,j)
            na[j]=(j,p,s)
            p = j
    f = open('navigation.csv','w',encoding='utf-8')
    f.write('navigation,pre_navigation,str\n')
    for i in na:
        f.write("%s,%s,%s\n"%(na[i][0],na[i][1],na[i][2]))
    f.close()
    
def make_shop(dd):
    shop = {}
    for i in dd:
        j = tuple(i)
        navi = j[18].split('>>')[-1]
        char = j[19]
        if '外送' in char:
            deli = 1
        else:
            deli = 0
        if '停车' in char:
            park = 1
        else:
            park = 0
        if '早' in char or '24' in char:
            brea = 1
        else:
            brea = 0
        if '茶' in char or '24' in char:
            tea = 1
        else:
            tea = 0
        if '夜' in char or '24' in char:
            nigh = 1
        else:
            nigh = 0                
        res = list(j[:3]+tuple([j[5]])+j[6:15]+j[16:18]+j[20:28]+tuple([j[29]])+tuple([navi])+(park,deli,brea,tea,nigh))
        
        shop[int(i[0])]=res
        
    f = open('shop.csv','w',encoding='utf-8')
    f.write('shop_id,name,alias,city_i,area,address,business_area,phone,hours,avg_price,stars,photos,description,original_latitude,original_longitude,product_rating,environment_rating,service_rating,very_good_remarks,good_remarks,common_remarks,bad_remarks,very_bad_remarks,is_chains,last_navigation,parking,delivery,breakfast,tea,night\n')
    for i in shop:
        tmp = shop[i]
        f.write(tmp[0])
        for j in tmp[1:]:
            f.write(',%s'%j)
        f.write('\n')
    f.close()
        
        
        
        
        
        
        
        
        
        
        