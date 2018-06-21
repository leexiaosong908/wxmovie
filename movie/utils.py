# coding: utf-8

import requests
from bs4 import BeautifulSoup
import sys
import os
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

def get_movie_from_friok(page = 1):
    host = 'http://www.friok.com/category/gaoq/page/{0}'.format(page)
    try:
        wb = requests.get(host,headers = header,timeout=10).content
        soup = BeautifulSoup(wb,'html5lib')
    except BaseException as e:
        print('访问出错:',e)
    
    nums_list = []
    movie_nums = soup.select("h2 > a")
    for m in movie_nums:
        m = m.get("href")[21:-5]
        nums_list.append(m)
    video_list = []
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


    
if __name__ == '__main__':
    #get_movie_from_friok()
    for i in range(52,121):
        print('当前第{}页'.format(i))
        get_movie_from_friok(page=i)