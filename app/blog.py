import os
import re
import urllib
import datetime
import calendar

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

from app import util, authorized
from model import Post

PAGESIZE = 8

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
    today = '<b id="today">'+ym[2]+'</b>'
    cal = re.sub(ym[2],today,cal)
    values = {
      'user': users.GetCurrentUser(),
      'user_is_admin': users.is_current_user_admin(),
      'user_nickname': util.getUserNickname(users.get_current_user()),
      'url': url,
      'url_linktext': url_linktext,
      'categories': util.getCategoryLists(),
      'calendar': cal,
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
    if users.is_current_user_admin():
      posts = Post.all().order('-date').fetch(PAGESIZE+1)
    else:
      posts = util.getPublicPosts().fetch(PAGESIZE+1)
    polder = None
    if len(posts) == PAGESIZE+1:
      polder = '2'
      posts = posts[:PAGESIZE]
    template_values = {
      'posts': posts,
      'page': '1',
      'count': len(posts),
      'polder': polder,      
      }
    self.generate('../templates/view.html', template_values)
    
class PageHandler(BaseRequestHandler):
  def get(self,page_num):
    try:
      page = int(page_num)
    except Error:
      raise Error('page_num_is_invalid')
    if page == 1:
      self.redirect('/')
    if users.is_current_user_admin():
      posts = Post.all().order('-date').fetch(PAGESIZE + 1, (page - 1) * PAGESIZE)
    else:
      posts = util.getPublicPosts().fetch(PAGESIZE + 1, (page - 1) * PAGESIZE)
    polder = None
    if len(posts) == PAGESIZE+1:
      polder = page + 1
      posts = posts[:PAGESIZE]
    pnewer = page - 1
    template_values = {
      'posts': posts,
      'page': page,
      'count': len(posts),
      'pnewer': pnewer,
      'polder': polder,
      }
    self.generate('../templates/view.html', template_values)
    
class AddPost(BaseRequestHandler): 
  @authorized.role("admin") 
  def get(self):    
    template_values = {}      
    self.generate('../templates/add.html', template_values)    
  
  @authorized.role("admin")
  def post(self):
    post = Post()
    post.title = self.request.get('title_input')
    post.content = self.request.get('content')
    post.tags_commas = self.request.get('tags')
    user = users.get_current_user()
    post.author = user
    post.catalog = urllib.quote(self.request.get('blogcatalog').encode('utf8'))
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
    util.flushCategoryLists()
    self.redirect(post.full_permalink())    
    
class DeletePost(BaseRequestHandler):
  @authorized.role("admin")
  def get(self,PostID):
    post = Post.get_by_id(int(PostID))
    template_values = {
      'post': post,
    }
    self.generate('../templates/delete.html', template_values)
  
  @authorized.role("admin")  
  def post(self,PostID):
    post= Post.get_by_id(int(PostID))
    if(post is not None):
        post.delete()
        util.flushCategoryLists()
    self.redirect('/')
   
class EditPost(BaseRequestHandler):
  @authorized.role("admin")
  def get(self,PostID):
    post = Post.get_by_id(int(PostID))
    tags_commas = post.tags_commas
    template_values = {
      'post': post,
      'tags_commas': tags_commas,
    }
    self.generate('../templates/edit.html', template_values)    
  
  @authorized.role("admin")  
  def post(self,PostID):
    post= Post.get_by_id(int(PostID))
    if(post is None):
      self.redirect('/')    
    post.title = self.request.get('title_input')    
    post.tags_commas = self.request.get('tags')
    post.content = self.request.get('content')
    post.catalog = urllib.quote(self.request.get('blogcatalog').encode('utf8'))
    private = self.request.get('private')    
    if private:
      post.private = True;
    else:      
      post.private = False;        
    post.lastModifiedDate = datetime.datetime.now()
    post.lastModifiedBy = users.get_current_user()        
    post.update()
    util.flushCategoryLists()
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
  def get(self,category):
    if users.is_current_user_admin():
      posts = Post.gql('where catalog =:1 ORDER BY date desc',category)
    else:
      posts = util.getPublicCategory(category) #only cahced public items
    if(posts is None):
      self.redirect('/')
    else:
      template_values = {
        'posts': posts,
      }
      self.generate('../templates/view.html', template_values)
    
class TagHandler(BaseRequestHandler):
  def get(self,tag):
    if users.is_current_user_admin():
      posts = Post.all().filter('tags', tag).order('-date')
    else:
      posts = util.getPublicTag(tag) #only cahced public items
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
    posts = Post.all().filter('private', False).order('-date').fetch(50)#only output public items
    last_updated = datetime.datetime.now()
    if posts and posts[0]:
      last_updated = posts[0].date    
    last_updated_time = last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
    for post in posts:
      post.formatted_date= post.date.strftime("%Y-%m-%dT%H:%M:%SZ")
    template_values = {
      'posts':posts,
      'last_updated': last_updated_time,
    }
    path = os.path.join(os.path.dirname(__file__), '../templates/atom.xml')
    self.response.headers['Content-Type'] = 'application/atom+xml'
    self.response.out.write(template.render(path, template_values))   
   