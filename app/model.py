from google.appengine.ext import db
import urllib

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
        return '/' + self.date.strftime('%Y/%m/')+ self.permalink
        
    def get_tags(self):
        '''comma delimted list of tags'''
        return ','.join([urllib.unquote(tag.encode('utf8')) for tag in self.tags])
  
    def set_tags(self, tags):
        if tags:
            self.tags = [db.Category(urllib.quote(tag.strip().encode('utf8'))) for tag in tags.split(',')]
  
    tags_commas = property(get_tags,set_tags)

    def save(self):
        my = self.date.strftime('%B %Y') # July 2008
        self.monthyear = my
        self.put()
    
    def update(self):
        self.put()

class Category(db.Model):
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