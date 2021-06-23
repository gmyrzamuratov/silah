from django.shortcuts import render
from django.conf import settings
import requests
import facebook
from requests_toolbelt import MultipartEncoder
import json
from project.models import Profile, Network
from post.models import Post, PostPhotos, PostVideos
from social_providers.models import PublishedPosts
from main.models import Timezone
import time
from .movie import Movie
from .telegram import Telegram
from .twitter import Twitter
from .discordly import Discordly
#from .insta import Instagram

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

import tweepy
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q

#from tweetsplitter import split_tweet

#https://developers.facebook.com/support/bugs/301152166901519/
# Create your views here.

def scheduler(request):

	profiles = Profile.objects.all()

	now = timezone.now()

	htmlCode = '<ul>'

	for profile in profiles:
		
		if profile.network.name == 'Google Calendar':

			posts = Post.objects.filter(Q(project=profile.project) & ~Q(publish_at=None)).exclude(id__in=PublishedPosts.objects.filter(profile=profile).values_list('post', flat=True))

			for post in posts:
				htmlCode += f'<li>{profile.network} - {post} - {post.publish_at}</li>'

				publishOnGoogleCalendar(post, profile)

				publishedPosts = PublishedPosts(post=post, profile=profile)
				publishedPosts.save()

		else:	

			posts = Post.objects.filter(Q(Q(publish_at__lte=now) | Q(publish_at=None)) & Q(project=profile.project) & Q (approved=1)).exclude(id__in=PublishedPosts.objects.filter(profile=profile).values_list('post', flat=True))

			for post in posts:
				htmlCode += f'<li>{profile.network} - {post} - {post.publish_at}</li>'

				publishedPosts = PublishedPosts(post=post, profile=profile)
				publishedPosts.save()

				if profile.network.name == 'Facebook':
					publishOnFacebook(post, profile)
				elif profile.network.name == 'Telegram':
					publishOnTelegram(post, profile)
				elif profile.network.name == 'Youtube':
					publishOnYoutube(post, profile)
				elif profile.network.name == 'Twitter':
					publishOnTwitter(post, profile)
				elif profile.network.name == 'Discord':
					publishOnDiscord(post, profile)
				#elif profile.network.name == 'Instagram':
				#	publishOnInstagram(post, profile)

	htmlCode += '</ul>'

	return HttpResponse(htmlCode)

def publishOnFacebook(post, profile):

	page_id = profile.profile_id
	access_token = profile.access_token
	graph = facebook.GraphAPI(access_token)

	message = post.content
	description = ''

	imagePath = ''

	imageList = []
	postImages = PostPhotos.objects.filter(post=post).order_by('order')
	for postImage in postImages:
		imagePath = str(settings.BASE_DIR)+postImage.photo.file.url
		#print(imagePath)
		photo_id = graph.put_photo(image=open(imagePath, 'rb'), published=False)
		imageList.append({'media_fbid': photo_id.get('id', '')})
		time.sleep(2)

	itHasError = False
	postVideos = PostVideos.objects.filter(post=post)
	for postVideo in postVideos:
		videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
		movie = Movie()
		videoPath = movie.getVideoPath(videoPath)
		#print(videoPath)
		#video_id = graph.put_video(video=open(videoPath, 'rb'), published=False)
		#graph.put_object(parent_object=page_id, connection_name="feed", message="This.", link="https://www.facebook.com")
		video_id = put_unpublishedvideo(videoPath, page_id, access_token, description, message)
		if video_id==-1:
			itHasError = True
			break
		#imageList.append({'media_fbid': video_id})
		time.sleep(2)
		#print(imageList)

	if itHasError == False:
		graph.put_object(parent_object=page_id, connection_name="feed", message=message, attached_media=json.dumps(imageList))

	return 1
	#return render(request, "project/new.html", {'data': request.method})

def put_unpublishedvideo(video_url, page_id, access_token, message):

	path = "{0}/videos".format(page_id)
	url = "https://graph-video.facebook.com/{0}?access_token={1}".format(path, access_token)
	files={'file':open(video_url,'rb')}
	result=requests.post(url, files=files, data={'title' : message, 'description': message, 'published': True})
	if (result.status_code == 200):
		j_res = result.json()
		facebook_video_id = j_res.get('id')
		return facebook_video_id
	else:
		print ("Facebook upload error: {0}".format(result.text))
		return -1;

	video_file_name=message[:50]
	local_video_file=video_url
	path = "{0}/videos".format(page_id)
	fb_url = "https://graph-video.facebook.com/{0}?access_token={1}".format(path, access_token)
	print(fb_url)

	m = MultipartEncoder(
		fields={'description': description,
		'title': message,
		'comment':'postvideo',
		'published':'false',
		'source': (video_file_name, open(local_video_file, 'rb'), 'video/mp4')})

	#print(m.content_type)

	r = requests.post(fb_url,headers={'Content-Type': m.content_type},data=m)
	if (r.status_code == 200):
		j_res = r.json()
		facebook_video_id = j_res.get('id')
		print ("facebook_video_id = {0}".format(facebook_video_id))
	else:
		print ("Facebook upload error: {0}".format(r.text))


