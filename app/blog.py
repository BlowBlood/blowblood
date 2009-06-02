import os
import re
import urllib
import datetime
import calendar
import Cookie
import sys
from datetime import timedelta

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

from app import util, authorized, log
from model import Post, Comment

PAGESIZE = 8

class BaseRequestHandler(webapp.RequestHandler):
  """Supplies a common template generation function.

  When you call generate(), we augment the template variables supplied with
  the current user in the 'user' variable and the current webapp request
  in the 'request' variable.
  """
  @log.visitor
  def generate(self, template_name, template_values={}):
    if users.get_current_user():
      log_url = util.xhtmlize_url(users.create_logout_url(self.request.uri))
      url_linktext = 'Logout'
    else:
      log_url = util.xhtmlize_url(users.create_login_url(self.request.uri))
      url_linktext = 'Login'
    ym = datetime.datetime.now().strftime("%Y %m %d").split()
    cal = calendar.HTMLCalendar().formatmonth(int(ym[0]),int(ym[1]))
    ym[2] = ym[2][1:] if ym[2][0] == '0' else ym[2]   # truncate leadding '0' if ym[2] < '10'
    pattern = '<td class="\w\w\w">'+ym[2]+'</td>'
    today = '<td id="today">'+ym[2]+'</td>'    
    cal = re.sub(pattern,today,cal)
    values = {
      'user': users.GetCurrentUser(),
      'user_is_admin': users.is_current_user_admin(),
      'user_nickname': util.getUserNickname(users.get_current_user()),
      'log_url': log_url,
      'url_linktext': url_linktext,
      'categories': util.getCategoryLists(),
      'calendar': cal,
      'recentcoms': util.getRecentComment(),
      'tags': util.getTagLists(),
      'archives': util.getArchiveLists(),
      'counter': util.getCounter(),
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
  @log.counter
  def get(self):
    if users.is_current_user_admin():
      posts = Post.all().order('-date').fetch(PAGESIZE+1)
    else:
      posts = util.getPublicPosts(1)
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
  @log.counter
  def get(self,page_num):
    try:
      page = int(page_num)
    except Error:
      raise Error('page_num_is_invalid')
    if page == 1:
      return self.redirect('/')
    if users.is_current_user_admin():
      posts = Post.all().order('-date').fetch(PAGESIZE + 1, (page - 1) * PAGESIZE)
    else:
      posts = util.getPublicPosts(page)
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
    post.catalog = self.request.get('blogcatalog')
    private = self.request.get('private')
    if private:
      post.private = True;
    else:      
      post.private = False;        
    #try:     #no need this ugly permalink now!
    #  permalink =  util.get_permalink(post.date,util.translate('zh-CN','en', util.u(post.title,'utf-8')))
    #  if not permalink:
    #    raise Exception
    #except Exception: 
    #  self.response.out.write("transalte error in title %s = %s<br />\n" % (post.title,util.get_permalink(post.date,util.translate('zh-CN','en', util.u(post.title,'utf-8')))))
    #  return
    #check the permalink duplication problem.
    #maxpermalinkBlog = db.GqlQuery("select * from Post where permalink >= :1 and permalink < :2 order by permalink desc",permalink, permalink+u"\xEF\xBF\xBD").get()
    #if maxpermalinkBlog is not None:
    #  permalink = maxpermalinkBlog.permalink+ post.date.strftime('-%Y-%m-%d')
    #post.permalink =  permalink
    post.save()    
    util.flushCategoryLists()
    util.flushArchiveLists()
    util.flushTagLists()
    util.flushPublicPosts()
    return self.redirect(post.full_permalink())    
    
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
      post.clear_tags()
      post.clear_archive()
      post.clear_category()
      comments = post.comment_set
      for comment in comments:
        comment.delete()
      post.delete()
      util.flushRecentComment()
      util.flushCategoryLists()
      util.flushArchiveLists()
      util.flushTagLists()
    return self.redirect('/')
   
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
      return self.redirect('/')    
    post.title = self.request.get('title_input') 
    post.clear_tags()   
    post.tags_commas = self.request.get('tags')
    post.content = self.request.get('content')
    post.clear_category()
    post.catalog = self.request.get('blogcatalog')
    private = self.request.get('private')    
    if private:
      post.private = True;
    else:      
      post.private = False;        
    post.lastModifiedDate = datetime.datetime.now()
    post.lastModifiedBy = users.get_current_user()        
    post.update()
    util.flushCategoryLists()
    util.flushTagLists()
    return self.redirect(post.full_permalink())
    
class AddComment(BaseRequestHandler):
  def post(self):
    post_id_ = self.request.get('post_id')
    post = Post.get_by_id(int(post_id_))
    if post is None:
      return self.redirect('/')
    comment = Comment()
    comment.post = post
    comment.author = self.request.get('comm_name')
    if users.is_current_user_admin():
      comment.author_is_admin = True
    comment.authorEmail = self.request.get('comm_email')
    comment.authorWebsite = self.request.get('comm_url')
    comment.content = self.request.get('comment')
    comment.userIp = self.request.remote_addr
    user = users.get_current_user()
    if user is not None:
      comment.user = user
      comment.author = str(user.nickname())
      comment.authorEmail = str(user.email()) 
    cookies = Cookie.SimpleCookie()
    cookies['comm_name'] = urllib.quote(comment.author.encode('utf8')) 
    cookies['comm_name']['path'] = '/'
    cookies['comm_name']['max-age'] = 3600*24*365
    cookies['comm_email'] = comment.authorEmail  
    cookies['comm_email']['path'] = '/'
    cookies['comm_email']['max-age'] = 3600*24*365
    cookies['comm_url'] = comment.authorWebsite 
    cookies['comm_url']['path'] = '/'
    cookies['comm_url']['max-age'] = 3600*24*365
    output_headers = []
    output_headers.append('%s\r\n' % cookies)
    for header in output_headers:
      sys.stdout.write(header)         
    comment.save()
    util.flushRecentComment()
    return self.redirect(post.full_permalink())

class OPostView(BaseRequestHandler):
  @log.counter
  def get(self,year,month,perm_stem): 
    post = db.Query(Post).filter('permalink =',perm_stem).get()
    if(post is None):
      return self.redirect('/')
    url = ""
    if users.is_current_user_admin():
      url = "www.blowblood.com"
      prevp = db.GqlQuery("select * from Post where date > :1 order by date limit 1",post.date).get()
      nextp = db.GqlQuery("select * from Post where date < :1 order by date desc limit 1",post.date).get()
    else:
      post.hitcount += 1
      post.put()
      prevp = db.GqlQuery("select * from Post where date > :1 and private = False order by date limit 1",post.date).get()
      nextp = db.GqlQuery("select * from Post where date < :1 and private = False order by date desc limit 1",post.date).get()
    template_values = {
      'post': post,            
      'comments': sorted(post.comment_set, key = lambda comm:comm.date, reverse = True),
      'comm_url': url,
      'comm_email': os.environ['USER_EMAIL'],
      'comm_name': util.getUserNickname(os.environ['USER_EMAIL']),
      'prevp': prevp,
      'nextp': nextp,
    }
    self.generate('../templates/post.html', template_values)
        
class PostView(BaseRequestHandler):
  @log.counter
  def get(self,post_id): 
    post_id_ = int(post_id)
    post = Post.get_by_id(post_id_)    
    if post == None:
      return self.redirect('/');
    comm_name = 'anonymous'
    comm_email = ''
    comm_url = ''
    if users.is_current_user_admin():
      prevp = db.GqlQuery("select * from Post where date > :1 order by date limit 1",post.date).get()
      nextp = db.GqlQuery("select * from Post where date < :1 order by date desc limit 1",post.date).get()      
      comm_email = os.environ['USER_EMAIL']
      comm_name = comm_email.split("@")[0]
      comm_url = "www.blowblood.com"
    else:
      post.hitcount += 1
      post.put()
      prevp = db.GqlQuery("select * from Post where date > :1 and private = False order by date limit 1",post.date).get()
      nextp = db.GqlQuery("select * from Post where date < :1 and private = False order by date desc limit 1",post.date).get()
      cookies = os.environ.get('HTTP_COOKIE', None)
      if cookies is not None:
        user_cookie = Cookie.SimpleCookie()
        user_cookie.load(cookies)
        try:
          comm_name = user_cookie['comm_name'].value
          if comm_name:
            comm_name = urllib.unquote(comm_name.encode('utf8'))
          comm_email = user_cookie['comm_email'].value
          comm_url = user_cookie['comm_url'].value
        except KeyError:
          pass        
    template_values = {
      'post': post,            
      'comments': sorted(post.comment_set, key = lambda comm:comm.date, reverse = True),
      'comm_name': comm_name,
      'comm_email': comm_email,
      'comm_url': comm_url,
      'prevp': prevp,
      'nextp': nextp,
    }
    self.generate('../templates/post.html', template_values)
    
class CatalogHandler(BaseRequestHandler):
  def get(self,category):
    if users.is_current_user_admin():
      posts = Post.gql('where catalog =:1 ORDER BY date desc',category)
    else:
      posts = util.getPublicCategory(category) #only cahced public items
    if(posts is None):
      return self.redirect('/')
    else:
      template_values = {
        'posts': posts,
      }
      self.generate('../templates/view.html', template_values)

class ArchiveHandler(BaseRequestHandler):
  def get(self,year,month):
    if year is None:
      return self.redirect('/')
    if month is None:
      return self.redirect('/')
    my = year + "/" + month    
    if users.is_current_user_admin():
      posts = Post.gql('where monthyear =:1 ORDER BY date desc',my)
    else:
      posts = util.getPublicArchive(my)  #only cahced public items
    if(posts is None):
      return self.redirect('/')
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
      return self.redirect('/')
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
   