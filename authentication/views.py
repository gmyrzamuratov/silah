from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from authentication.models import MyUser
from main.models import Timezone, CurrentProject
from project.models import Project

# Create your views here.
# Create your views here.
def signin(request):
	
	return render(request, "authentication/signin.html")

def signup(request):

	return render(request, "authentication/signup.html")	

def login(request):

	email = request.POST['email']
	password = request.POST['password']

	user = authenticate(request, email=email, password=password)
	if user is not None:
		auth_login(request, user)

		timezones = Timezone.objects.filter(owner=request.user)

		if len(timezones) != 0:
			request.session['django_timezone'] = timezones[0].timezone

		if 'CurrentProject' not in request.session or request.session['CurrentProject'] == None:
			projects = CurrentProject.objects.filter(owner=request.user)
			if len(projects) == 0:
				projects = Project.objects.filter(owner=request.user)
				if len(projects)!=0:
					newCurrentProject = CurrentProject(owner=request.user, project=projects[0])
					newCurrentProject.save()
					request.session['CurrentProject'] = getJSON(projects[0])
			else:
				request.session['CurrentProject'] = getJSON(projects[0].project)

		return redirect("/")
	else:
		error = {'message': 'Incorrect user or password', }
		return render(request, "authentication/signin.html", error)

def getJSON(project):
	return {
	'id': project.id,
	'title': project.title
	}

def registration(request):

	email = request.POST['email']
	password = request.POST['password']
	repassword = request.POST['repassword']

	if password == repassword:

		#user = User(email=email, password=password)
		user = MyUser(email=email)
		user.set_password(password)
		user.is_active = True
		user.save()

		return render(request, "authentication/signin.html")
	else:
		error = {'message': 'Password does not same', }
		return render(request, "authentication/signup.html", error)