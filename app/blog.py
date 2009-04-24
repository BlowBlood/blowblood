import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

from app import util
from model import Post

class NotFoundHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('404!Not Found!')
   
class UnauthorizedHandler(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('403!Not Authorized') 
    
class ExceptionHander(webapp.RequestHandler):
  def get(self,suburl):
    self.response.out.write("Error, your requested /%s is Not found in this server!\n" % (suburl))
      
class MainPage(webapp.RequestHandler):
  def get(self):

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
    posts = Post.gql('ORDER BY date desc')

    template_values = {
      'posts': posts,
      'user': users.GetCurrentUser(),
      'user_is_admin': users.is_current_user_admin(),
      'user_nickname': util.getUserNickname(users.get_current_user()),
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), '../templates/view.html')    
    self.response.out.write(template.render(path, template_values))
    
class AddPost(webapp.RequestHandler):
  def get(self):
    if users.is_current_user_admin():
      template_values = {
        'user': users.GetCurrentUser(),
        'user_is_admin': users.is_current_user_admin(),
        'user_nickname': util.getUserNickname(users.get_current_user()),
        'url': users.create_logout_url(self.request.uri),
        'url_linktext': 'Logout',
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/add.html')    
      self.response.out.write(template.render(path, template_values))
    else:
      self.redirect("/403.html")
    
  def post(self):
    post = Post()
    post.title = self.request.get('title_input')
    post.content = self.request.get('content')
    post.tags_commas = self.request.get('tags')
    user = users.get_current_user()
    post.author = user
    post.catalog = self.request.get('blogcatalog')
    private = self.request.get('private')    
    if private:
      post.private = True;
    else:      
      post.private = False;        
    try:
      permalink =  util.get_permalink(post.date,util.translate('zh-CN','en', util.u(post.title,'utf-8')))
      if not permalink:
        raise Exception
    except Exception: 
      self.response.out.write("transalte error in title %s = %s<br />\n" % (post.title,util.get_permalink(post.date,util.translate('zh-CN','en', util.u(post.title,'utf-8')))))
      return
    #check the permalink duplication problem.
    maxpermalinkBlog = db.GqlQuery("select * from Post where permalink >= :1 and permalink < :2 order by permalink desc",permalink, permalink+u"\xEF\xBF\xBD").get()
    if maxpermalinkBlog is not None:
      permalink = maxpermalinkBlog.permalink+"1"
    post.permalink =  permalink
    post.save()    
    self.redirect(post.full_permalink())    
   
class PostView(webapp.RequestHandler):
  def get(self,year,month, perm_stem): 
    post = db.Query(Post).filter('permalink =',perm_stem).get()
    if(post is None):
      self.redirect('/')
    else:
      template_values = {
        'post': post, 
        'user': users.GetCurrentUser(),
        'user_is_admin': users.is_current_user_admin(),
        'user_nickname': util.getUserNickname(users.get_current_user()),
        'url': users.create_logout_url(self.request.uri),
        'url_linktext': 'Logout',       
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/post.html')    
      self.response.out.write(template.render(path, template_values))
    
class PrintEnvironmentHandler(webapp.RequestHandler):
  def get(self):
    for name in os.environ.keys():
      self.response.out.write("%s = %s<br />\n" % (name, os.environ[name]))
      
