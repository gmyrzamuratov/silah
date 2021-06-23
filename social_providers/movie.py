import os
import moviepy.editor as moviepy
from post.models import PostVideos
from django.conf import settings

class Movie:

	def getVideoPath(this, path):

		filename, file_extension = os.path.splitext(path)

		if file_extension == ".mpeg":
			return filename+".mp4"
		else:
			return path

	def convertVideo(this, path):

		filename, file_extension = os.path.splitext(path)

		print(file_extension)

		if file_extension == ".mpeg":
			print("Begin to convert")
			if os.path.exists(filename+".mp4") !=True:
				clip = moviepy.VideoFileClip(path)
				clip.write_videofile(filename+".mp4")

			if os.path.exists(filename+".mp4"):
				return True
			else:
				return False

		else:
			print("No need to convert")
			return True

	def convertVideos(this, post):

		allVideosConverted = True
		postVideos = PostVideos.objects.filter(post=post)
		for postVideo in postVideos:
			videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
			if this.convertVideo(videoPath)!=True:
				allVideosConverted = False

		return allVideosConverted