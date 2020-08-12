import shapely.wkt
from shapely.geometry import MultiPolygon
import requests
import json
import pandas as pd
import numpy as np
import psycopg2

df = pd.read_excel("E:/gisdata/AMap_adcode_citycode.xlsx", usecols=[2])

city_code = np.array(df['citycode']).tolist()
citycode = []
for i in city_code:
    if np.isnan(i):
        continue
    else:
        citycode.append(str(int(i)))

citycode = list(set(citycode))

res_citycode = []
for i in citycode:
    if (len(i) == 2)|(len(i) == 3):
        p = '0'+ i
        res_citycode.append(p)
    else:
        res_citycode.append(p)

print(res_citycode)
conn = psycopg2.connect(host='localhost', database='test1', user='postgres', password='981014', port='5432')
cursor = conn.cursor()

for i in res_citycode:
    params = {
        "key": "dcb6328695c9c518d9184e69a7f294c1",
        "keywords": "{}".format(i),
        "extensions": "all"
    }
    ret = requests.get("https://restapi.amap.com/v3/config/district?", params=params)
    data = json.loads(ret.text)
    # 字符串转换成字典
    try:
        polyline = data["districts"][0]["polyline"]
        citycode = data["districts"][0]["citycode"]
        name = data["districts"][0]["name"]

        multi = []
        for i in polyline.split('|'):
            x = ','.join([' '.join(i.split(',')) for i in i.split(';')])
            a = shapely.wkt.loads('POLYGON (({}))'.format(x))
            multi.append(a)
        #print(MultiPolygon(multi))
        ins_sql = """insert into testgeo values(null, '{}','{}', st_geomfromtext('{}'))""".format(name,citycode,MultiPolygon(multi))
        cursor.execute(ins_sql)
        conn.commit()
    except:
        print('error')

cursor.close()
conn.close()