#!/usr/bin/env python
###
### This is a web service for use with App
### Inventor for Android (<http://appinventor.googlelabs.com>)
### This particular service stores and retrieves tag-value pairs 
### using the protocol necessary to communicate with the TinyWebDB
### component of an App Inventor app.


### Original code by: David Wolber (wolber@usfca.edu), using sample of Hal Abelson
### Web support and minecraft integration by: Isaac Hutt

import logging
from cgi import escape
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.db import Key
from django.utils import simplejson as json
from google.appengine.api import users

class StoredData(db.Model):
  tag = db.StringProperty()
  value = db.StringProperty(multiline=True)
  ## defining value as a string property limits individual values to 500
  ## characters.   To remove this limit, define value to be a text
  ## property instead, by commnenting out the previous line
  ## and replacing it by this one:
  ## value db.TextProperty()
  date = db.DateTimeProperty(required=True, auto_now=True)
class StoredMessages(db.Model):
  author = db.StringProperty()
  value = db.StringProperty(multiline=True)
  read = db.StringProperty()
  ## defining value as a string property limits individual values to 500
  ## characters.   To remove this limit, define value to be a text
  ## property instead, by commnenting out the previous line
  ## and replacing it by this one:
  ## value db.TextProperty()
  date = db.DateTimeProperty(required=True, auto_now=True)
class StoredUsers(db.Model):
  name = db.StringProperty()
  email = db.StringProperty()
  ID = db.StringProperty()
  verified = db.StringProperty()
  mcname = db.StringProperty()
  code = db.StringProperty()
  ## defining value as a string property limits individual values to 500
  ## characters.   To remove this limit, define value to be a text
  ## property instead, by commnenting out the previous line
  ## and replacing it by this one:
  ## value db.TextProperty()
  date = db.DateTimeProperty(required=True, auto_now=True)
IntroMessage = '''
<table border=0>
<tr valign="top">
<td><image src="/images/customLogo.png" width="200" hspace="10"></td>
<td>
<p>
Welcome to TheBuildcast news feed updater. 

</td> </tr> </table>'''


class MainPage(webapp.RequestHandler):

  def get(self):
    write_page_header(self);
    self.response.out.write(IntroMessage)
    write_available_operations(self)
    show_stored_data(self)
    self.response.out.write('</body></html>')

########################################
### Implementing the operations
### Each operation is design to respond to the JSON request
### or to the Web form, depending on whether the fmt input to the post
### is json or html.

### Each operation is a class.  The class includes the method that
### actually, manipualtes the DB, followed by the methods that respond
### to post and to get.


class StoreAValue(webapp.RequestHandler):

  def store_a_value(self, tag, value):
    # There's a potential readers/writers error here :(
	if users.get_current_user():
		if users.is_current_user_admin():
			entry1 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "7").get()
			entry1.value = value
			value.replace(" ", "()")
			entry1.value.replace(" ", "()")
			entry1.tag = "1"
			entry2 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "1").get()
			entry3 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "2").get()
			entry4 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "3").get()
			entry5 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "4").get()
			entry6 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "5").get()
			'''db.run_in_transaction(dbSafeDelete,"1")
			db.run_in_transaction(dbSafeDelete,"2")
			db.run_in_transaction(dbSafeDelete,"3")
			db.run_in_transaction(dbSafeDelete,"4")
			db.run_in_transaction(dbSafeDelete,"5")'''
			entry2.tag="2"
			entry3.tag="3"
			entry4.tag="4"
			entry5.tag="5"
			entry6.tag="7"
			entry1.put()
			entry2.put()
			entry3.put()
			entry4.put()
			entry5.put()
			entry6.put()
			## Send back a confirmation message.  The TinyWebDB component ignores
			## the message (other than to note that it was received), but other
			## components might use this.
			result = ["STORED", entry1.tag, value, entry1.value]
			WritePhoneOrWeb(self, lambda : json.dump(result, self.response.out))
		else:
			self.response.out.write("You do not have permission to do this! <p><a href='"+users.create_logout_url(self.request.uri)+"'>logout</a>")
	else:
		self.redirect(users.create_login_url(self.request.uri))

  def post(self):
    tag = self.request.get('tag')
    value = self.request.get('value').replace(" ", "()")
    self.store_a_value(tag, value.replace(" ", "()"))

  def get(self):
    self.response.out.write('''
    <html><body>
    <form action="/storeavalue" method="post"
          enctype=application/x-www-form-urlencoded>
       <input type="hidden" name="tag" value="1" />
       <p>News:<input type="text" name="value" /></p>
       <input type="hidden" name="fmt" value="html">
       <input type="submit" value="Add News">
    </form></body></html>\n''')

