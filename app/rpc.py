from google.appengine.ext import webapp

class MainPage(webapp.RequestHandler):
  def get(self):
    action = self.request.get('action')
    if action:
      self.response.out.write('action = %s' % (action))
    else:
      self.response.out.write(' no action')