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
    url = ndb.StringProperty()

class User(ndb.Model):
    user = ndb.UserProperty()
    users_photo_group_keys = ndb.KeyProperty(repeated=True)

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        # this is the login section
        user = users.get_current_user()
        if user:
            greeting = ('Hey, %s! (<a href="%s">sign out</a>)' %
                (user.nickname(), users.create_logout_url('/')))
            self.redirect('/newsfeed')
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
        user = users.get_current_user()
        if not user:
            self.redirect('/')
        else:
            greeting = ('%s! (<a href="%s">sign out</a>)' %
                (user.nickname(), users.create_logout_url('/')))
            #Get the current user's model. If there's none then create a model for the new user.
            current_user = get_user_model()
            #get the user's created photo groups. The variable is a list of PhotoGroup models
            photo_group_data = get_users_photo_groups(current_user)
            template_vars = {"photo_group_data" : photo_group_data, "greeting" : greeting}
            self.response.write(template.render(template_vars))

#This handler is needed in order to create a group.
#NEEDED FOR TESTING PURPOSES
class CreateGroupHandler(webapp2.RequestHandler):
    def get(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        template = jinja2_environment.get_template('templates/creategroup.html')
        self.response.write(template.render())
    def post(self):
        name = self.request.get("group_name")
        type = self.request.get("type")
        description = self.request.get("description")
        type = True if type.lower() == "public" else False
        user = users.get_current_user()
        new_photo_group = PhotoGroup(group_name = name, is_group_public=type, description=description)
        temp = add_url_to_photogroup(new_photo_group).put()
        current_user_model = get_user_model()
        current_user_model.users_photo_group_keys += [temp]
        current_user_model.put()
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

class EditUploadsHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("HELLO WORLD")

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
        current_user = get_user_model()
        users_photo_groups = get_users_photo_groups(current_user)
        for group in users_photo_groups:
            self.response.write(group.photos[0].url)
            self.response.write(group.group_name)
            self.response.write("<br/>")
            self.response.write("<br/>")

def add_url_to_photogroup(new_photo_group):
    new_photo_group = new_photo_group.put()
    temp_id = new_photo_group.id()
    temp = PhotoGroup.get_by_id(temp_id)
    group_url = "/newsfeed/view?group_id=" + str(temp_id)
    temp.url = group_url
    return temp

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        fixed = jinja2_environment.get_template('templates/fixed.html')
        self.response.write(fixed.render())
        about = jinja2_environment.get_template('templates/about.html')
        self.response.write(about.render())

def get_user_model():
    current_user = users.get_current_user()
    user_model_list = User.query().fetch()
    for temp_user_model in user_model_list:
        if temp_user_model.user == current_user:
            return temp_user_model
    new_user_model = User(user=current_user)
    new_user_model.put()
    return new_user_model

def get_users_photo_groups(current_user):
    users_photo_groups = []
    users_photo_group_keys = current_user.users_photo_group_keys
    logging.info(users_photo_group_keys)
    for photo_group in users_photo_group_keys:
        id = photo_group.id()
        group = PhotoGroup.get_by_id(id)
        users_photo_groups += [group]
    return users_photo_groups

jinja2_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/newsfeed', NewsfeedHandler),
    ('/newsfeed/view', ViewGroupHandler),
    ('/allgroups', ViewAllGroupsHandler),
    ('/upload', UploadHandler),
    ('/uploaded', FinishedUploadHandler),
    ('/upload/edit', EditUploadsHandler),
    ('/test', TestHandler),
    ('/create_group', CreateGroupHandler),
    ('/search', GroupSearchHandler),
    ('/about', AboutHandler)
], debug=True)