class GetValue(webapp.RequestHandler):

  def get_value(self, tag):
    entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
    if entry:
      value = entry.value
    else: value = ""
    ## We tag the returned result with "VALUE".  The TinyWebDB
    ## component makes no use of this, but other programs might.
    ## check if it is a html request and if so clean the tag and value variables
    if self.request.get('fmt') == "html":
      value = escape(value)
      tag = escape(tag)
    WritePhoneOrWeb(self, lambda : json.dump(["VALUE", tag, value], self.response.out))

  def post(self):
    tag = self.request.get('tag')
    self.get_value(tag)

  def get(self):
    self.response.out.write('''
    <html><body>
    <form action="/getvalue" method="post"
          enctype=application/x-www-form-urlencoded>
       <p>Tag<input type="text" name="tag"/></p>
       <input type="hidden" name="fmt" value="html">
       <input type="submit" value="Get value">
    </form></body></html>\n''')


### The DeleteEntry is called from the Web only, by pressing one of the
### buttons on the main page.  So there's no get method, only a post.

class DeleteEntry(webapp.RequestHandler):

  def post(self):
  	if users.get_current_user():
		if users.is_current_user_admin():
			logging.debug('/deleteentry?%s\n|%s|' %
						(self.request.query_string, self.request.body))
			entry_key_string = self.request.get('entry_key_string')
			key = db.Key(entry_key_string)
			tag = self.request.get('tag')
			entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", tag).get()
			entry.value=db.GqlQuery("SELECT * FROM StoredData where tag = :1", "7").get().value
			entry.put()
			self.redirect('/')
		else:
			self.response.out.write("You do not have permission to do this! <p><a href='"+users.create_logout_url(self.request.uri)+"'>logout</a>")
	else:
		self.redirect(users.create_login_url(self.request.uri))
		
class update(webapp.RequestHandler):

	def get(self):
		entry = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "update").get()
		self.response.out.write(entry.value)
		
class ChangeUpdate(webapp.RequestHandler):

	def post(self):
		tag = self.request.get('update')
		entry1 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "update").get()
		entry1.value = tag
		entry1.put()
		self.redirect('/')
	def get(self):
		self.response.out.write('''
		<html><body>
		<form action="/updater" method="post"
		enctype=application/x-www-form-urlencoded>
		<p>Tag<input type="text" name="update"/></p>
		<input type="hidden" name="fmt" value="html">
		<input type="submit" value="Get value">
		</form></body></html>\n''')
class chatter(webapp.RequestHandler):

	def post(self):
		tag = self.request.get('value')
		entry1 = db.GqlQuery("SELECT * FROM StoredData where tag = :1", "chat").get()
		if (entry1.value == ""):
			entry1.value = tag
			entry1.put()
		self.redirect('/chatter')
	def get(self):
		self.response.out.write('''
		<html><body>
		<form action="/chatter" method="post"
		enctype=application/x-www-form-urlencoded>
		<p>Text<input type="text" name="value"/></p>
		<input type="hidden" name="fmt" value="html">
		<input type="submit" value="Get value">
		</form></body></html>\n''')
########################################
#### Procedures used in displaying the main page
class chat(webapp.RequestHandler):

	def get(self):
		if db.GqlQuery("SELECT * FROM StoredMessages where read = :1 LIMIT 1", "false").get():
			entry = db.GqlQuery("SELECT * FROM StoredMessages where read = :1 LIMIT 1", "false").get()
			self.response.out.write(entry.author+"(online):"+entry.value)
			entry.read = "true"
			entry.put()
		
