import os, datetime

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from app.model import *
from app import util

class MainPage(webapp.RequestHandler):
  """ Renders the main template."""
  def get(self):
    referer = 'null'
    if os.environ.has_key('HTTP_REFERER'):
      referer = os.environ['HTTP_REFERER']    
    template_values = {
      'title':'AJAX Add (via GET)',
      'referer': referer,
    }
    path = os.path.join(os.path.dirname(__file__), "../templates/rpc.html")
    self.response.out.write(template.render(path, template_values))

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
    
    id = int(self.request.get('id'))
    if id:
      result = func(id)
      template_values = {
        'comm': result,
      }
      path = os.path.join(os.path.dirname(__file__), "../templates/rc_detail.html")
      self.response.out.write(template.render(path, template_values))
    """args = ()
    while True:
      key = 'arg%d' % len(args)
      val = self.request.get(key)
      if val:
        args += (simplejson.loads(val),)
      else:
        break
    result = func(*args)
    self.response.out.write(result)"""
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

  """def Add(self, *args):
    # The JSON encoding may have encoded integers as strings.
    # Be sure to convert args to any mandatory type(s).
    ints = [int(arg) for arg in args]
    return sum(ints)"""
  def rc_detail_ajax(self, comm_id):
    comm = Comment.get_by_id(comm_id)
    if comm is not None:
      return comm
    return "not found"
    
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