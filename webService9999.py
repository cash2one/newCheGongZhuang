# encoding: UTF-8
from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
import requests
import re
import json
import time
reload(sys)
sys.setdefaultencoding("utf8")

def remoteRequestHeader(url,header):
	respones="error"
        st=time.time() 
	try:
		respones=requests.get(url,headers=header,timeout=5)
	except:
		print "error"
		return 
        end=time.time()
        print url,st,end,end-st,int(len(respones.text))/1024,dict(respones.headers).get('centent-length',0)
	return respones.text,respones.encoding
def remoteRequest(url):
	respones="error"
	try:
		respones=requests.get(url,timeout=5)
	except:
		print "error"
		return
	return respones.text,respones.encoding
if __name__ == "__main__":  
	s = SimpleXMLRPCServer(('0.0.0.0', 10110))
	s.register_function(remoteRequest)
	s.register_function(remoteRequestHeader)
	s.serve_forever()
