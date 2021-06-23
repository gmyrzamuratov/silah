from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'project'

urlpatterns = [
	path('list/', views.list, name='list'),	
	path('new/', views.new, name='new'),
	path('detail/<int:id>', views.detail, name='detail'),
	path('edit/<int:id>', views.edit, name='edit'),
	path('insert/', views.insert, name='insert'),
	path('update/', views.update, name='update'),
	path('profiles/<int:id>', views.profiles, name='profiles'),
	path('addsocialnetwork/<int:id>', views.addsocialnetwork, name='addsocialnetwork'),
	path('insertprofile', views.insertprofile, name='insertprofile'),
	path('insertTelegramProfile', views.insertTelegramProfile, name='insertTelegramProfile'),
	path('insertDiscordProfile', views.insertDiscordProfile, name='insertDiscordProfile'),
	path('insertInstagramProfile', views.insertInstagramProfile, name='insertInstagramProfile'),
	path('youtubeauthorize/<int:id>', views.youtubeauthorize, name='youtubeauthorize'),
	path('youtubeoauth2callback', views.youtubeoauth2callback, name='youtubeoauth2callback'),
	path('googlecalendarauthorize/<int:id>', views.googlecalendarauthorize, name='googlecalendarauthorize'),
	path('gcalendaroauth2callback', views.gcalendaroauth2callback, name='gcalendaroauth2callback'),
	path('twitter_login/<int:id>', views.twitter_login, name='twitter_login'),
	path('twitter_callback', views.twitter_callback, name='twitter_callback'),
	path('hootsuite_authorize/<int:id>', views.hootsuite_authorize, name='hootsuite_authorize'),
	path('hootsuite_callback', views.hootsuite_callback, name='hootsuite_callback'),	
]