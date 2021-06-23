from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch
from .forms import newForm, editForm
from .models import Project, Profile, Network
from main.models import CurrentProject
from post.models import Post

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
from project import oauth
import requests
from hootsweet import HootSweet

# Create your views here.
def list(request):

	if request.user.is_authenticated:
		projects = Project.objects.filter(owner=request.user)
		context = {
		'projects': projects,
		}
	else:
		context = {}	

	return render(request, "project/list.html", context)

def new(request):

	form = newForm()

	projects = Project.objects.filter(owner=request.user)
	context = {
	'form': form,
	'projects': projects,
	}

	return render(request, "project/new.html", context)

def edit(request, id):

	projects = Project.objects.filter(owner=request.user)
	project = Project.objects.get(pk=id)

	intial = {
	'id': id,
	'title': project.title
	}

	form = editForm(intial)

	context = {
	'form': form,
	'projects': projects
	}

	return render(request, "project/edit.html", context)

def detail(request, id):

	projects = Project.objects.filter(owner=request.user)
	projectDetails = Project.objects.get(pk=id)
	currentProjects = CurrentProject.objects.filter(owner=request.user)
	if len(currentProjects) == 0:
		newCurrentPorject = CurrentProject(owner=request.user, project=projectDetails)
		newCurrentPorject.save()
	else:
		currentProjects[0].project = projectDetails
		currentProjects[0].save()

	request.session['CurrentProject'] = getJSON(projectDetails)
	posts = Post.objects.filter(project=id)
	context = {
	'data': projectDetails,
	'posts': posts,
	'projects': projects
	}

	return render(request, "project/detail.html", context)

def getJSON(project):
	return {
	'id': project.id,
	'title': project.title
	}

def profiles(request, id):

	project = Project.objects.get(pk=id)
	profiles = Profile.objects.filter(project=id)
	context = {
	'profiles': profiles,
	'project': project
	}

	return render(request, "project/profiles.html", context)

def addsocialnetwork(request, id):

	networks = Network.objects.all()
	context = {
	'networks': networks,
	'project_id': id
	}

	return render(request, "project/add_social_network.html", context)

def youtubeauthorize(request, id):

	flow = InstalledAppFlow.from_client_secrets_file(str(settings.BASE_DIR)+settings.CLIENT_SECRETS_FILE, scopes=settings.YOUTUBE_UPLOAD_SCOPE)
	flow.redirect_uri = request.build_absolute_uri(reverse('project:youtubeoauth2callback'))

	print(flow.redirect_uri)
	authorization_url, state = flow.authorization_url(
	# Enable offline access so that you can refresh an access token without
	# re-prompting the user for permission. Recommended for web server apps.
	access_type='offline',

	prompt='consent',
	# Enable incremental authorization. Recommended as a best practice.
	include_granted_scopes='true')

	# Store the state so the callback can verify the auth server response.
	request.session['state'] = state
	request.session['project_id'] = id

	return HttpResponseRedirect(authorization_url)

def googlecalendarauthorize(request, id):

	flow = InstalledAppFlow.from_client_secrets_file(str(settings.BASE_DIR)+settings.GCALENDAR_CLIENT_SECRETS_FILE, scopes=settings.GCALENDAR_UPLOAD_SCOPE)
	flow.redirect_uri = request.build_absolute_uri(reverse('project:gcalendaroauth2callback'))

	print(flow.redirect_uri)
	authorization_url, state = flow.authorization_url(
	# Enable offline access so that you can refresh an access token without
	# re-prompting the user for permission. Recommended for web server apps.
	access_type='offline',

	prompt='consent',
	# Enable incremental authorization. Recommended as a best practice.
	include_granted_scopes='true')

	# Store the state so the callback can verify the auth server response.
	request.session['state'] = state
	request.session['project_id'] = id

	return HttpResponseRedirect(authorization_url)

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes,
          'id_token': credentials.id_token}

