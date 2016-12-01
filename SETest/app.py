#coding:utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

import os.path
import urllib
from json import JSONEncoder,loads,dumps
import datetime
import time
import re
from info_search import getUrlDict,asynchronous,asynchronous_page,multi_thread_page,multi_page,thread_page,threading_page,news_threading_page,threading_all_page,word_match,multiproc
import sugesstion
import hint_top_search
import relate_search
from tornado.options import define, options
import recommend
from record import onServerStartCreateLogTable,onQueryRecordLog
#from apscheduler.schedulers.blocking import BlockingScheduler
#import MySQLdb
import cgi
import json
#from suds.client import Client

define("port", default=7000, type=int, help="runs on port")

class BaseHandler(tornado.web.RequestHandler):
    #@tornado.web.asynchronous
    #@tornado.gen.coroutine
    def auth(self,ticket):
        ip="10.136.162.17"
        port=8080
        client = Client("http://%s:%s/AuthProxy/webservice/ServiceAuth?wsdl" % (ip, port),)
        client.options.cache.clear()
        result=client.service.ncs_parseTicket(ticket,"signValue" ,"127.0.0.1")
        k= json.loads(result)['content']
        key=k.keys()[0]
        value=k.get(key)
        boolrst=client.service.ncs_validateTicket(ticket,"signValue","127.0.0.1")
        print boolrst
        result=json.loads(boolrst)['status']
        res=0
        if result == 1:
            res=1
        return res
    def get_current_user(self):
        return self.get_secure_cookie("ticket")
    def render_login(self):
        url="http://123.125.45.244/login?_return=http://123.125.45.242:9999/&_sysid=2"
        self.redirect(url)
    def check_user(self):
        return 1
        name=self.get_current_user()
        result=self.auth(name)
        res=0
        if not self.get_current_user():
            self.render_login()
            res=0
        elif result== 0 or result ==None:
            self.render_login()
            res=0
        else:
            res=1

def qitaQueryForLog(type,word,search_dict):
    global suggestion_map,relate_search_map,hint_top_map,old_query
    if word != old_query:
        suggestion_map = {}
        relate_search_map = {}
        hint_top_map = {}
        old_query=word
    if type=="6":
        if suggestion_map: 
            return
        suggestion_map = sugesstion.start(word)# 联想词
    elif type=="7":
        if relate_search_map: 
            return
        relate_search_map = relate_search.threading_page(word, search_dict)  # 相关搜索
    elif type=="8":
        if hint_top_map:
            return
        hint_top_map = hint_top_search.hint_top(word, search_dict)  # 为你推荐


class RecommendHandler(tornado.web.RequestHandler):
    def get(self):
        query = self.get_argument('q',default="")
        pn = int(self.get_argument('pn', default='1'))
        url_type = self.get_argument('url_type', default='')
        search_dict={
            'baidu':self.get_argument('baidu',default='false'),
            's360':self.get_argument('s360',default='false'),
            'sogou':self.get_argument('sogou',default='false'),
            'china_so':self.get_argument('china_so',default='false'),
            'bing':self.get_argument('bing',default='false'),
            'shen_ma':self.get_argument('shen_ma',default='false'),

        }
        reco_list = []
        if query == "":
            #print "word empty"
            self.write("{\"status\":0}")
        else:
            datas = recommend.start(query,search_dict)
         #   self.write(datas)
            datas = loads(datas)
            if datas['status'] == 1:
                for key, value in datas.items():
                    if key != 'status':
                        reco_list = value;
            else:
                self.write("response status is 0!")

            self.render(
                "recommendQuery.html",
                reco_list=reco_list,
                search_dict=search_dict,
                pn=pn,
                url_type=url_type,
                searchword=query)

# 请求URL 路径为 　domain:port／的事件响应
class IndexHandler(BaseHandler):
    def get(self):
        if self.check_user()==1:
            self.render('index.html')

class SuggestionHandler(BaseHandler):
    def get(self):
        word = self.get_argument('term',default='')
        #print word
        if word == "":
            return
        datas =sugesstion.start(word)
        result = []
        for key,value in datas.items():
            result.append(key+"--" +value)
        self.write(JSONEncoder().encode(result))

class ResultItemModule(tornado.web.UIModule):
    def render(self, resultItem):
        return self.render_string(
            "modules/resultItem.html",
            resultItem=resultItem
        )

class NewsItemModule(tornado.web.UIModule):
    def render(self, resultItem):
        return self.render_string(
            "modules/newsItem.html",
            data=resultItem
        )

