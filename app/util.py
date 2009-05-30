import os, re, sys
import logging
# import code for encoding urls and generating md5 hashes
import urllib, hashlib

from google.appengine.api import urlfetch, users, memcache

from model import Post, Category, Comment, Tag, Archive, Counter
PAGESIZE = 8
def getUserNickname(user):
    default = "anonymous"
    if user:
        return user.email().split("@")[0]
    else:
        return default        

def xhtmlize_url(url):
    return re.sub(r'&',r'&amp;',url)

def u(s, encoding):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, encoding)

def getPublicPosts(page):
  posts = memcache.get("public_posts")
  if posts is not None:
    start_ = (page - 1) * PAGESIZE
    end_ = start_ + PAGESIZE + 1
    return posts[start_:end_]
  else:
    posts_ = Post.all().filter('private', False).order('-date')
    posts = [x for x in posts_]
    if not memcache.add("public_posts", posts, 3600):
      logging.error("Memcache set failed.")
    return posts    
  
def getPublicCategory(category):
  posts = Post.all().filter('catalog',category).filter('private',False).order('-date')
  return posts
    
def getPublicTag(tag):
  posts = Post.all().filter('tags',tag).filter('private',False).order('-date')
  return posts
    
def getPublicArchive(monthyear):
  posts = Post.all().filter('monthyear',monthyear).filter('private',False).order('-date')
  return posts
    
def getCategoryLists():
  key_ = "category_lists"
  categories = memcache.get(key_)
  if categories is not None:
    return categories
  else:
    categories_ = Category.all()
    categories = [x for x in categories_]
    if not memcache.add(key_, categories, 3600):
      logging.error("Memcache set failed.")
    return categories

def getTagLists():
  key_ = "tag_lists"
  tags = memcache.get(key_)
  if tags is not None:
    return tags
  else:
    tags_ = Tag.all()
    tags = [x for x in tags_]
    if not memcache.add(key_, tags, 3600):
      logging.error("Memcache set failed.")
    return tags
  
def getArchiveLists():
  key_ = "archive_lists"
  archives = memcache.get(key_)
  if archives is not None:
    return archives
  else:
    archives_ = Archive.all().order("-date")
    archives = [x for x in archives_]
    if not memcache.add(key_, archives, 3600):
      logging.error("Memcache set failed.")
    return archives
    
def getRecentComment():
  key_ = "recent_comments"
  comms = memcache.get(key_)
  if comms is not None:
    return comms
  else:
    comms = Comment.all().order('-date').fetch(8)
    for comm in comms:
      comm.content = re.sub(u'<[^>]*?>','',comm.content)[:50]
    if not memcache.add(key_, comms, 3600):
      logging.error("Memcache set failed.")
    return comms
    
def flushPublicPosts():
  memcache.delete("public_posts")

def flushCategoryLists():
  key_ = "category_lists"
  memcache.delete(key_)

def flushTagLists():
  key_ = "tag_lists"
  memcache.delete(key_)

def flushArchiveLists(): 
  key_ = "archive_lists" 
  memcache.delete(key_)
      
def flushRecentComment():
  key_ = "recent_comments"
  memcache.delete(key_)
  
def flushAll():
  memcache.flush_all()
  
def invalidreg(emailkey):
  """Email validation, checks for syntactically invalid email
  courtesy of Mark Nenadov.
  See
  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65215"""
  import re
  emailregex ="^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$"
  if len(emailkey) > 5:
    if re.match(emailregex, emailkey) != None:
      return True
  return False

def getGravatarUrl(email):
  # Set your variables here  
  default = "http://www.blowblood.com/static/images/unkown.jpg"
  if not invalidreg(email):
    return default  
  return '/rpc?action=get_gravatar&amp;'+urllib.urlencode({'id':hashlib.md5(email).hexdigest()})
  
def getFontSizeFromHot(num):
  num = int(num)
  if num<5:
    return 100
  if num<10:
    return 130
  if num<20:
    return 160
  if num<40:
    return 190
  if num<80:
    return 210
  if num<160:
    return 240
  if num<320:
    return 270
  if num<640:
    return 300
  if num<1280:
    return 330
  return 360
  
def getCounter():
  counter = Counter.all().get()
  if counter is None:
    return 0    
  return counter.count