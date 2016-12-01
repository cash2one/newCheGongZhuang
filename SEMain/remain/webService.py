# encoding: UTF-8
from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
import requests
import re
import json
reload(sys)
sys.setdefaultencoding("utf8")

def remoteRequestHeader(url,header):
	respones="error"
	try:
		respones=requests.get(url,headers=header,timeout=2)
	except:
		print error
		return 
	return respones.text,respones.encoding
def remoteRequest(url):
	respones="error"
	try:
		respones=requests.get(url,timeout=2)
	except:
		print error
		return
	return respones.text,respones.encoding
if __name__ == "__main__":  
	s = SimpleXMLRPCServer(('127.0.0.1', 10110))
	s.register_function(remoteRequest)
	s.serve_forever()