def publishOnTelegram(post, profile):

	channel_id = profile.profile_id
	access_token = profile.access_token

	message = post.content

	#telegramClient = Telegram()
	Telegram.sendMessage(access_token, channel_id, message)
	description = ''

	imageList = []
	postImages = PostPhotos.objects.filter(post=post).order_by('order')
	for postImage in postImages:
		imagePath = str(settings.BASE_DIR)+postImage.photo.file.url
		print(imagePath)
		Telegram.sendPhoto(access_token, channel_id, imagePath)
		time.sleep(2)

	videoList = []
	postVideos = PostVideos.objects.filter(post=post)
	for postVideo in postVideos:
		videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
		movie = Movie()
		videoPath = movie.getVideoPath(videoPath)
		print(videoPath)
		Telegram.sendVideo(access_token, channel_id, videoPath)
		time.sleep(2)

	#return render(request, "project/new.html", {'data': request.method})

def publishOnGoogleCalendar(post, profile):

	project = post.project

	channel_id = profile.profile_id
	access_token = profile.access_token

	message = post.content

	description = ''


	#scopes = profile.scopes
	#scopes = scopes.replace('[', '')
	#scopes = scopes.replace(']', '')
	#scopes = scopes.split(',')

	crdt = Credentials(
		token=profile.access_token, 
		refresh_token=profile.refresh_token, 
		id_token=profile.id_token, 
		token_uri=profile.token_uri, 
		client_id=profile.client_id, 
		client_secret=profile.client_secret, 
		scopes=settings.GCALENDAR_UPLOAD_SCOPE)

	if crdt and crdt.expired and crdt.refresh_token:
		crdt.refresh(Request())

		profile.access_token=crdt.token, 
		profile.refresh_token=crdt.refresh_token,
		profile.id_token=crdt.id_token,
		profile.token_uri=crdt.token_uri,
		profile.client_id=crdt.client_id,
		profile.client_secret=crdt.client_secret,
		profile.scopes=crdt.scopes
		profile.save()
		

	service = build('calendar', 'v3', credentials=crdt)

	start = post.publish_at.isoformat()
	end = (post.publish_at + timedelta(hours=1)).isoformat()

	timezoneList = Timezone.objects.filter(owner=project.owner)

	userTimezone = 'UTC'
	if len(timezoneList) > 0:
		userTimezone = timezoneList[0].timezone

	print(f'Timezone={userTimezone}')

	event_result = service.events().insert(calendarId='primary',
		body={
		"summary": post.content[0:50],
		"description": post.content,
		"start": {"dateTime": start, "timeZone": userTimezone},
		"end": {"dateTime": end, "timeZone": userTimezone},
		}
	).execute()

	print(f'event ID=')
	print(event_result['id'])

	return HttpResponse('')

def publishOnYoutube(post, profile):

	channel_id = profile.profile_id
	access_token = profile.access_token

	message = post.content

	description = ''

	scopes = profile.scopes
	#scopes = scopes.replace('[', '')
	#scopes = scopes.replace(']', '')
	#scopes = scopes.split(',')

	crdt = Credentials(
		token=profile.access_token, 
		refresh_token=profile.refresh_token, 
		id_token=profile.id_token, 
		token_uri=profile.token_uri, 
		client_id=profile.client_id, 
		client_secret=profile.client_secret, 
		scopes=settings.YOUTUBE_UPLOAD_SCOPE)

	if crdt and crdt.expired and crdt.refresh_token:
		crdt.refresh(Request())

		profile.access_token=crdt.token, 
		profile.refresh_token=crdt.refresh_token,
		profile.id_token=crdt.id_token,
		profile.token_uri=crdt.token_uri,
		profile.client_id=crdt.client_id,
		profile.client_secret=crdt.client_secret,
		profile.scopes=crdt.scopes
		profile.save()
		

	service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, credentials=crdt)

	postVideos = PostVideos.objects.filter(post=post)
	for postVideo in postVideos:
		videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
		movie = Movie()
		videoPath = movie.getVideoPath(videoPath)

		mediaFile = MediaFileUpload(videoPath)

		request_body = {
		'snippet': {
		'categoryI': 19,
		'title': post.content[0:50],
		'description': post.content,
		'tags': []
		},
		'status': {
		'privacyStatus': 'public',
		#'publishAt': upload_date_time,
		'selfDeclaredMadeForKids': False, 
		},
		'notifySubscribers': False
		}

		response_upload = service.videos().insert(
			part='snippet,status',
			body=request_body,
			media_body=mediaFile
		).execute()

		time.sleep(2)


