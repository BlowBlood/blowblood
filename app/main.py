from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from app import blog

from google.appengine.ext.webapp import template
template.register_template_library('app.filter')

def main():
  application = webapp.WSGIApplication(
                                     [('/', blog.MainPage),
                                      ('/add', blog.AddPost),
                                      ('/([12]\d\d\d)/(\d|[01]\d)/([-\w]+)/*$', blog.PostView),
                                      ('/e',blog.PrintEnvironmentHandler),
                                      ('/403.html', blog.UnauthorizedHandler),
                                      ('/404.html', blog.NotFoundHandler),
                                      ('/(.*)', blog.ExceptionHander),
                                     ],
                                     debug=True)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()