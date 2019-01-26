# -*- coding:utf-8 -*-
import requests,threading,datetime
import requests
import matplotlib.dates as mdates
import pylab
import matplotlib.pyplot as plt
from datetime import datetime
import re
import time
import pandas as pd
import codecs
import jieba
import sys
from wordcloud import WordCloud
from scipy.misc import imread
from os import path
import os
import netcloud
import importlib
import xlsxwriter
from bs4 import BeautifulSoup
from urllib import request
import random

with open("netcloud.txt", "r") as f:
    comments_list=f.readlines()
    del comments_list[0]
    print(len(comments_list))

location_list=[]
user_list=[]
for comment in comments_list:
    comment_sep=comment.split(" ",5)
    user_list.append(comment_sep[0])
user_list = list(set(user_list))
print(len(user_list))

def write(path,text):
    with open(path,'a', encoding='utf-8') as f:
        f.writelines(text)
        f.write('\n')

def truncatefile(path):
    with open(path, 'w', encoding='utf-8') as f:
        f.truncate()

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        txt = []
        for s in f.readlines():
            txt.append(s.strip())
    return txt

def getheaders():
    user_agent_list = [ \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    UserAgent=random.choice(user_agent_list)
    headers = {'User-Agent': UserAgent}
    return headers

def checkip(targeturl,ip):
    headers =getheaders()  # 定制请求头
    proxies = {"http": "http://"+ip, "https": "http://"+ip}  # 代理ip
    try:
        response=requests.get(url=targeturl,proxies=proxies,headers=headers,timeout=5).status_code
        if response == 200 :
            return True
        else:
            return False
    except:
        return False

def findip(type,pagenum,targeturl,path): # ip类型,页码,目标url,存放ip的路径
    list={'1': 'http://www.xicidaili.com/nt/', # xicidaili国内普通代理
          '2': 'http://www.xicidaili.com/nn/', # xicidaili国内高匿代理
          '3': 'http://www.xicidaili.com/wn/', # xicidaili国内https代理
          '4': 'http://www.xicidaili.com/wt/'} # xicidaili国外http代理
    url=list[str(type)]+str(pagenum) # 配置url
    headers = getheaders() # 定制请求头
    html=requests.get(url=url,headers=headers,timeout = 5).text
    soup=BeautifulSoup(html,'lxml')
    all=soup.find_all('tr',class_='odd')
    for i in all:
        t=i.find_all('td')
        ip=t[1].text+':'+t[2].text
        is_avail = checkip(targeturl,ip)
        if is_avail == True:
            write(path=path,text=ip)
            print(ip)


def getip(targeturl, path):
    truncatefile(path)  # 爬取前清空文档
    threads = []
    for type in range(4):  # 四种类型ip,每种类型取前三页,共12条线程
        for pagenum in range(3):
            t = threading.Thread(target=findip, args=(type + 1, pagenum + 1, targeturl, path))
            threads.append(t)
    print('开始爬取代理ip')
    for s in threads:  # 开启多线程爬取
        s.start()
    for e in threads:  # 等待所有线程结束
        e.join()
    print('爬取完成')
    ips = read(path)  # 读取爬到的ip数量

if __name__ == '__main__':
    path = 'ip.txt' # 存放爬取ip的文档path
    targeturl = 'http://www.cnblogs.com/TurboWay/' # 验证ip有效性的指定url
    getip(targeturl,path)

with open("ip.txt", "r") as f:
    ip_list = f.readlines()
    print(ip_list)

new_ip = []
for ip in ip_list:
    ip = ip.replace('\n', '')
    new_ip.append(ip)

proxy_ip = random.choice(new_ip)
proxies = {'http': 'http://'+proxy_ip}


comments_df=[]
count_=0
for comment in comments_list:
    try:
          if (re.search(re.compile(r'^\d+?'),comment)):
              comment_sep=comment.split(" ",5)
              comment_dic={}
              comment_dic['user_id']= comment_sep[0]
              comment_dic['content']= comment_sep[5]
              comment_time=int(comment_sep[3])
              real_time=comment_time*0.001
              real_date = time.strftime('%Y-%m',time.localtime(real_time))
              comment_dic['comment_time']=real_date
              comments_df.append(comment_dic)
              count_=count_+1
          else:
              comments_df[count_-1]['cotent'] +=comment
    except:
         pass

for user in user_list:
    if (re.search(re.compile(r'^\d+?'),user)):
       location={}
       print(user)
       location['user_id']=str(user)
       url='http://music.163.com/user/home?id='+str(user)
       user_page=requests.get(url,headers=getheaders(),proxies=proxies)
       html=BeautifulSoup(user_page.text,'lxml')
       html=str(html)
       pat4=re.compile(u'<span>所在地区：(.+?)</span>')
       city=re.search(pat4,html)
       if city:
              print(city)
              location['location']=str(city.group(1))
       else:
              location['location']='un-known'
       location_list.append(location)
    else:
       continue