def publishOnTwitter(post, profile):

	photoPerTweet = 2

	twitter = Twitter()

	"""
	tweetId = None
	tweet = "Hi, Sazalem"
	status = twitter.publish(profile, tweetId, tweet)

	tweetId = status.id
	tweet = "How are you?"
	status = twitter.publish(profile, tweetId, tweet)

	return"""

	tweet = post.content
	tweets = twitter.splitMessage(profile.name, tweet)

	#print(tweets)

	#return

	imageList = []
	postImages = PostPhotos.objects.filter(post=post).order_by('order')

	ind = 0
	for postImage in postImages:
		imagePath = str(settings.BASE_DIR)+postImage.photo.file.url
		upload_result = twitter.uploadImage(profile, imagePath)
		imageList.append(upload_result.media_id_string)
		time.sleep(2)
		ind += 1

	videoList = []
	if len(imageList) == 0:
		postVideos = PostVideos.objects.filter(post=post)

		for postVideo in postVideos:
			videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
			movie = Movie()
			videoPath = movie.getVideoPath(videoPath)
			upload_result = twitter.uploadVideo(profile, videoPath)
			print(upload_result)
			videoList.append(upload_result.media_id_string)
			time.sleep(2)

	if len(tweet) <= settings.TWITTER_MAX_SYMBOL_COUNT:

		if len(imageList) > 0:

			if len(imageList) > photoPerTweet:

				tempImageList = []
				for x in range(0, len(imageList)):
					print(imageList[x])
					tempImageList.append(imageList[x])
					if len(tempImageList) == photoPerTweet:
						twitter.publish(profile, None, "", tempImageList)
						tempImageList = []

				if len(tempImageList) > 0:
					twitter.publish(profile, None, tweet, tempImageList)
			else:
				twitter.publish(profile, None, tweet, imageList)
		elif len(videoList) > 0:
			twitter.publish(profile, None, tweet, None, videoList)
		else:
			twitter.publish(profile, None, tweet)

	else:

		tweets = twitter.splitMessage(profile.name, tweet)
		#tweets.reverse()

		publishMedia = True

		splittedImageList = []

		if len(imageList) > photoPerTweet:

			tempImageList = []
			for x in range(0, len(imageList)):
				print(imageList[x])
				tempImageList.append(imageList[x])
				if len(tempImageList) == photoPerTweet:
					splittedImageList.append(tempImageList)
					tempImageList = []

			if len(tempImageList) > 0:
				splittedImageList.append(tempImageList)
		else:
			splittedImageList.append(imageList)

		"""
		if len(tweets) < len(splittedImageList):
			index = len(tweets)
			for x in range(index, len(splittedImageList)):
				print("publish images")
				print(splittedImageList[x])
				twitter.publish(profile, "", splittedImageList[x])"""

		print(tweets)

		index = 0
		tweetId = None
		for tweet in tweets:

			#tweet = tweet.replace('\r', '')

			if tweet == '':
				continue

			if len(splittedImageList) > 0 and len(splittedImageList) > index:
				status = twitter.publish(profile, tweetId, tweet, splittedImageList[index])
			elif len(videoList) > 0 and publishMedia:
				status = twitter.publish(profile, tweetId, tweet, None, videoList)
			else:
				print(f'{index} - {tweet}')
				status = twitter.publish(profile, tweetId, tweet)

			tweetId = status.id

			index = index + 1
			publishMedia = False
			time.sleep(5)

def publishOnDiscord(post, profile):

	access_token = profile.access_token
	#url = 'https://discord.com/api/webhooks/773590010027966464/slOJjzNToSRFc47a1Q2VBmI0Na-jeRFDBbTKgGSQY108itcELVf1U8tahbwnDLOwUMP5'

	#post = Post.objects.get(pk=30)
	postImages = PostPhotos.objects.filter(post=post).order_by('order')

	imageList = []
	for postImage in postImages:
		imagePath = str(settings.BASE_DIR)+postImage.photo.file.url
		imageList.append(imagePath)

	videoList = []
	if len(imageList) == 0:
		postVideos = PostVideos.objects.filter(post=post)

		for postVideo in postVideos:
			videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
			movie = Movie()
			videoPath = movie.getVideoPath(videoPath)
			videoList.append(videoPath)

	Discordly.sendMessage(access_token, post.content, imageList, videoList)
"""
def publishOnInstagram(post, profile):

	access_token = profile.access_token

	postImages = PostPhotos.objects.filter(post=post).order_by('order')

	imageList = []
	for postImage in postImages:
		imagePath = str(settings.BASE_DIR)+postImage.photo.file.url
		imageList.append(imagePath)

	videoList = []
	if len(imageList) == 0:
		postVideos = PostVideos.objects.filter(post=post)

		for postVideo in postVideos:
			videoPath = str(settings.BASE_DIR)+postVideo.video.file.url
			movie = Movie()
			videoPath = movie.getVideoPath(videoPath)
			videoList.append(videoPath)

	Instagram.sendMessage(profile, post.content, imageList, videoList)
"""