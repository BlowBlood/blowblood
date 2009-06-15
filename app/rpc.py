import os, datetime

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch, memcache

from app.model import *
from app import util

class RPCHandler(webapp.RequestHandler):
  """ Allows the functions defined in the RPCMethods class to be RPCed."""
  def __init__(self):
    webapp.RequestHandler.__init__(self)
    self.methods = RPCMethods()
 
  def get(self):
    func = None
   
    action = self.request.get('action')
    if action:
      if action[0] == '_':
        self.error(403) # access denied
        return
      else:
        func = getattr(self.methods, action, None)
   
    if not func:
      self.error(404) # file not found
      return   
        
    func(self.request,self.response)
    
  def post(self):
    func = None
    action = self.request.get('action')
    if action:
      if action[0] == '_':
        self.error(403) # access denied
        return
      else:
        func = getattr(self.methods, action, None)
    if not func:
      self.error(404) # file not found
      return
    result = func()
    self.response.out.write(result)
      

class RPCMethods:
  """ Defines the methods that can be RPCed.
  NOTE: Do not allow remote callers access to private/protected "_*" methods.
  """

  """ GET Methids"""
  def rc_detail_ajax(self, request_,response_):
    try:
      comm_id = int(request_.get('id'))
    except ValueError:
      return response_.out.write("comm_id is invalid")
    comm = Comment.get_by_id(comm_id)
    if comm is None:
      return response_.out.write("comm_id is not found")
    path = os.path.join(os.path.dirname(__file__), "../templates/rc_detail.html")
    response_.out.write(template.render(path, {'comm': comm}))
  
  def get_gravatar(self, request_,response_):
    try:
      gravatar_id = request_.get('id')
    except ValueError:
      return response_.out.write("email is invalid")
    key_ = "gravatar_" + gravatar_id
    result_content = memcache.get(key_)
    if result_content is not None:
      response_.headers['Content-Type'] = "image/png"
      return response_.out.write(result_content)
    else:
      # construct the url
      default = "http://www.blowblood.com/static/images/unkown.jpg"
      gravatar_url = "http://www.gravatar.com/avatar.php?"
      gravatar_url += urllib.urlencode({'gravatar_id':gravatar_id, 'default':default, 'size':'32'})
      result = urlfetch.fetch(gravatar_url)
      if result.status_code == 200:
        response_.headers['Content-Type'] = "image/png"
        response_.out.write(result.content)
        if not memcache.add(key_, result.content, 3600):
          logging.error("Memcache set failed.")
      else:
        response_.out.write("No Image")
      
  def get_visitors(self, request_,response_):
    uas=UserAgent.all().fetch(500)
    user_agents = {}
    date = {}
    for ua in uas:
     user_agents[ua.name] = ua.count
     date[ua.name] = ua.date
    visitors = Visitor.all().order("date").fetch(200)
    for visitor in visitors:
      webbrowser = visitor.webbrowser
      num = user_agents.get(webbrowser,0)
      if num == 0:
        user_agents[webbrowser] = 1
        date[webbrowser] = visitor.date
      else:
        user_agents[webbrowser] = num + 1
    db.delete(visitors)
    db.delete(uas)
    for uakey in user_agents.keys():   
      ua = UserAgent()
      ua.name = uakey
      ua.count = user_agents[uakey]
      ua.date = date[uakey]
      ua.put()
    ua_list = UserAgent.all().fetch(500)
    path = os.path.join(os.path.dirname(__file__), "../templates/visitors.html")
    response_.out.write(template.render(path, {'ua_list': ua_list}))
      
  """ POST Methids"""
  def rbtags(self):
    d={}
    posts = Post.all()
    for post in posts:
      for tag in post.tags:
        d[tag] = d.get(tag,0) + 1
    dbtags = Tag.all().fetch(1000)
    db.delete(dbtags)
    for key in d.keys():
      tag_ = Tag()
      tag_.name = key
      tag_.num = d[key]
      tag_.put()    
    return "ok"
    
  def rbarchives(self):
    d={}
    date = {}
    posts = Post.all().order("date")
    for post in posts:
      my = post.monthyear
      num = d.get(my,0)
      if num == 0:
        d[my] = 1
        date[my] = post.date
      else:
        d[my] = num + 1
    archives = Archive.all().fetch(1000)
    db.delete(archives)
    for key in d.keys():
      archive_ = Archive()
      archive_.monthyear = key
      archive_.num = d[key]
      archive_.date = date[key]
      archive_.put()
    util.flushArchiveLists()
    return "ok"
  
  def rbcategories(self):
    d={}
    posts = Post.all()
    for post in posts:    
      d[post.catalog] = d.get(post.catalog,0) + 1
    categories = Category.all().fetch(1000)
    db.delete(categories)
    for key in d.keys():
      category_ = Category()
      category_.name = key
      category_.num = d[key]
      category_.put()    
    return "ok"
      
  def flushall(self):
    util.flushAll() 
    return "ok"

class GetGravatar(webapp.RequestHandler):
  def get(self,gravatar_id):
    if gravatar_id is None:
      return self.response.out.write("BadId")
    key_ = "gravatar_" + gravatar_id
    result_content = memcache.get(key_)
    if result_content is not None:
      self.response.headers['Content-Type'] = "image/png"
      return self.response.out.write(result_content)
    else:
      # construct the url
      default = "http://www.blowblood.com/static/images/unkown.jpg"
      gravatar_url = "http://www.gravatar.com/avatar.php?"
      gravatar_url += urllib.urlencode({'gravatar_id':gravatar_id, 'default':default, 'size':'32'})
      result = urlfetch.fetch(gravatar_url)
      if result.status_code == 200:
        self.response.headers['Content-Type'] = "image/png"
        self.response.out.write(result.content)
        if not memcache.add(key_, result.content, 3600):
          logging.error("Memcache set failed.")
      else:
        self.response.out.write("NoImage")
