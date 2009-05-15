import os
import StringIO
import bbpsw
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import gdata.photos.service
import gdata.media
import gdata.geo
import gdata.urlfetch
gdata.service.http_request_handler = gdata.urlfetch #override original http handler

from app import util, authorized

class main(webapp.RequestHandler):
  @authorized.role("admin")
  def get(self):
    self.redirect('404.html')
  
  @authorized.role("admin")
  def post(self):
    filename = self.request.get('imgfile')
    filetitle = self.request.get('imgtitle')
    file_handle = StringIO.StringIO(filename) #convert string to file-like object
    gd_client = gdata.photos.service.PhotosService()
    gd_client.email = 'gzguoer@gmail.com'
    gd_client.password = bbpsw.getpassword()
    gd_client.source = 'blowblood-upload-image'
    gd_client.ProgrammaticLogin()    
    album_url = '/data/feed/api/user/gzguoer/albumid/5334765855583692065'
    try:
      photo = gd_client.InsertPhotoSimple(album_url, 'blogimg',filetitle, file_handle, content_type='image/jpeg')      
      img_url = photo.GetMediaURL()+"?imgmax=512"
      self.response.out.write('<script type="text/javascript">window.parent.rteGetImage("%s")</script>' % img_url)
    except gdata.service.RequestError:
      self.response.out.write(GooglePhotosException)
