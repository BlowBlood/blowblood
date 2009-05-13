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

class main(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), '../templates/upload.html')
    self.response.out.write(template.render(path, template_values))
    
  def post(self):
    filename = self.request.get('imgfile')
    file_handle = StringIO.StringIO(filename) #convert string to file-like object
    gd_client = gdata.photos.service.PhotosService()
    gd_client.email = 'gzguoer@gmail.com'
    gd_client.password = bbpsw.getpassword()
    gd_client.source = 'blowblood-upload-image'
    gd_client.ProgrammaticLogin()    
    album_url = '/data/feed/api/user/gzguoer/albumid/5334765855583692065'
    photo = gd_client.InsertPhotoSimple(album_url, 'New Photo','Uploaded using the API', file_handle, content_type='image/jpeg')
    self.response.out.write("Upload completed")