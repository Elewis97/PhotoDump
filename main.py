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
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

class PhotoGroup(ndb.Model):
    group_name = ndb.StringProperty(required=True)
    is_group_public = ndb.BooleanProperty(required=False, default=False)
    created_by = ndb.UserProperty(auto_current_user_add=True)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    photo_links = ndb.StringProperty(repeated=True)

class Photo(ndb.Model):
    name = ndb.StringProperty(required=False)
    caption = ndb.StringProperty(required=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    uploaded_by = ndb.UserProperty(auto_current_user_add=True)
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    blob_key = ndb.BlobKeyProperty()
    #url = ndb.StringProperty(required=True)

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
        self.response.write(template.render())

class GroupfeedHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template('templates/groupfeed.html')
        query = PhotoGroup.query()
        photo_group_data = query.fetch()
        template_vars = {"photo_group_data" : photo_group_data}
        self.response.write(template.render())

#class ViewGroupHandler(webapp2.RequestHandler):
#    def get(self):


#This handler is needed in order to create a group.
#NEEDED FOR TESTING PURPOSES
class CreateGroupHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template('templates/creategroup.html')
        self.response.write(template.render())
    def post(self):
        template = jinja2_environment.get_template('templates/creategroup.html')
        name = self.request.get("group_name")
        type = self.request.get("type")
        type = True if type.lower() == "public" else False
        new_group = PhotoGroup(group_name = name, is_group_public=type)
        new_group.put()
        logging.info(self.request)
        self.redirect("/success")

# Tells the user when they successfully create a group.
class SuccessHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template('templates/success.html')
        self.response.write(template.render())

#THIS HANDLER IS FOR KIET TO TEST STUFF
class TestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(images.get_serving_url("2kBDZ5Z2bSes-oP1J6uK0w=="))

#This is the upload handler it deals with uploading photos.
#The photo will be uploaded to imgur using the imgur upload API
#The imgur API will then return a link and the link will be stored in a Photo class
class UploadHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2_environment.get_template("templates/upload.html")
        upload_url = blobstore.create_upload_url('/uploaded')
        template_vars = { "upload_url" : upload_url}
        self.response.write(template.render(template_vars))

class FinishedUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            #a = self.request.get("my_file")
            upload = self.get_uploads()[0]
            photo = Photo(blob_key=upload.key())
            photo.put()
            self.redirect('/view_photo/%s' % upload.key())
            self.response.write("success")
        except:
            self.response.write("failure")

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

jinja2_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/newsfeed', NewsfeedHandler),
    ('/groupfeed', GroupfeedHandler),
    ('/upload', UploadHandler),
    ('/uploaded', FinishedUploadHandler),
    ('/view_photo/([^/]+)', ViewPhotoHandler),
    ('/test', TestHandler),
    ('/create_group', CreateGroupHandler),
    ('/success', SuccessHandler)
], debug=True)
