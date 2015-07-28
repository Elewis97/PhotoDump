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

class PhotoGroup(ndb.Model):
    group_name = ndb.StringProperty(required=True)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    is_group_public = ndb.BooleanProperty(required=False, default=False)
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
        self.response.write('Hello world!')
        self.response.write(template.render())

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
        upload_stuff = self.get_uploads()
        logging.info("UPLOAD!!! " + str(upload_stuff))
        try:
            #a = self.request.get("my_file")
            upload = upload_stuff[0]
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
    ('/view_photo/([^/]+)', ViewPhotoHandler)
], debug=True)
