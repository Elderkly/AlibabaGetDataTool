# coding=utf-8
import threading # 导入threading模块
from queue import Queue #导入queue模块
import time  #导入time模块

# 爬取文章详情页
def get_detail_html(detail_url_list, id):
    while True:
        url = detail_url_list.get() #Queue队列的get方法用于从队列中提取元素
        time.sleep(2)  # 延时2s，模拟网络请求和爬取文章详情的过程
        print("thread {id}: get {url} detail finished".format(id=id,url=url)) #打印线程id和被爬取了文章内容的url

# 爬取文章列表页
def get_detail_url(queue):
    for i in range(10000):
        time.sleep(1) # 延时1s，模拟比爬取文章详情要快
        queue.put("http://testedu.com/{id}".format(id=i))#Queue队列的put方法用于向Queue队列中放置元素，由于Queue是先进先出队列，所以先被Put的URL也就会被先get出来。
        print("get detail url {id} end".format(id=i))#打印出得到了哪些文章的url

#主函数
if __name__ == "__main__":
    detail_url_queue = Queue(maxsize=1000) #用Queue构造一个大小为1000的线程安全的先进先出队列
    # 先创造四个线程
    thread = threading.Thread(target=get_detail_url, args=(detail_url_queue,)) #A线程负责抓取列表url
    html_thread= []
    for i in range(3):
        thread2 = threading.Thread(target=get_detail_html, args=(detail_url_queue,i))
        html_thread.append(thread2)#B C D 线程抓取文章详情
    start_time = time.time()
    # 启动四个线程
    thread.start()
    for i in range(3):
        html_thread[i].start()
    # 等待所有线程结束，thread.join()函数代表子线程完成之前，其父进程一直处于阻塞状态。
    thread.join()
    for i in range(3):
        html_thread[i].join()

    print("last time: {} s".format(time.time()-start_time))#等ABCD四个线程都结束后，在主进程中计算总爬取时间。