def youtubeoauth2callback(request):

	state = request.session['state']

	flow = InstalledAppFlow.from_client_secrets_file(str(settings.BASE_DIR)+settings.CLIENT_SECRETS_FILE, scopes=settings.YOUTUBE_UPLOAD_SCOPE, state=state)
	flow.redirect_uri = request.build_absolute_uri(reverse('project:youtubeoauth2callback'))

	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	authorization_response = request.build_absolute_uri()
	if "http:" in authorization_response:
		authorization_response = "https:" + authorization_response[5:]
	flow.fetch_token(authorization_response=authorization_response)

	# Store credentials in the session.
	# ACTION ITEM: In a production app, you likely want to save these
	#              credentials in a persistent database instead.
	credentials = flow.credentials
	pickle_file = str(settings.BASE_DIR)+f'/system/token_{settings.YOUTUBE_API_SERVICE_NAME}_{settings.YOUTUBE_API_VERSION}.pickle'
	with open(pickle_file, 'wb') as token:
		pickle.dump(credentials, token)

	#print(credentials_to_dict(credentials))

	crdt = Credentials(
		token=credentials.token, 
		refresh_token=credentials.refresh_token, 
		id_token=credentials.id_token, 
		token_uri=credentials.token_uri, 
		client_id=credentials.client_id, 
		client_secret=credentials.client_secret, 
		scopes=credentials.scopes)

	youtubeChannelId = ''
	youtubeChannelName = ''
	service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, credentials=crdt)
	response = service.channels().list(part='id,snippet', mine=True).execute()
	for k, v in response.items():
		if k == 'items':
			for d, c in v[0].items():
				if d == 'id':
					youtubeChannelId = c
				if d == 'snippet':
					for a, b in c.items():
						if a == 'title':
							youtubeChannelName = b

	print(youtubeChannelId)
	print(youtubeChannelName)
	print(credentials.id_token)

	if youtubeChannelId!='':
		project_id = request.session['project_id']
		network = Network.objects.filter(name='Youtube')[0]
		project = Project.objects.get(pk=project_id)

		newProfile = Profile(name=youtubeChannelName, 
			profile_id=youtubeChannelId, 
			access_token=credentials.token, 
			network=network, 
			project=project,
			refresh_token=credentials.refresh_token,
			id_token=credentials.id_token,
			token_uri=credentials.token_uri,
			client_id=credentials.client_id,
			client_secret=credentials.client_secret,
			scopes=credentials.scopes)
		newProfile.save()

	return redirect('project:profiles', id=project_id)
	#return render(request, "project/list.html")

def gcalendaroauth2callback(request):

	state = request.session['state']

	flow = InstalledAppFlow.from_client_secrets_file(str(settings.BASE_DIR)+settings.GCALENDAR_CLIENT_SECRETS_FILE, scopes=settings.GCALENDAR_UPLOAD_SCOPE, state=state)
	flow.redirect_uri = request.build_absolute_uri(reverse('project:gcalendaroauth2callback'))

	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	authorization_response = request.build_absolute_uri()
	if "http:" in authorization_response:
		authorization_response = "https:" + authorization_response[5:]
	flow.fetch_token(authorization_response=authorization_response)

	# Store credentials in the session.
	# ACTION ITEM: In a production app, you likely want to save these
	#              credentials in a persistent database instead.
	credentials = flow.credentials
	#pickle_file = str(settings.BASE_DIR)+f'/system/token_{settings.GCALENDAR_API_SERVICE_NAME}_{settings.GCALENDAR_API_VERSION}.pickle'
	#with open(pickle_file, 'wb') as token:
	#	pickle.dump(credentials, token)

	#print(credentials_to_dict(credentials))

	crdt = Credentials(
		token=credentials.token, 
		refresh_token=credentials.refresh_token, 
		id_token=credentials.id_token, 
		token_uri=credentials.token_uri, 
		client_id=credentials.client_id, 
		client_secret=credentials.client_secret, 
		scopes=credentials.scopes)

	googleCalendarId = 'primary'
	googleCalendarName = 'primary'
	service = build(settings.GCALENDAR_API_SERVICE_NAME, settings.GCALENDAR_API_VERSION, credentials=crdt)

	project_id = request.session['project_id']
	network = Network.objects.filter(name='Google Calendar')[0]
	project = Project.objects.get(pk=project_id)

	newProfile = Profile(name=googleCalendarName, 
			profile_id=googleCalendarId, 
			access_token=credentials.token, 
			network=network, 
			project=project,
			refresh_token=credentials.refresh_token,
			id_token=credentials.id_token,
			token_uri=credentials.token_uri,
			client_id=credentials.client_id,
			client_secret=credentials.client_secret,
			scopes=credentials.scopes)
	newProfile.save()

	return redirect('project:profiles', id=project_id)

