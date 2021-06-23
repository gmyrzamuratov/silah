from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'post'

urlpatterns = [
	path('list/<int:id>', views.list, name='list'),	
	path('new/<int:id>', views.new, name='new'),
	path('edit/<int:id>', views.edit, name='edit'),
	path('detail/<int:id>', views.detail, name='detail'),
	path('insert/', views.insert, name='insert'),
	path('update/', views.update, name='update'),
	path('uploadphoto/', views.uploadPhoto, name='uploadPhoto'),
	path('uploadFileFromURL/', views.uploadFileFromURL, name='uploadFileFromURL'),
	path('uploadphotodata/', views.uploadPhotoData, name='uploadPhotoData'),
	path('uploadvideo/', views.uploadVideo, name='uploadVideo'),
	path('getragicimages/<path:collection>/<int:position>/<str:searchQuery>', views.getRagicImages, name='getRagicImages'),
	path('getragicimages/<path:collection>/<int:position>', views.getRagicImages, name='getRagicImages'),
	path('getWordpressImages/<int:position>', views.getWordpressImages, name='getWordpressImages'),
	path('getWordpressImages/<int:position>/<str:searchQuery>', views.getWordpressImages, name='getWordpressImages'),
	path('check/', views.check, name='check'),
	path('getWordpressPosts/', views.getWordpressPosts, name='getWordpressPosts'),
	path('getAWSImages/<int:position>', views.getAWSImages, name='getAWSImages'),
	path('getAWSImages/<int:position>/<str:searchQuery>', views.getAWSImages, name='getAWSImages')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)