class webchat(webapp.RequestHandler):

	def get(self):
		
		self.response.out.write("Welcome to webchat")
		if users.get_current_user():
			self.response.out.write("<a href="+users.create_logout_url(self.request.uri)+">Logout</a>")
			if db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get():
				login = "true"
			else:
				entry = StoredUsers(name = users.get_current_user().nickname(),email = users.get_current_user().email(), ID = users.get_current_user().user_id(), mcname = "")
				entry.put()
			if db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get().mcname == "":
				self.response.out.write("<a href='/verify'>Verify Account</a>")
			else:
				self.response.out.write("You can post messages.")
				self.response.out.write('''
			<html><body>
			<form action="/" method="post"
			enctype=application/x-www-form-urlencoded>
			<p>Message<input type="text" name="message"/></p>
			<input type="submit" value="Post Message">
			</form></body</html>\n''')
		else:
			self.response.out.write("<a href="+users.create_login_url(self.request.uri)+">Login</a>")
		show_stored_messages(self)
	def post(self):
		message = self.request.get('message')
		entry = StoredMessages(author = db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get().mcname,value = message, read = "false")
		entry.put()
		self.redirect('/')
class verify(webapp.RequestHandler):

	def post(self):
		if users.get_current_user():
			self.response.out.write("<a href="+users.create_logout_url(self.request.uri)+">Logout</a>")
			if db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get():
				login = "true"
			else:
				self.redirect('/')
			if db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get().mcname:
				if db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get().mcname == "":
					self.response.out.write("You have not issued the /getverifcode command yet.")
				else:
					tag = self.request.get('code')
					name = self.request.get('mcname')
					entry1 = db.GqlQuery("SELECT * FROM StoredUsers where email = :1", users.get_current_user().email()).get()
					if tag == entry1.code and name == entry1.mcname:
						entry1.verified = "true"
						entry1.mcname = name
						entry1.put()
						self.redirect('/')
					else:
						self.response.out.write("Incorrect code.")
			else:
				self.redirect('/')
		else:
			self.redirect('/')
	def get(self):
		self.response.out.write('''
		<html><body>
		<form action="/verify" method="post"
		enctype=application/x-www-form-urlencoded>
		Please type /getverifcode your-google@email into minecraft to get the vefification code.
		<p>Code<input type="text" name="code"></p>
		MineCraft Name<input type="text" name="mcname">
		<input type="submit" value="Verify">
		</form></body></html>\n''')
class getcode(webapp.RequestHandler):
	def post(self):
		self.response.out.write('''
		<html><body>
		<form action="/verify" method="post"
		enctype=application/x-www-form-urlencoded>
		Please type /getverifcode your-google@email into minecraft to get the vefification code.
		<p>Code<input type="text" name="code"></p>
		MineCraft Name<input type="text" name="mcname">
		<input type="text" name="user">
		</form></body></html>\n''')
		user = self.request.get('user')
		code = self.request.get('code')
		name = self.request.get('mcname')
		entry = db.GqlQuery("SELECT * FROM StoredUsers where email = :1", user).get()
		entry.code = code
		entry.mcname = name
		entry.put()
	def get(self):
		self.response.out.write("If you are looking to hack this site then think again")
		self.response.out.write('''
		<html><body>
		<form action="/verify" method="post"
		enctype=application/x-www-form-urlencoded>
		Please type /getverifcode your-google@email into minecraft to get the vefification code.
		<p>Code<input type="text" name="code"></p>
		MineCraft Name<input type="text" name="mcname">
		<input type="text" name="user">
		</form></body></html>\n''')
class chatline(webapp.RequestHandler):
	def post(self):
		self.response.out.write('''
		<html><body>
		<form action="/addchatline" method="post"
		enctype=application/x-www-form-urlencoded>
		Please type /getverifcode your-google@email into minecraft to get the vefification code.
		<p>Code<input type="text" name="user"></p>
		MineCraft Name<input type="text" name="message">
		<input type="submit" value="a">
		</form></body></html>\n''')
		user = self.request.get('user')
		message = self.request.get('message')
		entry = StoredMessages(author = user,value = message, read = "false")
		entry.put()
	def get(self):
		self.response.out.write("If you are looking to hack this site then think again")
		self.response.out.write('''
		<html><body>
		<form action="/addchatline" method="post"
		enctype=application/x-www-form-urlencoded>
		Please type /getverifcode your-google@email into minecraft to get the vefification code.
		<p>Code<input type="text" name="user"></p>
		MineCraft Name<input type="text" name="message">
		<input type="submit" value="a">
		</form></body></html>\n''')

### Show the API
def write_available_operations(self):
  self.response.out.write('''
    <p>Tasks:\n
    <ul>
    <li><a href="/storeavalue">Add News</a></li>
    </ul>''')