def twitter_login(request, id):

	try:
		protocol      = 'https' if request.is_secure() else 'http'
		host          = request.get_host()
		path          = reverse('twitter-callback')
		callback_url  = protocol + '://' + host + path
	except NoReverseMatch:
		callback_url  = None

	# get a request token from Twitter
	consumer      = oauth.Consumer(settings.TWITTER_KEY, settings.TWITTER_SECRET)
	request_token = oauth.RequestToken(consumer, callback_url=callback_url)

	# save the redirect destination
	#request.session['redirect_to'] = request.REQUEST.get(redirect_field_name, None)
	request.session['project_id'] = id

	# redirect to Twitter for authorization
	return HttpResponseRedirect(request_token.authorization_url)


def twitter_callback(request):

	oauth_token    = request.GET['oauth_token']
	oauth_verifier = request.GET['oauth_verifier']

	# get an access token from Twitter
	consumer           = oauth.Consumer(settings.TWITTER_KEY, settings.TWITTER_SECRET)
	access_token       = oauth.AccessToken(consumer, oauth_token, oauth_verifier)

	# actually log in
	twitter_id  = access_token.user_id
	username    = access_token.username
	token       = access_token.token
	secret      = access_token.secret

	project_id = request.session['project_id']
	network = Network.objects.filter(name='Twitter')[0]
	project = Project.objects.get(pk=project_id)
	newProfile = Profile(name=username, 
			profile_id=twitter_id, 
			access_token=token, 
			network=network, 
			project=project,
			refresh_token='',
			id_token='',
			token_uri='',
			client_id=twitter_id,
			client_secret=secret,
			scopes='')
	newProfile.save()

	# redirect to the authenticated view
	#redirect_to = request.session['redirect_to']

	return redirect('project:profiles', id=project_id)


def handle_hootsuite_refresh(token):

	print(token)

def hootsuite_authorize(request, id):

	channel_name = request.POST['hootsuiteChannelName']

	client = HootSweet(settings.HOOTSUITE_CLIENT_ID, settings.HOOTSUITE_SECRET, redirect_uri=settings.HOOTSUITE_REDIRECT_URI, refresh_cb=handle_hootsuite_refresh)

	# Step 1 get authorization url from HootSuite
	url, state = client.authorization_url()

	request.session['channel_name'] = channel_name
	request.session['project_id'] = id

	# redirect to Twitter for authorization
	return HttpResponseRedirect(url)

	# Step 2 go to url above and get OAuth2 code
	#token = client.fetch_token(code)

	# client.token now contains your authentication token
	# Step 3 (optional) refresh token periodically, this automatically calls handle_refresh
	#token = client.refresh_token()

	# retrieve data from https://platform.hootsuite.com/v1/me
	#me = client.get_me()

	# retrieve authenticated members organizations https://platform.hootsuite.com/v1/me/organizations
	#organizations = client.get_me_organizations()

def hootsuite_callback(request):

	code    = request.GET['code']

	client = HootSweet(settings.HOOTSUITE_CLIENT_ID, settings.HOOTSUITE_SECRET, redirect_uri=settings.HOOTSUITE_REDIRECT_URI, refresh_cb=handle_hootsuite_refresh)

	token = client.fetch_token(code)

	print(f'token={token}')

	channel_name = request.session['channel_name']
	project_id = request.session['project_id']

	network = Network.objects.filter(name='Hootsuite')[0]

	project = Project.objects.get(pk=project_id)
	newProfile = Profile(name=channel_name, 
			profile_id='', 
			access_token=token, 
			network=network, 
			project=project,
			refresh_token='',
			id_token='',
			token_uri='',
			client_id='',
			client_secret='',
			scopes='')
	newProfile.save()

	# redirect to the authenticated view
	#redirect_to = request.session['redirect_to']

	return redirect('project:profiles', id=project_id)


def getLongLivedUserAccessToken(access_token):

	app_id = settings.FACEBOOK_APP_ID
	client_secret = settings.FACEBOOK_APP_SECRET

	url = f"https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={client_secret}&grant_type=fb_exchange_token&fb_exchange_token={access_token}"
	print("user url=" + url)

	facebook_long_lived_access_token = ""
	result=requests.get(url)
	if (result.status_code == 200):
		j_res = result.json()
		facebook_long_lived_access_token = j_res.get('access_token')
		print("user token = " + facebook_long_lived_access_token)

	return facebook_long_lived_access_token

