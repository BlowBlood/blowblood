# !/usr/bin/env python
import re
from google.appengine.ext import webapp
from datetime import timedelta

import urllib
import re
import cgi
from app import util

register = webapp.template.create_template_register()

@register.filter
def replace ( string, args ):
        search  = args[0]
        replace = args[1]
        return re.sub( search, replace, string )

@register.filter
def email_username ( email ):
        return email.split("@")[0]

@register.filter
def unquote ( str ):
        return urllib.unquote(str.encode('utf8'))

@register.filter
def quote ( str ):
        return urllib.quote(str)

@register.filter
def escape ( str ):
        return cgi.escape(str)

@register.filter
def timezone(value, offset):
    return value + timedelta(hours=offset)

@register.filter
def space2dollar(str):
    return str.replace(' ','$')
    
@register.filter
def gravatar(email):
    #return util.getGravatarUrl(email)
    return '/rpc?action=get_gravatar&amp;email='+email

@register.filter
def hot2fsize(num):
  return util.getFontSizeFromHot(num)