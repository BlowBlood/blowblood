import os
import re
import sys
import urllib
import logging

from google.appengine.api import urlfetch, users, memcache

from app.BeautifulSoup import BeautifulSoup

from model import Post

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
  
def getPublicCatagory(catagory):
  key_ = "catagory_" + catagory
  posts = memcache.get(key_)
  if posts is not None:
    return posts
  else:
    posts = Post.all().filter('catalog',catagory).filter('private',False).order('-date')
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

def flushPublicPosts():
  memcache.delete("public_posts")
  
def flushPublicPublicCatagory(catagory):
  key_ = "catagory_" + catagory
  memcache.delete(key_)
  
def flushPublicPublicTag(tag):
  key_ = "catagory_" + tag
  memcache.delete(key_)