from django.shortcuts import render, redirect
import twitter
import re
from datetime import datetime
from .models import User, Style, Truck, Rating

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
	#for a given truck id show off a truck and reviews
	#let's people leave ratings if logged in
	truck = Truck.truckManager.filter(id=id)
	ratings = Rating.objects.filter(truck_id=id)
	avg = 0
	if len(ratings) > 0:
		total = 0
		for rating in ratings:
			total += float(rating.rating)
		avg = str(float(total / len(ratings)))[0:4]

	context = {'truck': truck, 'ratings': ratings, 'avg': avg}
	return render(request, 'foodtruck/truck.html', context)

def edittruck(request, id):
	#for a given truck id edit the truck
	truck = Truck.truckManager.filter(id=id)
	context = {'truck': truck}
	return render(request, 'foodtruck/edit.html', context)

def edit(request, id):
	#handles the editting of a given truck
	truck = Truck.truckManager.filter(id=id).update(name=request.POST['name'], description=request.POST['description'], twitter=request.POST['twitter'])
	return redirect('/truck/'+str(id))

def delete(request, id):
	#handles the deleting of a given truck
	truck = Truck.truckManager.filter(id=id).delete()
	return redirect('/')

def rating(request, id):
	#handles adding a rating for a given truck
	#also check if a rating already exists for the truck and maybe return an error if the rating is blank
	check = Rating.objects.filter(truck_id=id).filter(user_id=request.session['user'][0])
	if len(check) == 0:
		rating = Rating.objects.create(user_id=request.session['user'][0], truck_id=id, title=request.POST['title'], review=request.POST['review'], rating=request.POST['rating'])

	return redirect('/truck/'+str(id))

def update(request):
	#handles location updating for the app
	today = datetime.utcnow()
	trucks = Truck.truckManager.all()
	for truck in trucks:
		try:
			print truck.twitter
			timeline = api.GetUserTimeline(screen_name='{}'.format(truck.twitter), count=1)
			now = datetime.strptime(timeline[0].created_at, '%a %b %d %H:%M:%S +0000 %Y')
			print timeline
			print '*'*100
			if now.date() == today.date():
				if TYSON_REGEX.search(str(timeline[0].text)):
					update = Truck.truckManager.filter(id=truck.id).update(location='Tysons Corner')
		except: 
			pass
	return redirect('/')

def reset(request):
	trucks = Truck.truckManager.all()
	for truck in trucks:
		update = Truck.truckManager.filter(id=truck.id).update(location='unknown')
	return redirect('/')


