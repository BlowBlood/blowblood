import os

from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from app import util
from model import Post

class MainPage(webapp.RequestHandler):
  def get(self):      
    if users.get_current_user():
      url = util.xhtmlize_url(users.create_logout_url(self.request.uri))
      url_linktext = 'Logout'
    else:
      url = util.xhtmlize_url(users.create_login_url(self.request.uri))
      url_linktext = 'Login'
    posts = Post.gql('ORDER BY date desc')
    post = None
    if posts and posts[0]:
      post=posts[0]
    values = {
      'user': users.GetCurrentUser(),
      'user_is_admin': users.is_current_user_admin(),
      'user_nickname': util.getUserNickname(users.get_current_user()),
      'url': url,
      'url_linktext': url_linktext,
      'post': post,
    }    
    path = os.path.join(os.path.dirname(__file__),'../templates/admin.html')
    self.response.out.write(template.render(path, values))