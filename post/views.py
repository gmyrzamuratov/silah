from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Post, Photo, PostPhotos, Video, PostVideos, ProjectForWordpress, WordpressPosts
from project.models import Project
from .forms import newForm, editForm, PhotoForm, VideoForm
import base64
from django.conf import settings
import os
from django.core.files.base import ContentFile
import requests
from django.http import HttpResponse
import re
from datetime import datetime
from urllib.parse import unquote
from social_providers.movie import Movie
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pymysql

# Create your views here.
def list(request, id):

	posts = Post.objects.filter(project=id)
	context = {
	'project': id,
	'posts': posts
	}

	return render(request, "post/list.html", context)

def new(request, id):

	intial = {
	'project': id
	}

	#form = editForm(intial, instance=data)
	form = newForm(intial)

	context = {
	'form': form,
	}

	return render(request, "post/new.html", context)

def edit(request, id):

	post = Post.objects.get(pk=id)
	postPhotos = PostPhotos.objects.filter(post=post).order_by('order')
	photoURL=''
	photos = ''
	for photo in postPhotos:
		photoURL = photo.photo.file.url
		if photos == '':
			photos = str(photo.photo.id)
		else:
			photos = photos + ',' + str(photo.photo.id)			

	postVideos = PostVideos.objects.filter(post=post)
	videoURL=''
	videos = ''
	for video in postVideos:
		videoURL = video.video.file.url
		if videos == '':
			videos = str(video.video.id)
		else:
			videos = videos + ',' + str(video.video.id)			

	intial = {
	'id': id,
	'content': post.content,
	'photos': photos,
	'videos': videos,
	'publish_at': post.publish_at
	}

	#form = editForm(intial, instance=data)
	form = editForm(intial)

	context = {
	'form': form,
	'postPhotos': postPhotos,
	'postVideos': postVideos,
	'photoURL': photoURL
	}

	return render(request, "post/edit.html", context)

def detail(request, id):

	post = Post.objects.get(pk=id)
	postPhotos = PostPhotos.objects.filter(post=post).order_by('order')
	postVideos = PostVideos.objects.filter(post=post)
	context = {
	'data': post,
	'photos': postPhotos,
	'videos': postVideos
	}

	return render(request, "post/detail.html", context)

def check(request):

	movie = Movie()

	posts = Post.objects.filter(approved=0)

	for post in posts:
		if movie.convertVideos(post):
			post.approved = 1
			post.save()

	return HttpResponse("Test")

# API -----------------------------------------------------------------------------
# Functions
def insert(request):

	if request.method == 'POST':

		form = newForm(request.POST)

		if(form.is_valid()):

			content = form.cleaned_data['content']
			photos  = form.cleaned_data['photos']
			videos  = form.cleaned_data['videos']
			projectId = form.cleaned_data['project']
			publish_at  = form.cleaned_data['publish_at']

			if content == '':
				return

			project = Project.objects.get(pk=projectId)

			newPost = Post(content=content, project=project, publish_at=publish_at, approved=0)
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

			listVideos = videos.split(',')

			for videoId in listVideos:
				if videoId == '':
					continue
				video = Video.objects.get(pk=videoId)
				newPostVideo = PostVideos(post=newPost, video=video)
				newPostVideo.save()

			return redirect('post:list', id=projectId)
		else:
			print(form.errors)
			return render(request, "post/new.html", {'data': request.method})

	else:
		return render(request, "post/new.html", {'data':request.method})

def update(request):

	if request.method == 'POST':

		form = editForm(request.POST)

		if(form.is_valid()):

			id      = form.data['id']
			content = form.cleaned_data['content']
			photos  = form.cleaned_data['photos']
			videos  = form.cleaned_data['videos']
			publish_at  = form.cleaned_data['publish_at']

			try:
				post = Post.objects.get(pk=id)
				post.content = content
				post.publish_at = publish_at
				post.approved = 0
				post.save()
			except Post.DoesNotExist:
				raise Http404(f"We can't find post with id={id}")

			PostPhotos.objects.filter(post=post).delete()

			index = 0
			if photos!='':
				listPhotos = photos.split(',')

				for photoId in listPhotos:
					photo = Photo.objects.get(pk=photoId)
					newPostPhoto = PostPhotos(post=post, photo=photo, order=index)
					newPostPhoto.save()

					index = index + 1

			PostVideos.objects.filter(post=post).delete()
			if videos!='':
				listVideos = videos.split(',')

				for videoId in listVideos:
					video = Video.objects.get(pk=videoId)
					newPostVideo = PostVideos(post=post, video=video)
					newPostVideo.save()

			return redirect('post:detail', id=id)

	else:
		return render(request, "post/edit.html", {'data':request.method})

