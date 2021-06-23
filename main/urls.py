from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'main'

urlpatterns = [
	path('', views.index, name='index'),	
	path('calendar/', views.calendar, name='calendar'),	
	path('calendar/add', views.add_calendar, name='add_calendar'),
	path('insert_calendar', views.insert_calendar, name='insert_calendar'),
	path('set_timezone/', views.set_timezone, name='set_timezone'),
	path('privacy-policy/', views.privacyPolicy, name='privacyPolicy'),
	path('api/', include('api.urls'))
]