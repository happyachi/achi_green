from django.shortcuts import render
import json, requests
from urllib import request as re

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

from main import  time_srt_to_int

# Create your views here.
def index(request):
    return render(request, 'index.html', locals())


def math(request):
    light_list = {
        "燈具":{
            "省電燈泡":{"name":"省電燈泡-23W","value":23},
            "Led燈泡":{"name":"Led燈泡-13W","value":13},
            
        },
        "燈管":{
            "T8四尺燈管":{"name":"T8四尺燈管-36W","value":36},
            "T8四尺Led燈管":{"name":"T8四尺Led燈管-18W","value":18},
        },

    }
    data_json = json.dumps(light_list)

    return render(request, 'math.html', {'data_json': data_json} )


def temperature_now(request):
    """透過氣象局API，讀取資料"""
    # 從氣象局要"溫度分布-小時溫度觀測分析格點資料"
    dataid = "O-A0038-003"
    apikey = "CWB-3B17CB00-19B8-49CC-8166-C4B528D2039D" 
    format = "JSON"
    api_url = "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/"+ dataid + "?Authorization=" + apikey + "&format=" + format
    json_data = re.urlopen(api_url).read().decode("utf-8")  # 抓JSON資料回來
    data = json.loads(json_data)   #字串變字典
    date_time = data["cwbopendata"]["dataset"]["datasetInfo"]["parameterSet"]["parameter"][2]["parameterValue"]    # 資料時間
    contents = data["cwbopendata"]["dataset"]["contents"]["content"]   # 溫度資料
    
    date_time_2 = time_srt_to_int.time_str_to_int_1(date_time)    # 整理時間資料
    
    # 分割溫度資料
    value = contents.split("\n")
    for i in range(len(value)):
        value[i]=value[i].split(",")
    value2 = value[::-1]    # 翻轉資料順序
    
    # 把溫度從str轉成int
    for i in range(len(value2)):
        for j in range(len(value2[i])):
            try:
                value2[i][j] = float(value2[i][j])
            except:
                value2[i][j]=None

    # 抓溫度圖片
    p_dataid = "O-A0038-001"
    p_api_url = "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/"+ p_dataid + "?Authorization=" + apikey + "&format=" + format
    p_json_data = re.urlopen(p_api_url).read().decode("utf-8")  # 抓JSON資料回來
    p_data = json.loads(p_json_data)   #字串變字典
    p_uri = p_data["cwbopendata"]["dataset"]["resource"]["uri"]    # uri

    return render(request, 'temperature.html', locals())


def reservoir_now(request):

    # 容量大於100的水庫清單
    reservoir_base_list =[
        ['10201', '石門水庫'],['10204', '新山水庫'],['10205', '翡翠水庫'],['10401', '寶山水庫'],['10405', '寶山第二水庫'],
        ['10501', '永和山水庫'],['10503', '大埔水庫'],['10601', '明德水庫'],['20101', '鯉魚潭水庫'],['20201', '德基水庫'],
        ['20202', '石岡壩'],['20501', '霧社水庫'],['20502', '日月潭水庫'],['20509', '湖山水庫'],['30301', '仁義潭水庫'],
        ['30302', '蘭潭水庫'],['30401', '白河水庫'],['30501', '烏山頭水庫'],['30502', '曾文水庫'],['30503','南化水庫'],
        ['30801', '澄清湖水庫'],['30802', '阿公店水庫'],['30803', '鳳山水庫'],['31201', '牡丹水庫'],['31301', '成功水庫'],
        ['50201',  '太湖水庫']
        ]

    # 取出及時水情
    api_url = "https://fhy.wra.gov.tw/Api/v2/Reservoir/Info/RealTime"
    print(api_url)
    json_data = re.urlopen(api_url).read().decode("utf-8")  #線上API
    json_data = json.loads(json_data)   #字串變字典
    list1 = list(json_data.values())
    list2 = []

    # 過濾出我們要的資訊(測站代碼,水情時間,有效容量(萬立方公尺),有效蓄水量（萬立方公尺）,蓄水百分比)
    v = (0,1,4,5,6)
    for i in range(len(list1[1])):
        l1 = list(list1[1][i].values())
        l2 = []
        for j in v:
            l2.append(l1[j])
        list2.append(l2)

    # 把指定水庫名加到清單後面
    k = len(list2)-1
    for i in range(len(list2)):
        for j in range(len(reservoir_base_list)):
            if list2[k-i][0] == reservoir_base_list[j][0]:
                list2[k-i].append(reservoir_base_list[j][1])
        try:
            list2[k-i][5]
        except:
            del list2[k-i]

    # 建立資料
    labels = []
    value = []
    for i in range(len(list2)):
        labels.append(list2[i][5])
        value.append(list2[i][4])

    fig = px.bar(x=labels,y=value,  color=labels,)
    fig = fig.to_json()

    return render(request, 'reservoir.html',locals() )


def energy_now(request):
    """抓取及時發電資料"""
    # API抓數據
    api_url = "https://data.taipower.com.tw/opendata/apply/file/d006001/001.json"
    json_data = re.urlopen(api_url).read().decode("utf-8")  #線上API
    json_data = json.loads(json_data)   #字串變字典
    list1 = list(json_data.values())
    time = list1[0]
    list2 = list(list1[1])
    for i in range(len(list2)):
        list2[i] = list(list2[i])
    # ['核能', '核三#1', '951.0', '944.9', '99.359%', ' ']
    for i in range(len(list2)):
        list2[i] = list(list2[i])

    labels = []
    values = []
    list3 = []

    num = (2,22,24,30,57,68,72,82,135,157,171,182,192,195)  # 各能源小計在的地方
    for i in num:
        labels.append(list2[i][0])  # 取出能源別
        list3.append(list2[i][3].split("("))    # 切割指定位置數值 ['燃煤', '小計', '11600.0(21.769%)', '10119.0(28.512%)', '', '']

    for i in range(len(list3)):
            values.append(list3[i][0])  # 切割完取出指定位置前方數值

    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=0.4,  # 设置中心的空白部分大小
        textinfo='label+percent',  # 标签显示方式
        # marker=dict(colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']),  # 设置颜色
        hoverinfo='label+percent+value',  # 鼠标悬停显示信息
        textfont=dict(size=14)  # 文本字体大小
        )])
    fig.update_layout(
        # autosize=True,
        # width=800,
        height = 600,
        margin=dict(l=20, r=20, t=20, b=20),  # 上下左右的边距大小
    )
    fig = fig.to_json()


    return render(request, 'energy.html',locals() )


def energy_history(request):
    # 開啟檔案，取出整點list
    json_data = re.urlopen("https://storage.googleapis.com/achi-green.appspot.com/jsons/final.json").read().decode("utf-8")  # 抓JSON資料回來
    list = json.loads(json_data)   # 字串變list

    # 轉為製圖用數據
    df =pd.read_json("https://storage.googleapis.com/achi-green.appspot.com/jsons/final.json")   # 透過pandas開啟
    fig_list = []
    for i in range(1, 11):  
        fig = go.Figure([go.Scatter(x=df[0], y=df[i])])
        b = [i, df[i][0]]
        fig_list.append([b, fig.to_json()])

    return render(request, 'energy_history.html',locals() )