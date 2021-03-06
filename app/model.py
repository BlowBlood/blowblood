# This Python file uses the following encoding: utf-8
from google.appengine.ext import db
import urllib, re

class Post(db.Model):
    permalink = db.StringProperty()
    title = db.StringProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    author = db.UserProperty()
    catalog = db.StringProperty()
    private = db.BooleanProperty()    
    hitcount = db.IntegerProperty(default=0)
    commentcount = db.IntegerProperty(default=0)
    lastModifiedDate = db.DateTimeProperty()
    lastModifiedBy = db.UserProperty()
    tags = db.ListProperty(db.Category)
    monthyear = db.StringProperty(multiline=False)

    def full_permalink(self):        
        return '/post/' +  str(self.key().id())
        
    def get_tags(self):
        '''comma delimted list of tags'''
        return ','.join([urllib.unquote(tag.encode('utf8')) for tag in self.tags])
  
    def set_tags(self, tags):
        if tags:
            self.tags = [db.Category(urllib.quote(tag.strip().encode('utf8'))) for tag in re.split(',|，',tags)]
  
    tags_commas = property(get_tags,set_tags)

    def update_tags(self,update):
        """Update Tag cloud info"""
        if self.tags: 
            for tag_ in self.tags:
                tags = Tag.all().filter('name',tag_).fetch(10)
                if tags == []:
                    tagnew = Tag(name=tag_,num=1)
                    tagnew.put()
                else:
                    if not update:
                        tags[0].num+=1
                        tags[0].put()
    
    def clear_tags(self):
        """Clear all tags when edit blog or delete blog """
        if self.tags:
            for tag_ in self.tags:
                tags = Tag.all().filter('name',tag_).fetch(10)
                if tags != []:
                    tags[0].num -= 1
                    if tags[0].num == 0:
                        tags[0].delete()
                    else:
                        tags[0].put()
    
    def update_archive(self,update):
      """Add or Update archive of this post"""
      my = self.date.strftime('%Y/%m') # 2008/05
      self.monthyear = my
      archive = Archive.all().filter('monthyear',my).fetch(10)
      if archive == []:
        archive = Archive(monthyear = my, num = 1)
        archive.put()
      else:
        if not update:          
          archive[0].num += 1
          archive[0].put()      
    
    def clear_archive(self):
      archive = Archive.all().filter('monthyear',self.monthyear).fetch(10)
      if archive  != []:
        if archive[0].num == 1:
          archive[0].delete()
        else:
          archive[0].num -= 1
          archive[0].put()
          
    def update_category(self,update):
      """Add or Update archive of this post"""
      category = Category.all().filter('name',self.catalog).fetch(10)
      if category == []:
        category_ = Category(name = self.catalog, num = 1)
        category_.put()
      else:
        if not update:          
          category[0].num += 1
          category[0].put()      
    
    def clear_category(self):
      category = Category.all().filter('name',self.catalog).fetch(10)
      if category  != []:
        if category[0].num == 1:
          category[0].delete()
        else:
          category[0].num -= 1
          category[0].put()      
                        
    def save(self):
      self.update_tags(False)
      self.update_archive(False)
      self.update_category(False)
      self.put()
    
    def update(self):
      self.update_tags(False)
      self.update_category(False)
      self.put()

class Comment(db.Model):
  post = db.ReferenceProperty(Post)    
  date = db.DateTimeProperty(auto_now_add=True)
  user = db.UserProperty()
  author = db.StringProperty()
  author_is_admin = db.BooleanProperty()    
  authorEmail = db.EmailProperty()
  authorWebsite = db.StringProperty()
  userIp = db.StringProperty()
  content = db.TextProperty()
  
  def save(self):
    self.put()
    if self.post is not None:
      self.post.commentcount += 1
      self.post.put()

class Archive(db.Model):
  monthyear = db.StringProperty()
  num = db.IntegerProperty(default=0)
  date = db.DateTimeProperty(auto_now_add=True)
    
class Category(db.Model):
  name = db.StringProperty()
  num = db.IntegerProperty(default=0)

class Tag(db.Model):
  name = db.StringProperty()
  num = db.IntegerProperty(default=0)
    
class BBBlog(db.Model):
  title = db.StringProperty(multiline=False, default='BlowBlood')
  description = db.StringProperty(multiline=False,default='BlowBlood@WestGate')
  author = db.StringProperty(multiline=False, default='Your Blog Author')
  email = db.StringProperty(multiline=False, default='')  
  base_url = db.StringProperty(multiline=False,default='http://www.blowblood.com')  
  num_post_per_page = db.IntegerProperty(default=8)
  web_hit_count = db.IntegerProperty(default=0)
  
class Counter(db.Model):
  count = db.IntegerProperty(default=0)
  
class Visitor(db.Model):
  nickname = db.StringProperty(default="anonymous")
  userIP = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  url = db.StringProperty()
  webbrowser = db.StringProperty()
  referer = db.StringProperty()
  
class UserAgent(db.Model):
  name = db.StringProperty()
  count = db.IntegerProperty(default=0)
  date = db.DateTimeProperty(auto_now_add=True)