### Generate the page header
def write_page_header(self):
  self.response.headers['Content-Type'] = 'text/html'
  self.response.out.write('''
     <html>
     <head>
     <style type="text/css">
        body {margin-left: 5% ; margin-right: 5%; margin-top: 0.5in;
             font-family: verdana, arial,"trebuchet ms", helvetica, sans-serif;}
        ul {list-style: disc;}
     </style>
     <title>New Feed Editor</title>
     </head>
     <body>''')
  self.response.out.write('<h2>TheBuildcast New Feed Editor</h2>')

### Show the tags and values as a table.
def show_stored_data(self):
  self.response.out.write('''
    <p><table border=0>
      <tr>
         
         <th>News</th>
         <th>Date</th>
		 <th>Delete</th>
      </tr>''')
  # This next line is replaced by the one under it, in order to help
  # protect against SQL injection attacks.  Does it help enough?
  #entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY tag")
  entries = StoredData.all().order("-tag")
  for e in entries:
    entry_key_string = str(e.key())
    self.response.out.write('<tr>')
    self.response.out.write('<td>%s</td>' % escape(e.value))      
    self.response.out.write('<td><font size="-1">%s</font></td>\n' % e.date.ctime())
    self.response.out.write('''
      <td><form action="/deleteentry" method="post"
            enctype=application/x-www-form-urlencoded>
	    <input type="hidden" name="entry_key_string" value="%s">
	    <input type="hidden" name="tag" value="%s">
            <input type="hidden" name="fmt" value="html">
	    <input type="submit" style="background-color: red" value="Delete"></form></td>\n''' %
                            (entry_key_string, escape(e.tag)))
    self.response.out.write('</tr>')
  self.response.out.write('</table>')


def show_stored_messages(self):
  self.response.out.write('''
    <p><table border=0>
      <tr>
         
         <th>User</th>
         <th>Message</th>
	
      </tr>''')
  # This next line is replaced by the one under it, in order to help
  # protect against SQL injection attacks.  Does it help enough?
  #entries = db.GqlQuery("SELECT * FROM StoredData ORDER BY tag")
  entries = StoredMessages.all().order("-date")
  for e in entries:
    entry_key_string = str(e.key())
    self.response.out.write('<tr>')
    self.response.out.write('<td>%s</td>' % escape(e.author))      
    self.response.out.write('<td><font size="-1">%s</font></td>\n' % e.value)
    self.response.out.write('</tr>')
  self.response.out.write('</table>')


#### Utilty procedures for generating the output

#### Write response to the phone or to the Web depending on fmt
#### Handler is an appengine request handler.  writer is a thunk
#### (i.e. a procedure of no arguments) that does the write when invoked.
def WritePhoneOrWeb(handler, writer):
  if handler.request.get('fmt') == "html":
    WritePhoneOrWebToWeb(handler, writer)
  else:
    handler.response.headers['Content-Type'] = 'application/jsonrequest'
    writer()

#### Result when writing to the Web
def WritePhoneOrWebToWeb(handler, writer):
  handler.response.headers['Content-Type'] = 'text/html'
  handler.response.out.write('<html><body>')
  handler.response.out.write('''
  <em>The server will send this to the component:</em>
  <p />''')
  writer()
  WriteWebFooter(handler, writer)


#### Write to the Web (without checking fmt)
def WriteToWeb(handler, writer):
  handler.response.headers['Content-Type'] = 'text/html'
  handler.response.out.write('<html><body>')
  writer()
  WriteWebFooter(handler, writer)

def WriteWebFooter(handler, writer):
  handler.response.out.write('''
  <p><a href="/">
  <i>Return to Game Server Main Page</i>
  </a>''')
  handler.response.out.write('</body></html>')

### A utility that guards against attempts to delete a non-existent object
def dbSafeDelete(key):
  if db.get(key) :  db.delete(key)


### Assign the classes to the URL's

application =     \
   webapp.WSGIApplication([('/admin', MainPage),
                           ('/storeavalue', StoreAValue),
                           ('/deleteentry', DeleteEntry),
                           ('/getvalue', GetValue),
						   ('/update', update),
						   ('/updater', ChangeUpdate),
						   ('/chat', chat),
						   ('/chatter', chatter),
						   ('/',webchat),
						   ('/verify', verify),
						   ('/getcodesecretid123456789', getcode),
						   ('/addchatline', chatline)
                           ],
                          debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
