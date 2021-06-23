from django.db import models
from project.models import Project
import os
from datetime import datetime

# Create your models here.
def get_image_upload_path(instance, filename):
	_now = datetime.now()
	return "images/{year}/{month}/{day}/{filename}".format(year=_now.strftime('%Y'), month=_now.strftime('%m'), day=_now.strftime('%d'), filename=filename)

def get_video_upload_path(instance, filename):
	_now = datetime.now()
	return "videos/{year}/{month}/{day}/{filename}".format(year=_now.strftime('%Y'), month=_now.strftime('%m'), day=_now.strftime('%d'), filename=filename)

class Post(models.Model):

	content = models.TextField()
	project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)
	publish_at = models.DateTimeField(auto_now_add=False, null=True)
	approved = models.IntegerField()

	def __str__(self):
		return self.content

class Video(models.Model):

    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=get_video_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Photo(models.Model):

    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to=get_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class PostPhotos(models.Model):

	post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
	photo = models.ForeignKey(Photo, default=None, on_delete=models.CASCADE)
	order = models.IntegerField()

class PostVideos(models.Model):

	post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
	video = models.ForeignKey(Video, default=None, on_delete=models.CASCADE)

class ProjectForWordpress(models.Model):

	project = models.ForeignKey(Project, null=False, blank=False, on_delete=models.CASCADE)

	def __str__(self):
		return self.project.title

class WordpressPosts(models.Model):

	post_id = models.IntegerField()

	def __str__(self):
		return f'{self.post_id}'