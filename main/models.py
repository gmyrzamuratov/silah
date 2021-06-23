from django.db import models

from authentication.models import MyUser
from project.models import Project

class Timezone(models.Model):

	owner = models.ForeignKey(MyUser, null=False, blank=False, on_delete=models.CASCADE)
	timezone = models.CharField(max_length=200)

	def __str__(self):
		return self.timezone

class CurrentProject(models.Model):

	owner = models.ForeignKey(MyUser, null=False, blank=False, on_delete=models.CASCADE)
	project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Calendar(models.Model):

	owner = models.ForeignKey(MyUser, null=False, blank=False, on_delete=models.CASCADE)
	frame = models.CharField(max_length=250)