import os

from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from app import util, authorized
from model import Post, Category

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
    values = {
      'user': users.GetCurrentUser(),
      'user_is_admin': users.is_current_user_admin(),
      'user_nickname': util.getUserNickname(users.get_current_user()),
      'url': url,
      'url_linktext': url_linktext,
    }    
    values.update(template_values)
    path = os.path.join(os.path.dirname(__file__), template_name)
    self.response.out.write(template.render(path, values))
    
class MainPage(BaseRequestHandler):
  @authorized.role("admin")  
  def get(self):
    categories = Category.all()
    template_values = {
      'categories': categories,
    }    
    self.generate('../templates/admin.html', template_values)
    
  def post(self):
    name = self.request.get('name')
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