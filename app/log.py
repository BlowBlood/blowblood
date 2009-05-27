# this is log's decoration function definition
import os
import util
from model import Counter, Visitor
from google.appengine.api import users

def counter(handler_method):
  def wrapper(self, *args, **kwargs):
    counter = Counter.all().get()
    if counter is None:
        counter = Counter()
        counter.put()
    if not users.is_current_user_admin():
      counter.count += 1
      counter.put()
    return handler_method(self, *args, **kwargs)
  return wrapper
  
def visitor(handler_method):
  def wrapper(self, *args, **kwargs):
    visitor = Visitor()
    visitor.nickname= os.environ['USER_EMAIL']
    visitor.userIP = os.environ['REMOTE_ADDR']
    visitor.url = os.environ['PATH_INFO']
    visitor.webbrowser = os.environ['HTTP_USER_AGENT']
    if os.environ.has_key('HTTP_REFERER'):
      visitor.referer = os.environ['HTTP_REFERER']    
    visitor.put()
    handler_method(self, *args, **kwargs)
  return wrapper