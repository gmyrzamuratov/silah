from django.db import models
from project.models import Network, Profile
from post.models import Post

# Create your models here.
class PublishedPosts(models.Model):

	post = models.ForeignKey(Post, null=False, blank=False, on_delete=models.CASCADE)
	profile = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
	published_at = models.DateTimeField(auto_now_add=True)