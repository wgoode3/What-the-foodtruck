from __future__ import unicode_literals
from django.db import models
import re
import bcrypt

TWITTER_REGEX = re.compile(r'^@([A-Za-z0-9_]+)$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{8,}$')

class UserManager(models.Manager):
	def register(self, username, email, pw, cpw):
		message = []
		if len(username) < 1:
			message.append('username cannot be blank')
		if len(email) < 1:
			message.append('email cannot be blank')
		if not EMAIL_REGEX.match(email):
			message.append('invalid email address')
		check = User.userManager.filter(username=username)
		if len(check) > 0:
			message.append('username already exists')
		check = User.userManager.filter(email=email)
		if len(check) > 0:
			message.append('email already exists')
		if len(pw) < 1:
			message.append('password cannot be blank')
		if not PASSWORD_REGEX.match(pw):
			message.append('password must be 8 characters or more with at least one capital letter, lowercase letter, and number')
		if pw != cpw:
			message.append('password does not match confirm password')

		if len(message) > 0:
			return (False, message)
		else:
			pw_hash = bcrypt.hashpw(str(pw), bcrypt.gensalt())
			user = User.userManager.create(username=username, email=email, pw_hash=pw_hash) 
			return (True, user, user.id, user.username)

	def login(self, email, pw):
		message = []
		if len(email) < 1:
			message.append('email cannot be blank')
		if len(pw) < 1:
			message.append('password cannot be blank')
		if not EMAIL_REGEX.match(email):
			message.append('invalid email address')
		if not PASSWORD_REGEX.match(pw):
			message.append('password must be 8 characters or more with at least one capital letter, lowercase letter, and number')
		
		if len(message) < 1:
			login = User.userManager.filter(email=email)
			if len(login) < 1:
				message.append('email not in database')
			else:
				if bcrypt.checkpw(str(pw), str(login[0].pw_hash)):
					return (True, login, login[0].id, login[0].username)
				else:
					message.append('wrong password dude')

		return (False, message)

class User(models.Model):
	username = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	pw_hash = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	userManager = UserManager()

class StyleManager(models.Manager):
	def add(self, style):
		message = []
		if len(style) < 1:
			message.append('style cannot be blank')

		if len(message) > 0: 
			return (False, message)
		else:
			style = Style.styleManager.create(style=style) 
			return (True, style)

class Style(models.Model):
	style = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	styleManager = StyleManager()

class TruckManager(models.Manager):
	def add(self, name, description, twitter, area, user, style):
		message = []
		if len(name) < 1:
			message.append('truck name cannot be blank')
		if len(description) < 1:
			message.append('description cannot be blank')
		if len(twitter) < 1:
			message.append('you must include the twitter account')
		if not TWITTER_REGEX.match(twitter):
			message.append('twitter account must have the form "@account"')
		if len(area) < 1:
			message.append("please list the truck's area")

		if len(message) > 0: 
			return (False, message)
		else:		
			
			check = Truck.truckManager.filter(twitter=twitter)
			if len(check) > 0:
				message.append('this twitter account is already in use')

			if len(message) > 0: 
				return (False, message)
			else:
				truck = Truck.truckManager.create(name=name, description=description, twitter=twitter, location='unknown', area=area, user_id=user, style_id=style) 
				return (True, truck)

class Truck(models.Model):
	name = models.CharField(max_length=255)
	description = models.CharField(max_length=255)
	twitter = models.CharField(max_length=255)
	area = models.CharField(max_length=255)
	location = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	user = models.ForeignKey(User)
	style = models.ForeignKey(Style)
	truckManager = TruckManager()

#many to many!
class Rating(models.Model):
	user = models.ForeignKey(User)
	truck = models.ForeignKey(Truck)
	title = models.CharField(max_length=255)
	review = models.CharField(max_length=255)
	rating = models.PositiveSmallIntegerField()
	
	