class HeaderItemModule(tornado.web.UIModule):
    def render(self, id):
        return self.render_string(
            "modules/headerItem.html",
            id=id
        )

# 请求URL 路径为 　domain:port／query　的事件响应
class NewsQueryHandler(tornado.web.RequestHandler):
    def get(self):
        # 获取URL参数
        query = self.get_argument('q', default='')
        filte = self.get_argument('filte', default='false')
        pn = int(self.get_argument('pn', default='1'))
        url_type = self.get_argument('url_type', default='')

        mobile = self.get_argument('mobile',default='false')

        if(mobile == 'true'):
		     search_dict={
            'm_baidu':self.get_argument('m_baidu',default='false'),
            'm_s360':self.get_argument('m_s360',default='false'),
            'm_sogou':self.get_argument('m_sogou',default='false'),
            'm_china_so':self.get_argument('m_china_so',default='false'),
            'm_bing':self.get_argument('m_bing',default='false'),
        }
        else:
		     search_dict={
            'baidu':self.get_argument('baidu',default='false'),
            's360':self.get_argument('s360',default='false'),
            'sogou':self.get_argument('sogou',default='false'),
            'china_so':self.get_argument('china_so',default='false'),
            'bing':self.get_argument('bing',default='false'),
            'shen_ma':self.get_argument('shen_ma',default='false'),
        }

        # 获取所有搜索引擎第pn页的搜索结果
        datalist = news_threading_page(query, pn, search_dict)

        # TODO content根据选择种类来进行分类
        searchResult = []
        if datalist:
            one_search_data = datalist[0]  # 一个search取一个data即可
            if one_search_data['status'] ==0:
                print "news 获取数据失败"
            searchResult = one_search_data.get('data')
            #print searchResult
        # 模板引擎动态生成网页
        self.render(
            "newsQuery.html",
            searchResult=searchResult,
            search_dict=search_dict,
            pn=pn,
            url_type=url_type,
            searchword=query)



# 请求URL 路径为 　domain:port／queryAll　的事件响应
class AllQueryHandler(BaseHandler):
    def get(self):
        # 获取URL参数
        result=self.check_user()
        if result == 0:
            return
        query_init = self.get_argument('q',default='')
        query = self.get_argument('q',default='')
        try:
			query_gbk=query.encode('gbk','ignore')
			#print query_gbk
        except:
            f.write("error")
	
        query = urllib.quote(query.encode('utf-8'))
        filte = self.get_argument('filte',default='false')
        pn = int(self.get_argument('pn',default='1'))
        content_type = self.get_argument('content_type', default='2')
        cur_time = str(time.strftime('%Y-%m-%d %X',time.localtime()))
        search_dict={
            'baidu':self.get_argument('baidu',default='false'),
            's360':self.get_argument('s360',default='false'),
            'sogou':self.get_argument('sogou',default='false'),
            'china_so':self.get_argument('china_so',default='false'),
            'bing':self.get_argument('bing',default='false'),
            'shen_ma':self.get_argument('shen_ma',default='false'),
        }

        search_String = ""
        search_other_String = ""
        for key in search_dict:
            if search_dict[key] == 'true':
                search_String = search_String+"&"+key+"=true"
            else:
                search_other_String = search_other_String+"&"+key+"=true"

        self.set_cookie("search_String", search_String)
        self.set_cookie("search_other_String", search_other_String)


        url_dict = getUrlDict(query,pn,content_type,search_dict)
        if url_dict is None:
            url_dict = {}
        global suggestion_map,relate_search_map,hint_top_map
        # 模板引擎动态生成网页
        self.render(
            "all-query-new.html",
            search_dict=search_dict,
            searchword=query,
            pn=pn,
            url_dict=url_dict,
            content_type=content_type,
            baidu=self.get_argument('baidu', default='false'),
            s360=self.get_argument('s360', default='false'),
            sogou=self.get_argument('sogou', default='false'),
            china_so=self.get_argument('china_so', default='false'),
            bing=self.get_argument('bing', default='false'),
        )


