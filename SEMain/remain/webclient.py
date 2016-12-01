# encoding: UTF-8
from suds.client import Client  
import sys
import os
import json
from xmlrpclib import ServerProxy
ip="10.136.162.26"
    
if __name__ == '__main__':
	s = ServerProxy("http://127.0.0.1:8989")
	print s,s.remoteRequest("http://www.baidu.com")
	 






