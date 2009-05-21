from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from app import m

def main():
  application = webapp.WSGIApplication(
                                     [('/', m.MainPage),
                                     ],
                                     debug=True)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()