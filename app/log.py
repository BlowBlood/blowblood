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
    if (os.environ.get('USER_IS_ADMIN', '0')) != '1':
      visitor = Visitor()
      visitor.nickname= os.environ.get('USER_EMAIL','')
      visitor.userIP = os.environ.get('REMOTE_ADDR','')
      visitor.url = os.environ.get('PATH_INFO','')
      visitor.webbrowser = os.environ.get('HTTP_USER_AGENT','')
      visitor.referer = os.environ.get('HTTP_REFERER','')
      visitor.put()
    handler_method(self, *args, **kwargs)
  return wrapper