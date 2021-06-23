from django.db import models
#from django.contrib.auth.models import User
from authentication.models import MyUser

# Create your models here.

class Project(models.Model):

	title = models.CharField(max_length=200)
	owner = models.ForeignKey(MyUser, null=False, blank=False, on_delete=models.CASCADE)

	def __str__(self):
		return self.title

class Network(models.Model):

	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name
		
class Profile(models.Model):

	name = models.CharField(max_length=200)
	profile_id = models.CharField(max_length=200)
	project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
	network = models.ForeignKey(Network, null=False, blank=False, on_delete=models.CASCADE)
	access_token = models.CharField(max_length=200, default='')
	refresh_token = models.CharField(max_length=200, default='', null=True)
	id_token = models.CharField(max_length=200, default='', null=True)
	token_uri = models.CharField(max_length=200, default='')
	client_id = models.CharField(max_length=200, default='')
	client_secret = models.CharField(max_length=200, default='')
	scopes = models.CharField(max_length=200, default='')

	def __str__(self):
		return self.project.title + ' ' + self.network.name + ' ' + self.name