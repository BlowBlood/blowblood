import os, urllib, re

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

class MainPage(webapp.RequestHandler):
  def get(self):    
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    word = self.request.get('word')
    result = urllib.urlopen(word).read()
    template_values = {
      'result': result,
    }
    path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
    self.response.out.write(template.render(path, template_values))