def getFilename_fromCd(cd):

	if not cd:
		return None

	fname = re.findall('filename=(.+)', cd)

	if len(fname) == 0:
		return None

	fileName = fname[0]
	fileName = fileName[1:]
	fileName = fileName[:-1]
	return fileName

def uploadPhoto(request):

	form = PhotoForm(request.POST, request.FILES)

	if form.is_valid():
		photo = form.save()
		data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'id': photo.id}
	else:
		data = {'is_valid': False}

	return JsonResponse(data)

def uploadFileFromURL(request):

	#return None
	url = request.POST['url']

	print('----------------------------------')
	print(url)

	media_root = settings.MEDIA_ROOT
	
	#url = 'https://www.ragic.com/sims/file.jsp?a=SilahReport&f=E6hadeij5n@image1.jpg'
	r = requests.get(url, allow_redirects=True)
	#print('----------------------------------')
	#print(r.headers.get('content-disposition'))
	#imageFilename = getFilename_fromCd(r.headers.get('content-disposition'))
	a = urlparse(url)
	imageFilename = os.path.basename(a.path)
	
	now = datetime.now()
	d = now.strftime("%m%d%Y%H%M%S")
	print(d)
	print(imageFilename)
	imageFilename = d + imageFilename

	imageFileFullPath = media_root+'/images/'+imageFilename
	print(imageFilename)
	print(imageFileFullPath)
	open(imageFileFullPath, 'wb').write(r.content)

	photo = Photo()
	photo.file = '/images/'+imageFilename
	# Save the article
	photo.save()

	#photo.file = '/images/' + imageFilename
	#photo.file.name = '/images/' + imageFilename
	#photo.save()
	data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'id': photo.id}
	
	return JsonResponse(data)	

def uploadPhotoData(request):

	imageStream = request.POST['imageStream']
	imageId = request.POST['imageId']
	imageFilename = request.POST['imageFilename']

	if imageStream != '':
		image_array = imageStream.split(';')
		pre_extension = image_array[0]
		image_array = image_array[1].split(',')

		extension = pre_extension.split('/')[1]
		print('extension=' + extension)

		imgdata = base64.b64decode(image_array[1])
		media_root = settings.MEDIA_ROOT

		if extension == 'jpeg':
			extension = 'jpg'

		imageFilename = imageFilename.replace('.jpg', '')		
		imageFilename = imageFilename.replace('.png', '')
		imageFilename = imageFilename.replace('.jpeg', '')
		imageFilename = '/'+imageFilename+'.'+extension

		image = ContentFile(imgdata, os.path.basename(media_root+imageFilename))

	photo = Photo.objects.get(pk=imageId)
	photo.file = image
	photo.save()

	data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'id': photo.id}
	
	return JsonResponse(data)

def uploadVideo(request):

	form = VideoForm(request.POST, request.FILES)

	if form.is_valid():
		video = form.save()
		data = {'is_valid': True, 'name': video.file.name, 'url': video.file.url, 'id': video.id}
	else:
		data = {'is_valid': False}

	return JsonResponse(data)

