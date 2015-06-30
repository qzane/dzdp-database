# 2015年春季学期 数据库 PJ2：MYSQL查询优化

###13307130226 张谦 13级计算机科学与技术
###13307130364 茌海 13级信息安全

# 亮点
* 使用python对原始数据进行了必要的分析，尤其是把city、tags、navigation、groupon等不符合第一范式的数据进行了提取和拆分

* characteristics字段中提及了：```停车、外送、下午茶、夜宵、早餐、24小时```也按照含义修改为5个字段

* 为了模拟硬件不充分的条件、体现优化效果，更改了MySQL的默认参数:

>key buffer 16M 改 16K
>
>query cache limit 1M改1K
>
>query cache size 16M改1K




# 对数据的初步分析
使用notepad++打开文件，发现编码为UTF-8格式，似乎是使用类似CSV的方法，用\n作为行结束标志，用，作为字段分割，于是创建名为new.csv的副本，用excel打开，发现基本没有问题，第一行为字段名，其余行为字段内容。但是仔细观察以后发现一些行出现了问题，比如第44行“旺角站车仔面”的数据中，周一~周六被识别为了多行，观察源文件以后发现这部分内容是在"引号内的，所以应该是使用类似json的格式，用引号限定一个字段。另外注意到数据中很多内容是错误的，比如营业时间中有填手机号的，有使用中文描述的，鉴于这些问题，决定使用Python对数据进行初步的清理和挖掘。

# 使用Python对数据进行清理和挖掘

### 读取数据
注意到文件是UTF-8编码的
```python
f = open('new.csv','r',encoding='utf-8')
```
获取字段名
```python
keys = f.readline().split(',')
```
构造自动机对每个字段内的数据进行解析
```python
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
```

### 清理数据
使用numpy可以用类似于Matlab中的方法处理矩阵，可以方便的观察每一列的内容。
```python
import numpy as np
dd = np.array(data)
dd[:,1] #查看所有shop_id
```
使用dd[:,X]的方法逐列分析数据，得到下列有用信息：

>0. 检查读入数据，没有异常
>1. 查重、查空、确定主键：shop_id,name,alias
>2. 对province,city,city_i进行统计
>3. 记录address，对address,business_area进行统计
>4. phone:(None,13xxxxxxxxx,区号-座机号,座机号)
>5. huors:(XX:XX----XX:XX,周X,每天,节假日,X点XX-X点XX,中午,晚上,凌晨,AM,PM,至)
>6. avg_price:对价格进行统计
>7. stars:5分制，进行统计
>8. tags:逗号分隔标签
>9. original_latitude,original_longitude:判断范围
>10. navigation:级别，类似tag，重点处理!!!
>11. characteristics:停车、外送、下午茶、夜宵、早餐、24小时
>12. product_rating,environment_rating,service_rating:10分制，有空缺，与stars对比
>13. remarks...
>14. recommended_dishes:逗号分隔，可用于建表
>15. is_chains:0/1
>16. groupon:套餐，分号分隔
>17. card:会员优惠,每家店只有一种


### 确定实体
0. shop
1. province
2. city,city_i
3. tags
4. navigation
5. recommended_dishes
6. groupon
7. card

### 确定关系
province <--(1,n)--> city,city_i <br>
shop <--(n,1)-->city_i<br>
shop <--(n,n)--> tags<br>
navigation --(1,n)--> navigation<br>
shop <--(1,n)--> recommended_dishes<br>
shop <--(1,n)--> groupon<br>
shop <--(1,1)--> card<br>

### 建表
#######**加粗**代表主键，*斜体*代表外键

shop(**shop_id**,name,alias,*city_i*,area,address,business_area,phone,hours,avg_price,stars,photos,
description,original_latitude,original_longitude,product_rating,environment_rating,service_rating,
very_good_remarks,good_remarks,common_remarks,bad_remarks,very_bad_remarks,is_chains,*last_navigation*,
parking,delivery,breakfast,tea,night)#最后几项为原表中characteristics的内容拆分而来

province(**province**)

city(**city\_id**,city,*province*)

tags(**tag**)

shoptags(__shop\_id__,**tag**)

navigation(**navigation**,*pre\_navigation*,str) #str中列出前面的信息，加快读取

recommended\_dishes(**dish**,__shop\_id__)

groupon(**groupon**,__shop\_id__)

card(**card**,__shop\_id__)

### 载入数据
![p0](https://raw.githubusercontent.com/qzane/gitpic/master/db.pj2.png)
数据库截图
使用Python将数据转换为csv格式，再导入数据库中
```python    
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
        res = list(j[:3]+tuple([j[5]])+j[6:15]+j[16:18]+j[20:28]
        +tuple([j[29]])+tuple([navi])+(park,deli,brea,tea,nigh))
        
        shop[int(i[0])]=res
        
    f = open('shop.csv','w',encoding='utf-8')
    f.write('''
    shop_id,name,alias,city_i,area,address,business_area,\
    phone,hours,avg_price,stars,photos,description,original_latitude,\
    original_longitude,product_rating,environment_rating,service_rating,\
    very_good_remarks,good_remarks,common_remarks,bad_remarks,very_bad_remarks,\
    is_chains,last_navigation,parking,delivery,breakfast,tea,night\n''')
    for i in shop:
        tmp = shop[i]
        f.write(tmp[0])
        for j in tmp[1:]:
            f.write(',%s'%j)
        f.write('\n')
    f.close()
```
载入好的数据库备份见"附录A.sql"



# 查询&查询优化

* 查询所有店铺信息,包括城市、省份
```sql
SELECT * FROM `shop` join city join province 
where shop.city_i=city.city_i 
and city.province_id=province.province_id
```
```查询花费 0.0011 秒```

为查询中所有使用的主键和外键都加入索引以后执行查询：```查询花费 0.0007 秒```


* 查询所有店名与该店铺的推荐菜数目,并根据数目从大到小排列
```sql
SELECT shop.name,count(recommended_dishes.shop_id) 
as recommended_dishes 
from shop join recommended_dishes 
where shop.shop_id=recommended_dishes.shop_id 
GROUP BY shop.name 
order by recommended_dishes DESC
```
```查询花费 0.0168 秒```

为查询中所有使用的主键和外键都加入索引以后执行查询：```查询花费 0.0114 秒```

* 查询并统计不同省份的餐厅总数
```sql
SELECT province.province,count(shop.shop_id) as cc 
from province join city on(province.province_id=city.province_id)
join shop on (city.city_i = shop.city_i) 
group by province.province_id 
order by cc
```
```查询花费 0.0117 秒```

为查询中所有使用的主键和外键都加入索引以后执行查询：``查询花费 0.0006 秒```

# 总结：
在硬件不充裕的情况下加入索引的确可以改善查询速度，但是数据库内部本身的一些优化手段，比如缓存的使用已经使这种差距不太明显了。在数据集不是很大的时候，现代数据库的默认配置已经可以满足个人使用时大部分的要求了。



