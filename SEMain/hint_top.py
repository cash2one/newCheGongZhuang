# encoding: utf-8
import requests
import sys
import re
import threading
import json
from xmlrpclib import ServerProxy
import time
import datetime
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding("utf8")
ip="10.136.35.68"
ip1="127.0.0.1"
def getRemoteClientHeader(url,header):
    s=ServerProxy("http://%s:%d"%(ip1,10110))
    result=s.remoteRequestHeader(url,header)
    return result[0]
def getRemoteClientHeader_2(url,header):
    s=ServerProxy("http://%s:%d"%(ip1,10110))
    result= s.remoteRequestHeader(url,header)
    return result
def getRemoteClient(url):
    s=ServerProxy("http://%s:%d"%(ip1,10110))
    result= s.remoteRequest(url)
    return result[0]
def getRemoteClient_2(url):
    s=ServerProxy("http://%s:%d"%(ip1,10110))
    result= s.remoteRequest(url)
    return result
if __name__ == "__main__":
    word = "卡"
    search_dict={'baidu':'true','sogou':'false','s360':'false','bing':'false','china_so':'false','shen_ma':'false'}
    print getRemoteClient("http://www.baidu.com")
