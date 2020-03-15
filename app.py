# coding=utf-8
import re
import sys
import time
import requests
import urllib2
import threading
from flask import request
from flask import Flask
from flask_cors import CORS
from bs4 import BeautifulSoup

mainJson = []
app = Flask(__name__)
CORS(app, supports_credentials=True)
reload(sys)
sys.setdefaultencoding('utf8')

# 创建线程类，继承Thread类
class MyThread(threading.Thread):
  def __init__(self, func, args):
    threading.Thread.__init__(self) # 调用父类的构造函数
    self.args = args
    self.func = func
 
  def run(self): # 线程活动方法
    apply(self.func, self.args)

# 爬取页面html结构
def get_html(url):
    headers = {
        'User-Agent':'Mozilla/5.0(Macintosh; Intel Mac OS X 10_11_4)\
        AppleWebKit/537.36(KHTML, like Gecko) Chrome/52 .0.2743. 116 Safari/537.36'
    }     #模拟浏览器访问
    response = requests.get(url,headers = headers)       #请求访问网站
    html = response.text       #获取网页源码
    return html                #返回网页源码

#   获取产品类别
@app.route('/getProductCategories', methods=['GET','POST'])
def getData():
    url = request.args.get("url")
    menu = []
    if url:
        try:
            soup = BeautifulSoup(get_html(url + '/productlist.html'), 'lxml')   #初始化BeautifulSoup库,并设置解析器
            for li in soup.find_all(attrs={"class": "next-menu ver group-menu"}):         #遍历父节点
                    for a in li.find_all(name='a'):     #遍历子节点
                        if a.string==None:
                            pass
                        else:
                            menu.append({'text':a.string,'href':url + a['href']})
        except:
            return {'code':50001,'msg':'地址出错'}
        else:
            return {'code':0,'data':menu}
    else:
        return {'code':50001,'msg':'地址出错'}

#   获取最大分页页数
@app.route('/getMaxPage')
def getMaxPage():
    page = 1
    maxPage = 1
    url = request.args.get("url")
    if url:
        try:
            _url = get_getCommodityList_url(url, page)
            soup = BeautifulSoup(get_html(_url), 'lxml')   #初始化BeautifulSoup库,并设置解析器
            #   爬取翻页按钮 写入总页数
            for nextBtn in soup.find_all(attrs={"class": "next-pagination-pages"}):
                _page = nextBtn.find_all(attrs={"class": ["next-btn next-btn-normal next-btn-medium next-pagination-item","next-btn next-btn-normal next-btn-medium next-pagination-item current"]})[-1].string
                if _page !=None:
                    maxPage = int(_page)
                # print('总页数%s'%_page)
        except:
            return {'code':50001,'msg':'地址出错'}
        else:
            return {'code':0,'data':{'page':maxPage}}
    else:
        return {'code':50001,'msg':'地址出错'}

#   获取商品列表
@app.route('/getCommodityList')
def getCommodityList():
    mainJson = []
    page = int(request.args.get("page"))
    maxPage = int(request.args.get("maxPage"))
    url = request.args.get("url")
    if url:
        try:
            _url = get_getCommodityList_url(url, page)
            getJson = getList(url, page, maxPage, mainJson)
        except Exception as r:
            print('未知错误 %s' %r)
            return {'code':50001,'msg':'获取商品列表失败','data': mainJson}
        else:
            return {'code':0,'data':mainJson}
    else:
        return {'code':50001,'msg':'地址出错'}

#   递归爬取所有商品
def getList(url, page, maxPage, mainJson):
    if url:
        _url = get_getCommodityList_url(url,page)
        # print(_url)
        soup = BeautifulSoup(get_html(_url), 'lxml')   #初始化BeautifulSoup库,并设置解析器
        box = soup.find(attrs={"class": "component-product-list"})                           #   父节点
        listArray = box.find_all(attrs={"class": ["icbu-product-card vertical large product-item","icbu-product-card vertical large product-item last"]})  #   所有子节点
         # 多线程
        t_start = time.time()
        threadList = [MyThread(get_deitails_keyword, (item, url, mainJson, index, len(listArray))) for index,item in enumerate(listArray)]
        # 调用线程类创建新线程，返回线程列表
        for t in threadList:
            t.setDaemon(True) # 设置守护线程，父线程会等待子线程执行完后再退出
            t.start() # 线程开启
        for i in threadList:
            i.join() # 等待线程终止，等子线程执行完后再执行父线程
        # print('第%s页耗时%s'%(page,(time.time()-t_start)))
        mainJson = mainJson.sort(key = lambda x:x["time"])
        return mainJson
    else:
        mainJson = mainJson.sort(key = lambda x:x["time"])
        return mainJson
        
#   爬取详情页关键词
def get_deitails_keyword(item, url, mainJson, index, length):
    a = item.find(name = 'a')
    span = item.find(attrs={"class": "title-con"})
    start_time = time.time()
    if span.string != None:
        keyWord = []
        try:
            details = BeautifulSoup(get_html('https://geqian.en.alibaba.com'+a['href']), 'lxml')
            title = details.find(name = 'title').string
            # print(title)
            name = re.sub(span.string,'',title,flags=re.IGNORECASE)
            name = name.replace(' - Buy ','')
            name = name.replace(' Product on Alibaba.com','')
            keyWord = name.split(',')
        except Exception as r:
            keyWord = []
            print('获取关键词出错 %s' %r)
        else:
            mainJson.append({'text':span.string, 'keyWord': keyWord, 'time': start_time})
    # if index == length:               #   当前周期遍历完毕
    #     print('第' + str(page) + '页爬取结束')
    #     if page != maxPage:                     #   如果不是最后一页则递归遍历 直到所有数据爬取完毕
    #         return getList(url, page + 1, maxPage, mainJson)
    #     else:
    #         return mainJson

# 爬取商品时根据分页拼接url
def get_getCommodityList_url(url,page):
    urlArray = url.split('/')
    pageUrl = urlArray[3][-2:]
    page = (0 if (page == 1) else page)
    if (pageUrl.find('-') == -1):
        urlArray[3] = urlArray[3] + '-' + str(page)
    else:
        urlArray[3] = urlArray[3][:-2] + '-' + str(page)
    _url = '/'.join(urlArray)
    return _url

#   查询关键词
@app.route('/getKeyWord')
def getKeyWord():
    keyWordArray = []
    url = request.args.get("url")
    if url:
        try:
            details = BeautifulSoup(get_html(url), 'lxml')
            title = details.find(name = 'title').string
            # print(title)
            name = re.sub(details.find(attrs = {'class': 'ma-title'}).string,'',title,flags=re.IGNORECASE)
            name = name.replace(' - Buy ','')
            name = name.replace(' Product on Alibaba.com','')
            # print(name)
            keyWordArray = name.split(',')
        except Exception as r:
            print('getKeyWordError%s' %r)
            return {'code':50001,'msg':'地址出错'}
        else:
            return {'code':0,'data':keyWordArray}
    else:
        return {'code':50001,'msg':'地址出错'}

if __name__ == "__main__":
    app.run(
        host = '0.0.0.0',#任何ip都可以访问
        port = 5000,#端口
        debug = False
    )

