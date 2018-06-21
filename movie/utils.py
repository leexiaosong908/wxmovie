# coding: utf-8

import requests
from bs4 import BeautifulSoup
import sys
import os
import time
import schedule
import threading
from datetime import datetime as dt

from django.core.wsgi import get_wsgi_application
sys.path.extend(['/home/sg/wxmovie',])
os.environ.setdefault('DJANGO_SETTINGS_MODULE','wxmovie.settings')
application = get_wsgi_application()
import django
django.setup()
from movie.models import *

header = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'Connection':'keep-alive',
    'Host':'www.friok.com',
    'Referer':'http://www.friok.com/'
}
def print_file(pstr):
    with open('dump.log','a') as f:
        dts = dt.now().strftime('%Y%m%d %H:%M:%S:%f')
        pstr = '%s %s'%(dts, pstr)
        print(pstr,file = f)

def get_movie_from_friok2():
    list_urls = []
    detail_ids = []

    # 获取总页数
    gaoq_url = 'http://www.friok.com/category/gaoq'
    gaoq_data = requests.get(gaoq_url,headers = header,timeout=30).content
    gaoq_soup = BeautifulSoup(gaoq_data,'html5lib')
    pagenums = gaoq_soup.select('.page-numbers')
    pagemax = int(pagenums[-2].text)
    #print(pagemax)

    # 生成列表页的url
    for page in range(1,pagemax):
        #if page % 2 == 0:
        
        host = 'http://www.friok.com/category/gaoq/page/{0}'.format(page)
        list_urls.append(host)
    #print(list_urls)

    # 获取资源id
    # for url in list_urls:
    #     try:
    #         detail = requests.get(url,headers = header,timeout=20).content
    #         soup = BeautifulSoup(detail,'html5lib')
    #         ds = soup.select('h2 > a')
    #         if len(ds) > 0:
    #             for d in ds:
    #                 d = d.get("href")
    #                 d = d.split('m/')[1].split('.')[0]
    #                 #print(d)
    #                 if d is not None:
    #                     detail_ids.append(d)
    #                 else:
    #                     continue
    #             list_urls.remove(url)
    #         else:
    #             print('资源获取失败:%s'%url)
    #             continue
    #     except BaseException as e:
    #         print('访问出错:%s %s'%(e,url))
    #         continue

    # print('资源数量:%d'%len(detail_ids))
    # print('资源剩余:%d \n %s'%(len(list_urls),list_urls))

    # 获取资源id
    while len(list_urls) > 0:
        with open('utils.log','a') as f:
            dts = dt.now().strftime('%Y%m%d %H:%M:%S:%f')
            print('%s 获取:%d 剩余:%d页'%(dts, len(detail_ids), len(list_urls)),file=f)
        try:
            url = list_urls[-1]
            detail = requests.get(url,headers = header,timeout=20).content
            soup = BeautifulSoup(detail,'html5lib')
            ds = soup.select('h2 > a')
            if len(ds) > 0:
                for d in ds:
                    d = d.get("href")
                    d = d.split('m/')[1].split('.')[0]
                    #print(d)
                    if d is not None:
                        detail_ids.append(d)
                    else:
                        continue
                list_urls.remove(url)
            else:
                print('资源获取失败:%s'%url)
                continue
        except BaseException as e:
            print('访问出错:%s %s'%(e,url))
            continue
    else:
        print('一共 %d 资源'%len(detail_ids))
        print(detail_ids)

    # 获取下载页信息
    for n in detail_ids:
        try:
            down_url = 'http://www.friok.com/download.php?id='+n
            down_data = requests.get(down_url,headers = header, timeout=20).content
            dsoup = BeautifulSoup(down_data,'html5lib')
            name = dsoup.title.get_text()[:-4]
            link = dsoup.select_one('div.list > a').get('href')
            passwd = dsoup.select('div.desc > p')[1].get_text().split(': ')[-1]
            result = Movie.objects.get_or_create(
                title = name,
                link = link,
                passwd = passwd
            )
            print('[*]完成数据写入:',name,link,passwd)
            detail_ids.remove(n)
        except Exception as e:
            print('[-]数据写入错误%s %s'%(down_url,e))
            continue


def get_movie_from_friok(page = 1):
    host = 'http://www.friok.com/category/gaoq/page/{0}'.format(page)
    try:
        wb = requests.get(host,headers = header,timeout=10).content
        soup = BeautifulSoup(wb,'html5lib')

        nums_list = []
        movie_nums = soup.select("h2 > a")
        for m in movie_nums:
            m = m.get("href")[21:-5]
            nums_list.append(m) 
    except BaseException as e:
        print('访问出错:',e)
    
    print(nums_list)


    for n in nums_list:
        down_url = 'http://www.friok.com/download.php?id='+n

        try:
            down_data = requests.get(down_url,headers = header).content
        
            try:    
                dsoup = BeautifulSoup(down_data,'html5lib')
                name = dsoup.title.get_text()[:-4]
                link = dsoup.select_one('div.list > a').get('href')
                passwd = dsoup.select('div.desc > p')[1].get_text().split(': ')[-1]
                result = Movie.objects.get_or_create(
                    title = name,
                    link = link,
                    passwd = passwd
                )
                print('[*]完成数据写入:',name,link,passwd)
            except Exception as e:
                print('[-]数据写入错误',e)
                continue
        except BaseException as e:
            print('[-]数据下载出错',e)
            continue


def task_friok():
    threading.Thread(target=get_movie_from_friok2).start()

if __name__ == '__main__':
    #get_movie_from_friok()
    # for i in range(52,121):
    #     print('当前第{}页'.format(i))
    #     get_movie_from_friok(page=i)

    schedule.every().day.at("21:27").do(task_friok)
    while True:
        schedule.run_pending()
        time.sleep(1)
    