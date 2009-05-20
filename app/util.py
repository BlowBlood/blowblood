import os, re, sys
import logging
# import code for encoding urls and generating md5 hashes
import urllib, hashlib

from google.appengine.api import urlfetch, users, memcache

from app.BeautifulSoup import BeautifulSoup

from model import Post, Category, Comment, Tag

def getUserNickname(user):
    default = "anonymous"
    if user:
        return user.email().split("@")[0]
    else:
        return default        
        
def get_permalink(date,title):
    return get_friendly_url(title)

def get_friendly_url(title):
    return re.sub('-+', '-', re.sub('[^\w-]', '', re.sub('\s+', '-', removepunctuation(title).strip()))).lower()
    
def xhtmlize_url(url):
    return re.sub(r'&',r'&amp;',url)
    
def removepunctuation(str):
    punctuation = re.compile(r'[.?!,":;]')
    str = punctuation.sub("", str)
    return str
    
def u(s, encoding):
    if isinstance(s, unicode):
        return s
    else:
        return unicode(s, encoding)
        
def translate(sl, tl, text):
    assert type(text) == type(u''), "Expects input to be unicode."
    # Do a POST to google
    # I suspect "ie" to be Input Encoding.
    # I have no idea what "hl" is.
    translated_page = urlfetch.fetch(
        url="http://translate.google.com/translate_t?" + urllib.urlencode({'sl': sl, 'tl': tl}),
        payload=urllib.urlencode({'hl': 'en',
                               'ie': 'UTF8',
                               'text': text.encode('utf-8'),
                               'sl': sl, 'tl': tl}),
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if translated_page.status_code == 200:
        translated_soup = BeautifulSoup(translated_page.content)
        return translated_soup('div', id='result_box')[0].string
    else:
        return "ss"
        
def getPublicPosts():
  posts = memcache.get("public_posts")
  if posts is not None:
    return posts
  else:
    posts = Post.all().filter('private', False).order('-date')
    if not memcache.add("public_posts", posts, 3600):
      logging.error("Memcache set failed.")
    return posts    
  
def getPublicCategory(category):
  key_ = "category_" + category
  posts = memcache.get(key_)
  if posts is not None:
    return posts
  else:
    posts = Post.all().filter('catalog',category).filter('private',False).order('-date')
    if not memcache.add(key_, posts, 3600):
      logging.error("Memcache set failed.")
    return posts
    
def getPublicTag(tag):
  key_ = "tag_" + tag
  posts = memcache.get(key_)
  if posts is not None:
    return posts
  else:
    posts = Post.all().filter('tags',tag).filter('private',False).order('-date')
    if not memcache.add(key_, posts, 3600):
      logging.error("Memcache set failed.")
    return posts

def getCategoryLists():
  key_ = "category_lists"
  categories = memcache.get(key_)
  if categories is not None:
    return categories
  else:
    categories = Category.all()
    for category in categories:
      category.num = Post.all().filter('catalog',urllib.quote(category.name.encode('utf8'))).count()
      category.put()
    categories = Category.all()
    if not memcache.add(key_, categories, 3600):
      logging.error("Memcache set failed.")
    return categories

def getTagLists():
  key_ = "tag_lists"
  tags = memcache.get(key_)
  if tags is not None:
    return tags
  else:
    tags = Tag.all()
    if not memcache.add(key_, tags, 3600):
      logging.error("Memcache set failed.")
    return tags
    
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
  
def flushPublicPublicCategory(category):
  key_ = "category_" + category
  memcache.delete(key_)
  
def flushPublicPublicTag(tag):
  key_ = "tag_" + tag
  memcache.delete(key_)
  
def flushCategoryLists():
  key_ = "category_lists"
  memcache.delete(key_)

def flushTagLists():
  key_ = "tag_lists"
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
  size = 32
  # construct the url
  gravatar_url = "http://www.gravatar.com/avatar.php?"
  gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email).hexdigest(), 'default':default, 'size':str(size)})
  return xhtmlize_url(gravatar_url)
  
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