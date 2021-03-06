#Authorized file, including authSub and role authorization

from google.appengine.api import users

def role(role):
    """This method refer to the Bloog (http://bloog.appspot.com).

    A decorator to enforce user roles, currently 'user' (logged in) and 'admin'.

    To use it, decorate your handler methods like this:

    import authorized
    @authorized.role("admin")
    def get(self):
      user = users.GetCurrentUser(self)
      self.response.out.write('Hello, ' + user.nickname())

    If this decorator is applied to a GET handler, we check if the user is logged in and
    redirect her to the create_login_url() if not.

    For HTTP verbs other than GET, we cannot do redirects to the login url because the
    return redirects are done as GETs (not the original HTTP verb for the handler).  
    So if the user is not logged in, we return an error.
    """
    def wrapper(handler_method):
        def check_login(self, *args, **kwargs):
            user = users.get_current_user()
            if not user:
                if self.request.method != 'GET':
                    self.error(403)
                else:
                    self.redirect(users.create_login_url(self.request.uri))
            elif role == "user" or (role == "admin" and users.is_current_user_admin()):
                return handler_method(self, *args, **kwargs)
            else:
                if self.request.method == 'GET':
                    self.redirect("/403.html")  # Some unauthorized feedback
                else:
                    self.error(403) # User didn't meet role.  
        return check_login
    return wrapper