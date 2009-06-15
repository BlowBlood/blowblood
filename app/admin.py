import os, urllib, datetime
import calendar
import re

from google.appengine.api import users, memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from app import util, authorized
from model import Post, Category, UserAgent, Visitor

class BaseRequestHandler(webapp.RequestHandler):
  """Supplies a common template generation function.

  When you call generate(), we augment the template variables supplied with
  the current user in the 'user' variable and the current webapp request
  in the 'request' variable.
  """
  def generate(self, template_name, template_values={}):
    if users.get_current_user():
      url = util.xhtmlize_url(users.create_logout_url(self.request.uri))
      url_linktext = 'Logout'
    else:
      url = util.xhtmlize_url(users.create_login_url(self.request.uri))
      url_linktext = 'Login'
    ym = datetime.datetime.now().strftime("%Y %m %d").split()
    cal = calendar.HTMLCalendar().formatmonth(int(ym[0]),int(ym[1]))
    pattern = '<td class="\w\w\w">'+ym[2]+'</td>'
    today = '<td id="today">'+ym[2]+'</td>'    
    cal = re.sub(pattern,today,cal)
    values = {
      'user': users.GetCurrentUser(),
      'user_is_admin': users.is_current_user_admin(),
      'user_nickname': util.getUserNickname(users.get_current_user()),
      'url': url,
      'url_linktext': url_linktext,  
      'categories': util.getCategoryLists(),
      'calendar': cal,
      'tags': util.getTagLists(),
      'archives': util.getArchiveLists(),
      'counter': util.getCounter(),    
    }    
    values.update(template_values)
    path = os.path.join(os.path.dirname(__file__), template_name)
    self.response.out.write(template.render(path, values))
    
class MainPage(BaseRequestHandler):
  @authorized.role("admin")  
  def get(self):
    categories = Category.all()
    cache_stats = memcache.get_stats()
    oldest_item_age = int(cache_stats['oldest_item_age'])
    format_time = str(oldest_item_age/3600)+":"
    oldest_item_age = oldest_item_age%3600
    format_time += str(oldest_item_age/60)+":"
    oldest_item_age = oldest_item_age%60
    format_time += str(oldest_item_age/60)
    cache_stats['oldest_item_age'] = format_time
    ua_list = UserAgent.all().fetch(500)
    ua_list = sorted(ua_list,key = lambda x:x.count,reverse = True)
    visitor_counter = Visitor.all().count()
    template_values = {
      'cache_stats': cache_stats,
      'ua_list': ua_list,
      'visitor_counter': visitor_counter,
    }
    self.generate('../templates/admin.html', template_values)
    
  def post(self):
    name = urllib.quote(self.request.get('name').encode('utf8'))
    category = Category.all().filter('name',name).get()
    if category is not None:
      self.response.out.write('category: %s has already existed' % (name))
    else:
      category = Category()
      category.name = name
      category.put()
      categories = Category.all()
      template_values = {
        'categories': categories,
      }
      self.generate('../templates/admin.html', template_values)