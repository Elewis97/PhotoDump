#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import logging
import json
from google.appengine.ext import ndb
from google.appengine.ext import vendor
from google.appengine.api import users

# This line adds the imgur API library to the project
# vendor.add('lib')

class PhotoGroup(ndb.Model):
    group_name = ndb.StringProperty(required=True)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    is_group_public = ndb.BooleanProperty(required=False, default=False)
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    photo_links = ndb.StringProperty(repeated=True)

class Photo(ndb.Model):
    caption = ndb.StringProperty(required=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    uploaded_by = ndb.StringProperty()
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    url = ndb.StringProperty(required=True)


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        # this is the login section
        logging.info("WELCOME HANDLER ENTERED")
        user = users.get_current_user()
        if user:
            greeting = ('Hey, %s! (<a href="%s">sign out</a>)' %
                (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/newsfeed'))
        # this renders the template welcome.html
        template = jinja2_environment.get_template('templates/welcome.html')
        self.response.write(template.render(greeting=greeting))



class NewsfeedHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template('templates/newsfeed.html')
        self.response.write('Hello world!')
        self.response.write(template.render())

class GroupfeedHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template('templates/groupfeed.html')
        self.response.write('Hello world!')
        self.response.write(template.render())

#This is the upload handler it deals with uploading photos.
#The photo will be uploaded to imgur using the imgur upload API
#The imgur API will then return a link and the link will be stored in a Photo class
class UploadHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template("templates/upload.html")
        self.response.write("Hello world")

jinja2_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/newsfeed', NewsfeedHandler),
    ('/groupfeed', GroupfeedHandler),
    ('/upload', UploadHandler)
], debug=True)