def getRagicImages(request, collection, position, searchQuery=None):

	collection = collection.replace('_', '/')

	if searchQuery==None:
		url = f'https://www.ragic.com/SilahReport/{collection}/?v=3&limit={position*5},5&api'
	else:
		url = f'https://www.ragic.com/SilahReport/{collection}/?v=3&limit={position*5},5&fts={searchQuery}&api'

	print(url)

	result=requests.get(url, headers={'Authorization': f'Basic {settings.RAGIC_TOKEN}'})

	imageFolder = 'https://www.ragic.com/sims/file.jsp?a=SilahReport&f='
	
	data = []
	if (result.status_code == 200):
		jsonData = result.json()
		for item in jsonData:
			post = jsonData[item]
			_id = post['_ragicId']
			_collectionId = ''

			images = []
			for index in post:
				if 'Collection ID' in index:
					_collectionId = post[index]
				else:
					value = post[index]
					if type(value) is str:
						ext = value[-3:]

						if ext=='jpg':
							images.append(imageFolder+value)

						ext = value[-4:]
						if ext=='jpeg':
							images.append(imageFolder+value)

			"""
			_primaryImage = post['Primary Image']
			_secondaryImage = post['Secondary Image']

			images = []
			if _primaryImage!='':
				images.append(imageFolder+_primaryImage)
			else:
				images.append('')

			if _secondaryImage!='':
				images.append(imageFolder+_secondaryImage)
			else:
				images.append('')

			for image in post:
				if 'Image ' in image:
					if post[image] != '':
						_thirdImage = imageFolder+post[image]
						images.append(_thirdImage)
			"""

			data.append({'id' : _id, 'collectionID': _collectionId, 'images' : images})

	return JsonResponse({'data' : data})

def getWordpressImages(request, position, searchQuery=None):

	if searchQuery==None:
		url = f'https://silahreport.com/wp-json/wp/v2/posts/?page={position}'
	else:
		url = f'https://silahreport.com/wp-json/wp/v2/posts/?page={position}&search={searchQuery}'

	print(url)

	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

	result=requests.get(url, headers=headers)

	#print(result.content)

	data = []
	if (result.status_code == 200):
		jsonData = result.json()
		for post in jsonData:
			_id = post['id']
			_content = post['content']

			images = []
			links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(_content))
			for link in links:
				print(link)
				pos = link.find('.jpg')
				print(pos)
				if (pos != -1):
					link = link[:pos+4]
					if link not in images:
						images.append(link)

				pos = link.find('.png')
				if (pos != -1):
					link = link[:pos+4]
					if link not in images:
						images.append(link)

				print(link)

			data.append({'id' : _id, 'images': images})

	else:
		print(result.status_code)

	return JsonResponse({'data' : data})

def uploadImageFromWordpress(url):

	media_root = settings.MEDIA_ROOT
	
	#url = 'https://www.ragic.com/sims/file.jsp?a=SilahReport&f=E6hadeij5n@image1.jpg'
	r = requests.get(url, allow_redirects=True)
	#print('----------------------------------')
	#print(r.headers.get('content-disposition'))
	#imageFilename = getFilename_fromCd(r.headers.get('content-disposition'))
	a = urlparse(url)
	imageFilename = os.path.basename(a.path)
	
	now = datetime.now()
	d = now.strftime("%m%d%Y%H%M%S")
	print(d)
	print(imageFilename)
	imageFilename = d + imageFilename

	imageFileFullPath = media_root+'/images/'+imageFilename
	print(imageFilename)
	print(imageFileFullPath)
	open(imageFileFullPath, 'wb').write(r.content)

	photo = Photo()
	photo.file = '/images/'+imageFilename
	# Save the article
	photo.save()

	return photo	

