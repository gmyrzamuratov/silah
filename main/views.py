from django.shortcuts import render, redirect
import pytz
from .models import Timezone, Calendar, CurrentProject
from project.models import Project
from .forms import addForm

# Create your views here.
def index(request):

	if request.user.is_authenticated:
		# 
		if 'CurrentProject' not in request.session or request.session['CurrentProject'] == None:
			projects = CurrentProject.objects.filter(owner=request.user)
			if len(projects) == 0:
				projects = Project.objects.filter(owner=request.user)
				if len(projects)!=0:
					newCurrentProject = CurrentProject(owner=request.user, project=projects[0])
					newCurrentProject.save()
					request.session['CurrentProject'] = getJSON(projects[0])
					return redirect('post:new', id=request.session['CurrentProject']['id'])
				else:
					return redirect('project/list')
			else:
				request.session['CurrentProject'] = getJSON(projects[0].project)
				return redirect('post:new', id=projects[0].project.id)
		else:
			return redirect('post:new', id=request.session['CurrentProject']['id'])

	else:
		context = {}

		return render(request, "main/index.html", context)

def getJSON(project):
	return {
	'id': project.id,
	'title': project.title
	}

# Create your views here.
def privacyPolicy(request):

	if request.user.is_authenticated:
		projects = Project.objects.filter(owner=request.user)
		context = {
		'projects': projects
		}
	else:
		context = {}

	return render(request, "main/privacypolicy.html", context)

def calendar(request):

	projects = Project.objects.filter(owner=request.user)
	calendares = Calendar.objects.filter(owner=request.user)
	if len(calendares) == 0:
		htmlCode = "Empty"
	else:
		htmlCode = calendares[0].frame

	context = {
	"calendarCode" : htmlCode,
	'projects': projects
	}

	return render(request, "main/calendar.html", context)

def add_calendar(request):

	projects = Project.objects.filter(owner=request.user)
	calendares = Calendar.objects.filter(owner=request.user)
	if len(calendares) == 0:
		frame = ""
	else:
		frame = calendares[0].frame

	intial = {
	'frame': frame
	}

	#form = editForm(intial, instance=data)
	form = addForm(intial)

	context = {
	'form': form,
	'projects': projects
	}

	return render(request, "main/add_calendar.html", context)

# API
def set_timezone(request):

	if request.method == 'POST':
		request.session['django_timezone'] = request.POST['timezone']

		timezones = Timezone.objects.filter(owner=request.user)

		if len(timezones) == 0:
			timezone = Timezone(owner=request.user, timezone=request.POST['timezone'])
			timezone.save()
		else:
			timezone = timezones[0]
			timezone.timezone = request.POST['timezone']
			timezone.save()

		return redirect('/')
	else:
		return render(request, 'main/timezone.html', {'timezones': pytz.common_timezones})

def insert_calendar(request):

	if request.method == 'POST':

		form = addForm(request.POST)

		if(form.is_valid()):

			frame = form.cleaned_data['frame']

			calendares = Calendar.objects.filter(owner=request.user)
			if len(calendares) == 0:
				newCalendar = Calendar(owner=request.user, frame = frame)
				newCalendar.save()
			else:
				editCalendar = calendares[0]
				editCalendar.save()

	return redirect('/calendar')