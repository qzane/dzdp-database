# 对数据的初步分析
使用notepad++打开文件，发现编码为UTF-8格式，似乎是使用类似CSV的方法，用\n作为行结束标志，用，作为字段分割，于是创建名为new.csv的副本，用excel打开，发现基本没有问题，第一行为字段名，其余行为字段内容。但是仔细观察以后发现一些行出现了问题，比如第44行“旺角站车仔面”的数据中，周一~周六被识别为了多行，观察源文件以后发现这部分内容是在"引号内的，所以应该是使用类似json的格式，用引号限定一个字段。另外注意到数据中很多内容是错误的，比如营业时间中有填手机号的，有使用中文描述的，鉴于这些问题，决定使用Python对数据进行初步的清理和挖掘。

# 使用Python对数据进行清理和挖掘

### 读取数据
注意到文件是UTF-8编码的
```
f = open('new.csv','r',encoding='utf-8')
```
获取字段名
```
keys = f.readline().split(',')
```
构造自动机对每个字段内的数据进行解析
``` python
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
```
import numpy as np
dd = np.array(data)
```
使用dd[:,X]的方法逐列分析数据，得到下列有用信息：

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
>11. characteristics:停车、外送、下午茶
>12. product_rating,environment_rating,service_rating:10分制，有空缺，与stars对比
>13. remarks...
>14. recommended_dishes:逗号分隔，可用于建表
>15. is_chains:0/1
>16. groupon:套餐，分号分隔
>17. card:会员优惠

### 确定函数依赖
shop_id -> all
city_id -> city -> province
phone -> all

### 确定实体
1. province
2. city,city_i
3. tags
4. navigation
5. groupon
6. card

### 确定关系


