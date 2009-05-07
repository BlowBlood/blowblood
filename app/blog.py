import os
import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

from app import util
from model import Post

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
      
      
class MainPage(BaseRequestHandler):
  def get(self):      
    posts = Post.gql('ORDER BY date desc')
    template_values = {
      'posts': posts,
      }
    self.generate('../templates/view.html', template_values)
    
class AddPost(BaseRequestHandler):
  def get(self):
    if users.is_current_user_admin():
      template_values = {}      
      self.generate('../templates/add.html', template_values)
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
      permalink = maxpermalinkBlog.permalink+ post.date.strftime('-%Y-%m-%d')
    post.permalink =  permalink
    post.save()    
    self.redirect(post.full_permalink())    
    
class DeletePost(BaseRequestHandler):
  def get(self,PostID):
    if users.is_current_user_admin():
      post = Post.get_by_id(int(PostID))
      template_values = {
        'post': post,
      }
      self.generate('../templates/delete.html', template_values)
    else:
      self.redirect("/403.html")
    
  def post(self,PostID):
    post= Post.get_by_id(int(PostID))
    if(post is not None):
        post.delete()                
    self.redirect('/')
   
class EditPost(BaseRequestHandler):
  def get(self,PostID):
    if users.is_current_user_admin():
      post = Post.get_by_id(int(PostID))
      tags_commas = post.tags_commas
      template_values = {
        'post': post,
        'tags_commas': tags_commas,
      }
      self.generate('../templates/edit.html', template_values)
    else:
      self.redirect("/403.html")
    
  def post(self,PostID):
    post= Post.get_by_id(int(PostID))
    if(post is None):
      self.redirect('/')    
    post.title = self.request.get('title_input')    
    post.tags_commas = self.request.get('tags')
    post.content = self.request.get('content')
    post.catalog = self.request.get('blogcatalog')
    private = self.request.get('private')    
    if private:
      post.private = True;
    else:      
      post.private = False;        
    post.lastModifiedDate = datetime.datetime.now()
    post.lastModifiedBy = users.get_current_user()        
    post.update()
    self.redirect(post.full_permalink())
    
class PostView(BaseRequestHandler):
  def get(self,year,month,perm_stem): 
    post = db.Query(Post).filter('permalink =',perm_stem).get()
    if(post is None):
      self.redirect('/')
    else:
      template_values = {
        'post': post,            
      }
      self.generate('../templates/post.html', template_values)
    
class CatalogHandler(BaseRequestHandler):
  def get(self,catalog_name):
    posts = Post.gql('where catalog =:1 ORDER BY date desc',catalog_name)
    if(posts is None):
      self.redirect('/')
    else:
      template_values = {
        'posts': posts,            
      }
      self.generate('../templates/view.html', template_values)   
    
class TagHandler(BaseRequestHandler):
  def get(self,tag):
    posts = Post.all().filter('tags', tag).order('-date')
    if(posts is None):
      self.redirect('/')
    else:
      template_values = {
        'posts': posts,            
      }
      self.generate('../templates/view.html', template_values)
      
class PrintEnvironmentHandler(webapp.RequestHandler):
  def get(self):
    for name in os.environ.keys():
      self.response.out.write("%s = %s<br />\n" % (name, os.environ[name]))
      
class FeedHandler(webapp.RequestHandler):
  def get(self):
    posts = Post.all().order('-date').fetch(50)
    last_update = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    template_values = {
      'posts':posts,
      'last_update': last_update,
    }
    path = os.path.join(os.path.dirname(__file__), '../templates/atom.xml')
    self.response.out.write(template.render(path, template_values))   
   