def getLongLivedPageAccessToken(user_id, long_lived_user_access_token, page_id):

	app_id = settings.FACEBOOK_APP_ID
	client_secret = settings.FACEBOOK_APP_SECRET

	url = f"https://graph.facebook.com/v8.0/{user_id}/accounts?access_token={long_lived_user_access_token}"
	print('page token url' + url)
	
	facebook_long_lived_access_token = ""
	result=requests.get(url)
	print('request result' + result.text)
	if (result.status_code == 200):
		j_res = result.json()
		pages = j_res.get('data')
		for page in pages:
			if page['id'] == page_id:
				facebook_long_lived_access_token = page['access_token']
				print("page token = " + facebook_long_lived_access_token)


	return facebook_long_lived_access_token

# API -----------------------------------------------------------------------------
# Functions
def insert(request):

	if request.method == 'POST':

		form = newForm(request.POST)

		if(form.is_valid()):

			title = form.cleaned_data['title']

			if title == '':
				return

			newProject = Project(title=title, owner=request.user)
			newProject.save()

			return redirect('project:list')
		else:
			return render(request, "project/new.html", {'data': request.method})

	else:
		return render(request, "project/new.html", {'data':request.method})

def update(request):

	if request.method == 'POST':

		form = editForm(request.POST)

		if(form.is_valid()):

			id    = form.data['id']
			title = form.cleaned_data['title']

			try:
				obj = Project.objects.get(pk=id)
				obj.title = title
				obj.save()
			except Project.DoesNotExist:
				raise Http404(f"We can't find post with id={id}")


			return redirect('project:detail', id=id)

	else:
		return render(request, "project/edit.html", {'data':request.method})

def insertprofile(request):

	if request.method == 'POST':

		name = request.POST['name']
		profile_id = request.POST['profile_id']
		user_id = request.POST['user_id']
		user_access_token = request.POST['user_access_token']
		access_token = request.POST['access_token']
		project_id = request.POST['project_id']
		network_id = request.POST['network_id']

		if name == '':
			return

		network = Network.objects.get(pk=network_id)
		project = Project.objects.get(pk=project_id)

		long_lived_user_access_token = getLongLivedUserAccessToken(user_access_token)

		long_lived_page_access_token = getLongLivedPageAccessToken(user_id, long_lived_user_access_token, profile_id)

		newProfile = Profile(name=name, profile_id=profile_id, access_token=long_lived_page_access_token, network=network, project=project)
		newProfile.save()

		return profiles(request, project_id)
	else:
		return render(request, "project/new.html", {'data': request.method})


def insertTelegramProfile(request):

	if request.method == 'POST':

		name = request.POST['telegramChannelName']
		profile_id = request.POST['telegramChannelId']
		access_token = request.POST['telegramChanelAccessToken']
		project_id = request.POST['telegramProjectId']

		if name == '':
			return

		network = Network.objects.filter(name='Telegram')[0]
		project = Project.objects.get(pk=project_id)	

		newProfile = Profile(name=name, profile_id=profile_id, access_token=access_token, network=network, project=project)
		newProfile.save()

		return profiles(request, project_id)
	else:
		return render(request, "project/new.html", {'data': request.method})

def insertDiscordProfile(request):

	if request.method == 'POST':

		name = request.POST['discordChannelName']
		access_token = request.POST['discordChanelAccessToken']
		project_id = request.POST['discordProjectId']

		if name == '':
			return

		network = Network.objects.filter(name='Discord')[0]
		project = Project.objects.get(pk=project_id)	

		newProfile = Profile(name=name, access_token=access_token, network=network, project=project)
		newProfile.save()

		return profiles(request, project_id)
	else:
		return render(request, "project/new.html", {'data': request.method})

def insertInstagramProfile(request):

	if request.method == 'POST':

		name = request.POST['instagramChannelName']
		access_token = request.POST['instagramChanelAccessToken']
		project_id = request.POST['instagramProjectId']

		if name == '':
			return

		network = Network.objects.filter(name='Instagram')[0]
		project = Project.objects.get(pk=project_id)	

		newProfile = Profile(name=name, access_token=access_token, network=network, project=project)
		newProfile.save()

		return profiles(request, project_id)
	else:
		return render(request, "project/new.html", {'data': request.method})