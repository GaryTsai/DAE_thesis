from flask import jsonify, request
from . import api
import datetime
import json
from sqlalchemy import func, and_, or_, between, exists
# from .. import db
# from ..models import *
from selenium import webdriver
# urllib可以存取網頁、下載資料、剖析資料、修改表頭(header)、執行GET與POST的請求…。
from urllib.request import urlopen
from bs4 import BeautifulSoup


@api.route('/week_power_storage', methods=['GET'])
def week_power_storage():
    html = urlopen("http://data.taipower.com.tw/opendata/apply/file/d006007/%E5%8F%B0%E7%81%A3%E9%9B%BB%E5%8A%9B%E5%85%AC%E5%8F%B8_%E6%9C%AA%E4%BE%86%E4%B8%80%E9%80%B1%E9%9B%BB%E5%8A%9B%E4%BE%9B%E9%9C%80%E9%A0%90%E6%B8%AC.txt").read()
    #urlopen 獲取頁面
    print("urlopen(url).read()結果 html-->")
    print()
    print(html)
    #xml、lxml
    result = BeautifulSoup(html, 'html5lib')
    #BeautifulSoup選擇解析器
    print('BeautifulSoup html5lib結果')
    print()
    print(result)
    #取得html底下的文本並用\n分割
    print('result.body結果')
    print()
    print(result.body)
    print('result.body.get_text()結果')
    print()
    print(result.body.get_text())
    print(r'soup = result.body.get_text().split(\n)結果')
    print()
    soup = result.body.get_text().split('\n')
    print(soup)
    rawdata = []
    data = []
    # print('string')
    # print(int('123'))
    for i in range(0, 7):
        rawdata.append(soup[i])
        print('rawdata')
        print(rawdata)
        r = rawdata[i].split(',')
        print('r')
        # print(int('abc'))
        print(int('123456'))
        cook = {"date": r[0],
                #尖峰負載(萬瓩)
                "systemNetPeakLoad(MW)": int(r[1]) / 10,
                #尖峰供電能力(萬瓩)
                "systemPeakLoad(MW)": int(r[2]) / 10,
                # (淨尖峰供電能力(萬瓩)-尖峰負載(萬瓩))/10 = 備轉容量(萬瓩)
                "operatingReserve(MW)": round((int(r[1]) - int(r[2])) / 10, 2),
                #備轉容量燈號比率
                "operatingReservePercent(%)": round((int(r[1]) - int(r[2])) / int(r[2]) * 100, 2)
                }
        data.append(cook)
    print(data)

    # driver = webdriver.PhantomJS(
    #     executable_path=r'C:\Program Files\phantomjs-2.1.1-windows\bin\phantomjs.exe')  # 加r將\視為字串
    # driver.get(
    #     'http://stpc00601.taipower.com.tw/loadGraph/loadGraph/load_briefing.html')
    # pageSource = driver.page_source

    # bsToday = BeautifulSoup(pageSource, 'html5lib')
    # # print('bsToday')
    # # print(bsToday)
    # zeit = bsToday.body.find_all('div')[1].find_all(
    #     'div')[0].find_all('div')[0].find_all('span')
    # amount = bsToday.body.find_all('div')[4].div.find_all('table')
    # peakLoad = amount[1].tbody.tr.find_all('td')[0].find_all(
    #     'div')[1].span.get_text().strip().replace(',', '')
    # netLoad = amount[2].tbody.tr.find_all('td')[0].find_all(
    #     'div')[1].span.get_text().strip().replace(',', '')

    # ingredient = {"date": "",
    #               "systemNetPeakLoad(MW)": "",
    #               "systemPeakLoad(MW)": "",
    #               "operatingReserve(MW)": "",
    #               "operatingReservePercent(%)": "",
    #               "updateTime": zeit[1].get_text().strip()[0:5]
    #               }
    # data.append(ingredient)
    # print(data)
    # ingredient["date"] = zeit[0].get_text().strip().split(
    #     '(')[0].replace('.', '/').replace('106', '2017')
    # ingredient["systemNetPeakLoad(MW)"] = netLoad
    # ingredient["systemPeakLoad(MW)"] = peakLoad
    # ingredient["operatingReserve(MW)"] = round(
    #     float(netLoad) - float(peakLoad), 2)
    # ingredient["operatingReservePercent(%)"] = round(
    #     (float(netLoad) - float(peakLoad)) / float(netLoad) * 100, 3)
    # ingredient["updateTime"] = zeit[1].get_text().strip()[0:5]

    return jsonify(data)
