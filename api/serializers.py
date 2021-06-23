from rest_framework import serializers

from post.models import Post
from project.models import Project

class ProjectSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Project
		fields = ('id', 'title')

class PostSerializer(serializers.Serializer):

	content = serializers.CharField()
	project = serializers.IntegerField(
        required=True)
	publish_at = serializers.DateTimeField(allow_null=True)

class PostPhotosSerializer(serializers.Serializer):

	post = serializers.IntegerField(
        required=True)
	photo = serializers.IntegerField(
        required=True)
	order = serializers.IntegerField()