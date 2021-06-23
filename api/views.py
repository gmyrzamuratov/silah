from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response

from .serializers import PostSerializer, ProjectSerializer, PostPhotosSerializer
from post.models import Post, PostPhotos, Photo
from project.models import Project

class PostCreate(generics.CreateAPIView):

    serializer_class = PostSerializer

    def post(self, request):

    	# 2021-01-29T23:30:00+06:00
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.data.get('content', None)
        project = serializer.data.get('project', 0)
        publish_at = serializer.data.get('publish_at', None)
        photos = serializer.data.get('photos', '')

        currentProject = Project.objects.filter(id=project)
        if len(currentProject) == 0:
            return Response({
                "error": {
                    "details": "Project not found"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        newPost = Post(content=content, project=currentProject[0], publish_at=publish_at, approved=0)
        newPost.save()

        listPhotos = photos.split(',')

        index = 0
        for photoId in listPhotos:
            if photoId == '':
                continue
            photo = Photo.objects.get(pk=photoId)
            newPostPhoto = PostPhotos(post=newPost, photo=photo, order=index)
            newPostPhoto.save()
            index = index + 1

        
        data = {
            'id': newPost.id,
            'content': content
        }

        return Response(status=status.HTTP_200_OK, data=data)

class PostPhotoCreate(generics.CreateAPIView):

    serializer_class = PostPhotosSerializer

    def post(self, request):

    	# 2021-01-29T23:30:00+06:00
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        postId = serializer.data.get('post', None)
        photoId = serializer.data.get('photo', None)
        order = serializer.data.get('order', 0)

        currentPhoto = Photo.objects.filter(id=photoId)
        if len(currentPhoto) == 0:
            return Response({
                "error": {
                    "details": "Photo not found"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        currentPost = Post.objects.filter(id=postId)
        if len(currentPost) == 0:
            return Response({
                "error": {
                    "details": "Post not found"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        newPhoto = PostPhotos(photo=currentPhoto[0], post=currentPost[0], order=order)
        newPhoto.save()
        
        data = {
            'id': newPhoto.id
        }

        return Response(status=status.HTTP_200_OK, data=data)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer