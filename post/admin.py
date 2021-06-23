from django.contrib import admin
from .models import Post, Photo, PostPhotos, PostVideos, ProjectForWordpress, WordpressPosts

class PostAdmin(admin.ModelAdmin):
	list_display = ('id', 'content', 'project', 'publish_at', 'approved')
	fields = ('content','project','publish_at', 'approved')

admin.site.register(Post, PostAdmin)
admin.site.register(Photo)
admin.site.register(PostPhotos)
admin.site.register(PostVideos)
admin.site.register(ProjectForWordpress)
admin.site.register(WordpressPosts)