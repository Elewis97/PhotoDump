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
from google.appengine.api import search

class Photo(ndb.Model):
    name = ndb.StringProperty(required=False)
    caption = ndb.StringProperty(required=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    uploaded_by = ndb.UserProperty(auto_current_user_add=True)
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    blob_key = ndb.BlobKeyProperty()
    url = ndb.StringProperty(required=True)

class PhotoGroup(ndb.Model):
    group_name = ndb.StringProperty(required=True)
    is_group_public = ndb.BooleanProperty(required=False, default=False)
    created_by = ndb.UserProperty(auto_current_user_add=True)
    created_date = ndb.DateTimeProperty(auto_now_add=True)
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    photo_links = ndb.StringProperty(repeated=True)
    photos = ndb.StructuredProperty(Photo, repeated=True)
    description = ndb.StringProperty(required=False)

class User(ndb.Model):
    user = ndb.UserProperty()
    photo_group_keys = ndb.KeyProperty(repeated=True)

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
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        template = jinja2_environment.get_template('templates/welcome.html')
        self.response.write(template.render(greeting=greeting))

class NewsfeedHandler(webapp2.RequestHandler):
    def get(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        template = jinja2_environment.get_template('templates/newsfeed.html')

        # BACKEND: Looks through the user model to see if the current_user has
        # a model in datastore. If not, then create a User model for the current_user
        # and add it into datastore.
        current_user = get_user_model()
        logging.info(current_user)
        logging.info(current_user.user.nickname())
        greeting = "hello"
        template_vars = {"photo_group_data" : [], "greeting" : greeting}
        self.response.write(template.render(template_vars))

#This handler is needed in order to create a group.
#NEEDED FOR TESTING PURPOSES
class CreateGroupHandler(webapp2.RequestHandler):
    def post(self):
        template = jinja2_environment.get_template('templates/creategroup.html')
        name = self.request.get("group_name")
        type = self.request.get("type")
        description = self.request.get("description")
        type = True if type.lower() == "public" else False
        user = users.get_current_user()
        new_group = PhotoGroup(group_name = name, is_group_public=type, description=description)
        photo_group = new_group.put()
        logging.info(photo_group)
        current_user = users.get_current_user()
        user_list = User.query().fetch()
        for user in user_list:
            if user.user == current_user:
                logging.info("WENT IN HERE")
                user.photo_group_keys += [photo_group]
                user.put()
                break
        logging.info(self.request)
        self.redirect("/newsfeed")

class GroupSearchHandler(webapp2.RequestHandler):
    def get(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        query = PhotoGroup.query()
        search_term = self.request.get("searchBox")
        group_data = query.fetch()
        group_result = []
        for group in group_data:
            if group.group_name == search_term:
                group_result.append(group)

        #         self.response.write(group.group_name)
        #         self.response.write("<br/>")
        template_vars = {'group_result': group_result}
        template = jinja2_environment.get_template('templates/search.html')
        self.response.write(template.render(template_vars))

class ViewGroupHandler(webapp2.RequestHandler):
    def get(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        group_id = int(self.request.get("group_id"))
        group = PhotoGroup.get_by_id(group_id)
        template_vars = { "group" : group}
        template = jinja2_environment.get_template('templates/group.html')
        self.response.write(template.render(template_vars))


#This is the upload handler it deals with uploading photos.
#The photo will be uploaded to imgur using the imgur upload API
#The imgur API will then return a link and the link will be stored in a Photo class
class UploadHandler(webapp2.RequestHandler):
    def post(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        group_id = int(self.request.get("group_id"))
        group = PhotoGroup.get_by_id(group_id)
        template = jinja2_environment.get_template("templates/upload.html")
        upload_url = blobstore.create_upload_url('/uploaded')
        template_vars = { "upload_url" : upload_url, "group" : group}
        self.response.write(template.render(template_vars))

class FinishedUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            group_id = int(self.request.get("group_id"))
            group = PhotoGroup.get_by_id(group_id)
            logging.info("GROUP: " + group.group_name)
            upload_list = self.get_uploads()
            for upload in upload_list:
                blob_key = upload.key()
                serving_url = images.get_serving_url(blob_key)
                photo = Photo(blob_key=blob_key, url=serving_url)
                group.photos += [photo]
                group.put()
                logging.info("THIS WORKED RIGHT HERE")
            self.redirect("/newsfeed/view?group_id="+str(group_id))
        except:
            self.response.write("failure")

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)

#This handler lets me look at all the groups that have been stored
#in datastore. Used for debugging purposes.
class ViewAllGroupsHandler(webapp2.RequestHandler):
    def get(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        template = jinja2_environment.get_template('templates/groupfeed.html')
        query = PhotoGroup.query()
        photo_group_data = query.fetch()
        template_vars = {"photo_group_data" : photo_group_data} #PhotoGroup model list
        self.response.write(template.render(template_vars))

#THIS HANDLER IS FOR KIET TO TEST STUFF
class TestHandler(webapp2.RequestHandler):
    def get(self):
        user = User.get_by_id(6244676289953792)
        for photo_groups in user.photo_groups:
            self.response.write(photo_groups.group_name)
            self.response.write("</br>")
        #self.response.write(group.photos)
        #self.response.write("DISLIKES: " + str(group.dislikes))

def get_user_model():
    current_user = users.get_current_user()
    user_model_list = User.query().fetch()
    for temp_user_model in user_model_list:
        if temp_user_model.user == current_user:
            return temp_user_model
    new_user_model = User(user=current_user)
    new_user_model.put()
    return new_user_model

jinja2_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/newsfeed', NewsfeedHandler),
    ('/newsfeed/view', ViewGroupHandler),
    ('/allgroups', ViewAllGroupsHandler),
    ('/upload', UploadHandler),
    ('/uploaded', FinishedUploadHandler),
    ('/view_photo/([^/]+)', ViewPhotoHandler),
    ('/test', TestHandler),
    ('/create_group', CreateGroupHandler),
    ('/search', GroupSearchHandler)
], debug=True)