def getWordpressPosts(request):

	url = 'https://silahreport.com/wp-json/wp/v2/posts/?page=1'

	#print(url)

	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

	Projects = ProjectForWordpress.objects.all()
	if len(Projects) > 0:
		project = Projects[0].project
		#print(project.title)
	else:
		return HttpResponse("You didn't set project for wordpress")

	result=requests.get(url, headers=headers)

	if (result.status_code == 200):
		jsonData = result.json()
		for post in jsonData:
			_id = post['id']

			posts = WordpressPosts.objects.filter(post_id=_id)

			if len(posts) > 0:
				continue

			'''if _id < 7780:
				newPost = WordpressPosts()
				newPost.post_id = _id
				newPost.save()
				continue'''

			newPost = WordpressPosts()
			newPost.post_id = _id
			newPost.save()
			
			postData = post['content']
			htmlCode = post['content']['rendered']
			_title = post['title']['rendered']
			soup = BeautifulSoup(htmlCode)
			_content = soup.get_text()
			_link = post['link']

			images = []
			links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(postData))
			for link in links:
				if len(images)>=4:
					break
				#print(link)
				pos = link.find('.jpg')
				#print(pos)
				if (pos != -1):
					link = link[:pos+4]
					if link not in images:
						images.append(link)

				pos = link.find('.png')
				if (pos != -1):
					link = link[:pos+4]
					if link not in images:
						images.append(link)

				#print(link)

			words = _title.split(' ')
			wordCount = 1
			_postText = 'Just Published-'
			for word in words:
				wordCount+=1
				if wordCount > 200:
					break

				_postText = _postText + ' ' + word					

			_postText = _postText + '\n\n'

			words = _content.split(' ')
			for word in words:
				wordCount+=1
				if wordCount > 200:
					break

				_postText = _postText + ' ' + word					

			_postText = _postText + '...\n\n' + _link

			_postText = _postText.replace('&#8216;', '\'')
			_postText = _postText.replace('&#8217;', '\'')

			newPost = Post(content=_postText, project=project, publish_at=datetime.now(), approved=0)
			newPost.save()

			print(images)

			index = 0
			for imageUrl in images:
				print('----------------')
				print(imageUrl)
				photo = uploadImageFromWordpress(imageUrl)
				newPostPhoto = PostPhotos(post=newPost, photo=photo, order=index)
				newPostPhoto.save()
				index = index + 1

			break
	else:
		print(result.status_code)

	return HttpResponse("Test")

def isNumber(value):

	result = False
	try:
		tmp = int(value)
		result = True
	except:
		result = False

	return result

def getAWSImages(request, position, searchQuery=None):

	connection = pymysql.connect(host=settings.AWS_HOST, port=settings.AWS_PORT, user=settings.AWS_USER, passwd=settings.AWS_PASSWORD, db=settings.AWS_DB)

	curCollections = connection.cursor()

	print(f"SELECT * FROM collections WHERE id = {searchQuery} OR SRCollectionID LIKE '%{searchQuery}%' OR ReferenceName LIKE '%{searchQuery}%' OR model LIKE '%{searchQuery}%' OR receiver_markings LIKE '%{searchQuery}%' OR general_notes_on_item LIKE '%{searchQuery}%' ORDER BY id DESC LIMIT {position*5}, 5")

	if searchQuery==None:
		curCollections.execute(f"SELECT * FROM collections ORDER BY id DESC LIMIT {position*5}, 5")
	elif isNumber(searchQuery):
		#print('number')
		curCollections.execute(f"SELECT * FROM collections WHERE id = {searchQuery} OR SRCollectionID LIKE '%{searchQuery}%' OR ReferenceName LIKE '%{searchQuery}%' OR model LIKE '%{searchQuery}%' OR receiver_markings LIKE '%{searchQuery}%' OR general_notes_on_item LIKE '%{searchQuery}%' ORDER BY id DESC LIMIT {position*5}, 5")
	else:
		#print('not number')
		curCollections.execute(f"SELECT * FROM collections WHERE SRCollectionID LIKE '%{searchQuery}%' OR ReferenceName LIKE '%{searchQuery}%' OR model LIKE '%{searchQuery}%' OR receiver_markings LIKE '%{searchQuery}%' OR general_notes_on_item LIKE '%{searchQuery}%' ORDER BY id DESC LIMIT {position*5}, 5")
	"""	 ORDER BY id DESC LIMIT {position*5}, 5")"""

	data = []
	for rowCollection in curCollections:
		_id = rowCollection[0]
		print("HAHA")

		images = []
		curImages = connection.cursor()
		curImages.execute(f"SELECT * FROM media WHERE collections_id = {_id}")

		for rowImage in curImages:
			images.append(rowImage[4])

		curCollections.close()
		data.append({'id': _id, 'images': images})


	curCollections.close()
	connection.close()

	return JsonResponse({'data' : data})