from django.shortcuts import render, redirect
import twitter
import re
from datetime import datetime
from .models import User, Style, Truck # Rating

api = twitter.Api(consumer_key = 'LgPgWrpf0zyJimw1DSa4a9obx', 
	consumer_secret = 'RqazdCx73l8x2RRmvntVW08AYaFikh9lvYwc9iMdPTMICSgAmu', 
	access_token_key = '1564487502-FICCLO2KJOXTNW0BQmY3Hu7dxpm6psYcAsk8Bvw', 
	access_token_secret = 'GAQffclcmUeib1uPgsbGfM3RJnWDVDnxbnZzv7VcWNvJL')

TYSON_REGEX = re.compile(r'((t|T)yson).*')

def home(request):
	#landing page!

	#uncomment to nuke the databases
	#user = User.userManager.all().delete()
	#style = Style.styleManager.all().delete()
	#truck = truck.truckManager.all().delete()

	style = Style.styleManager.all()
	context = {'styles': style}
	return render(request, 'foodtruck/home.html', context)

def results(request):
	#shows the results dude
	#hey I think we need a search feature
	trucks = Truck.truckManager.all()
	context = {'trucks': trucks}
	return render(request, 'foodtruck/results.html', context)

def user(request):
	#a page to handle user login and registration
	return render(request, 'foodtruck/user.html')

def register(request):
	#make request to user in model and do some validatation... returns a tuple!
	user = User.userManager.register(request.POST['username'], request.POST['email'], request.POST['pw'], request.POST['cpw'])
	if user[0]:
		#Keep track of user in session
		request.session['user'] = (user[2], user[3])
		return redirect('/')
	else:
		#if there are errors let's show them
		context = {'errors': user[1]}
		return render(request, 'foodtruck/user.html', context)

def login(request):
	#make request to user in model and do some validatation... returns a tuple!
	user = User.userManager.login(request.POST['email'], request.POST['pw'])
	#check user is in database
	if user[0]:
		#check user password matches password for username
		if user[1]:
			#Keep track of user in session
			request.session['user'] = (user[2], user[3])
			return redirect('/')
	else:
		#if there are errors let's show them
		context = {'errors': user[1]}
		return render(request, 'foodtruck/user.html', context)

def logout(request):
	#gets rid of session variable and sends them back to login page
	request.session.clear()
	return redirect('/')

def addtruck(request):
	#require that they are logged in!
	if 'user' not in request.session:
		context = {'message': 'You need to login to add a truck!!!'}
		return render(request, 'foodtruck/user.html', context)
	else:
		#a page that shows forms for adding a food truck
		style = Style.styleManager.all()
		context = {'styles': style}
		return render(request, 'foodtruck/addtruck.html', context)

def add(request):
	#something that handles the request to the database

	if str(request.POST['style']) == 'Other':
		style = Style.styleManager.add(style=request.POST['other'])
		print style
		truck = Truck.truckManager.add(name=request.POST['name'], description=request.POST['description'], twitter=request.POST['twitter'], area=request.POST['area'], user=request.session['user'][0], style=style[1].id)
		# get the style id foreign key
	else:
		style = Style.styleManager.filter(id=request.POST['style'])
		# get the style id... request.POST['style']
		truck = Truck.truckManager.add(name=request.POST['name'], description=request.POST['description'], twitter=request.POST['twitter'], area=request.POST['area'], user=request.session['user'][0], style=request.POST['style'])
		print request.POST['style']

	#need to check style validation as well!

	return redirect('/')

def truck(request, id):
	#for a given truck id show off a truck
	#let's people leave ratings if logged in
	truck = Truck.truckManager.filter(id=id)
	context = {'truck': truck}
	return render(request, 'foodtruck/truck.html', context)

def edittruck(request, id):
	#for a given truck id edit the truck
	truck = Truck.truckManager.filter(id=id)
	context = {'truck': truck}
	return render(request, 'foodtruck/edit.html', context)

def edit(request, id):
	#handles the editting of a given truck
	#maybe use **args instead
	truck = Truck.truckManager.filter(id=id).update(name=request.POST['name'], description=request.POST['description'], twitter=request.POST['twitter'], style_id=style_id, area_id=area_id)
	return redirect('/')

def rating(request, id):
	#handles adding a rating for a given truck
	#check that user is logged in
	#keep track of truck number!
	rating = Rating.object.create(user_id=request.session['user'][2], truck_id=id, rating=request.POST['rating'], review=request.POST['review'])

	return redirect('/foodtruck/truck.html')

def update(request):
	#handles location updating for the app
	today = datetime.utcnow()
	trucks = Truck.truckManager.all()
	for truck in trucks:
		timeline = api.GetUserTimeline(screen_name='{}'.format(truck.twitter), count=1)
		now = datetime.strptime(timeline[0].created_at, '%a %b %d %H:%M:%S +0000 %Y')
		if now.date() == today.date():
			if TYSON_REGEX.search(str(timeline[0].text)):
				update = Truck.truckManager.filter(id=truck.id).update(location='Tysons Corner')

def reset(request):
	trucks = Truck.truckManager.all()
	for truck in trucks:
		update = Truck.truckManager.filter(id=truck.id).update(location='unknown')

