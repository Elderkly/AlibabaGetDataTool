# coding=utf-8
import requests
from flask import request
from flask import Flask
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, supports_credentials=True)

def get_html(url):
    headers = {
        'User-Agent':'Mozilla/5.0(Macintosh; Intel Mac OS X 10_11_4)\
        AppleWebKit/537.36(KHTML, like Gecko) Chrome/52 .0.2743. 116 Safari/537.36'

    }     #模拟浏览器访问
    response = requests.get(url,headers = headers)       #请求访问网站
    html = response.text       #获取网页源码
    return html                #返回网页源码

@app.route('/getData', methods=['GET','POST'])
def getData():
    url = request.args.get("url")
    menu = []
    if url:
        soup = BeautifulSoup(get_html(url), 'lxml')   #初始化BeautifulSoup库,并设置解析器
        for li in soup.find_all(attrs={"class": "next-menu ver group-menu"}):         #遍历父节点
                for a in li.find_all(name='a'):     #遍历子节点
                    if a.string==None:
                        pass
                    else:
                        menu.append(a.string)
        return {'code':0,'msg':menu}
    else:
        return {'code':50001,'msg':'地址出错'}

if __name__ == "__main__":
    app.run(
    host = '0.0.0.0',#任何ip都可以访问
    port = 5000,#端口
    debug = True
)

