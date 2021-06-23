from django.contrib import admin
from .models import PublishedPosts

# Register your models here.
class PublishedPostsAdmin(admin.ModelAdmin):
	list_display = ('id', 'profile', 'post')
	fields = ('profile', 'post')

admin.site.register(PublishedPosts, PublishedPostsAdmin)