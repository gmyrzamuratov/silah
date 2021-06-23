from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'social_providers'

urlpatterns = [
	#path('publish/', views.publish, name='publish'),
	#path('publishOnTelegram/', views.publishOnTelegram, name='publishOnTelegram'),
	#path('publishOnYoutube/', views.publishOnYoutube, name='publishOnYoutube'),
	#path('publishOnTwitter/', views.publishOnTwitter, name='publishOnTwitter'),
	path('scheduler/', views.scheduler, name='scheduler'),
	path('publishOnDiscord/', views.publishOnDiscord, name='publishOnDiscord')
	#path('publishOnGoogleCalendar/', views.publishOnGoogleCalendar, name='publishOnGoogleCalendar')
]