# 请求URL 路径为 　domain:port／queryAll　的事件响应
class AllQueryHandler2(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def remoteServer(self, ip, content_type, query_init, search_dict):
        global suggestion_map, relate_search_map, hint_top_map
        onQueryRecordLog(ip,(content_type),query_init,dumps(suggestion_map, ensure_ascii=False),dumps(relate_search_map,ensure_ascii=False),dumps(hint_top_map,ensure_ascii=False))

    def get(self):
        # 获取URL参数
        result = self.check_user()
        if result == 0:
            return
        query_init = self.get_argument('q', default='')
        query = self.get_argument('q', default='')
        try:
            query_gbk = query.encode('gbk', 'ignore')
        # print query_gbk
        except:
            f.write("error")

        query = urllib.quote(query.encode('utf-8'))
        filte = self.get_argument('filte', default='false')
        pn = int(self.get_argument('pn', default='1'))
        content_type = self.get_argument('content_type', default='2')
        cur_time = str(time.strftime('%Y-%m-%d %X', time.localtime()))
        search_dict = {
            'baidu': self.get_argument('baidu', default='false'),
            's360': self.get_argument('s360', default='false'),
            'sogou': self.get_argument('sogou', default='false'),
            'china_so': self.get_argument('china_so', default='false'),
            'bing': self.get_argument('bing', default='false'),
            'shen_ma': self.get_argument('shen_ma', default='false'),
        }

        search_String = ""
        search_other_String = ""
        for key in search_dict:
            if search_dict[key] == 'true':
                search_String = search_String + "&" + key + "=true"
            else:
                search_other_String = search_other_String + "&" + key + "=true"

        self.set_cookie("search_String", search_String)
        self.set_cookie("search_other_String", search_other_String)

        url_dict = getUrlDict(query, pn, content_type, search_dict)
        if url_dict is None:
            url_dict = {}
        global suggestion_map, relate_search_map, hint_top_map
        qitaQueryForLog(content_type, query_init, search_dict)
        # 动作写入日志
        self.remoteServer(self.request.remote_ip, content_type, query_init, search_dict)
        # 模板引擎动态生成网页
        self.render(
            "all-query.html",
            search_dict=search_dict,
            searchword=query,
            pn=pn,
            url_dict=url_dict,
            content_type=content_type,
        )


# 请求URL 路径为 　domain:port／queryQita　的事件响应
class QitaQueryHandler(tornado.web.RequestHandler):
    def get(self):
        word = self.get_argument('q',default='')
        #qita类型 1代表联想次 2代表相关搜索 3代表为您推荐
        q_type = self.get_argument('q_type', default='1')
        is_ajax = self.get_argument('is_ajax', default="false")
        print word
        if word == "":
            return
        search_dict = {'baidu': 'true', 's360': 'true', 'sogou': 'true', 'bing': 'true', 'china_so': 'true',
                       'shen_ma': 'true'}
        data_map = {}
        global suggestion_map,relate_search_map,hint_top_map
        if q_type == '1':
            data_map =suggestion_map
        elif q_type == '2':
            data_map =relate_search_map
        else:
            data_map =hint_top_map

        if is_ajax == "true":
            self.write(dumps(data_map))
        else:
            self.render(
                "qitaQuery.html",
                data_map=data_map,
                searchword=word)

class LoginHandler(BaseHandler):
    def get(self):
        ticket=""
        #result = self.check_user()
        result = 1
        if result == 1:
            self.render("index.html")
    def post(self):
        try:
            print "start recevice tickit"
            ticket=self.get_argument("ticket")
            result=self.auth(ticket)
            if result == 1:
                self.set_secure_cookie("ticket",ticket,expires_days=None)
                self.render("index.html")
        except:
            print "login_post_error"
            self.render_login() 
class LogoutHandler(BaseHandler):
    def get(self):
        if self.get_current_user() !=None:
            self.set_secure_cookie("ticket",'')
            self.redirect("http://123.125.45.244:80/logout")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    global suggestion_map,relate_search_map,hint_top_map,old_query
    old_query=""
    suggestion_map={}
    hint_top_map={}
    relate_search_map={}
    settings={'cookie_secret' : 'S6Bp2cVjSAGFXDZqyOh+hfn/fpBnaEzFh22IVmCsVJQ='}
    app = tornado.web.Application(
        handlers=[(r"/index", IndexHandler),
                  (r"/",LoginHandler),
                  (r"/logout",LogoutHandler),
                  (r"/queryAll", AllQueryHandler),
                  (r"/queryAll2", AllQueryHandler2),
                  #(r"/query", QueryHandler),
                  (r"/queryNews", NewsQueryHandler),
                  (r"/queryQita", QitaQueryHandler),
                  (r"/recommend", RecommendHandler),
                  (r"/suggest",SuggestionHandler)],

        # 设置　templates　及　static 路径，可在html 中引用本地文件
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        ui_modules={"ResultItem": ResultItemModule,"HeaderItem": HeaderItemModule,"NewsItem": NewsItemModule},
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        #开启此项，修改代码后服务器自动重启
        debug=True,**settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    #onServerStartCreateLogTable()
    tornado.ioloop.IOLoop.instance().start()

