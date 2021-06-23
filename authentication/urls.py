from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'authentication'

urlpatterns = [
	path('signup/', views.signup, name='signup'),
	path('signin/', views.signin, name='signin'),
	path('login/', views.login, name='login'),
	path('logout/', auth_views.LogoutView.as_view(), name='logout'),
	path('registration/', views.registration, name='registration'),
]