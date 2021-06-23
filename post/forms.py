from django import forms
from .models import Post, Photo, Video

class newForm(forms.Form):

    project = forms.IntegerField(widget=forms.HiddenInput)
    photos = forms.CharField(widget=forms.HiddenInput, required=False)
    videos = forms.CharField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='Content', widget=forms.Textarea(attrs={'class' : 'form-control'}))
    publish_at = forms.DateTimeField(input_formats = ['%m/%d/%Y %I:%M %p'], widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control datetimepicker-input',
                'data-target': '#datetimepicker'
                },
            format='%m/%d/%Y %I:%M %p'), required=False)

class editForm(forms.ModelForm):

    id = forms.IntegerField(widget=forms.HiddenInput)
    photos = forms.CharField(widget=forms.HiddenInput, required=False)
    videos = forms.CharField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='Content', widget=forms.Textarea(attrs={'class' : 'form-control'}))
    publish_at = forms.DateTimeField(input_formats = ['%m/%d/%Y %I:%M %p'], widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control datetimepicker-input',
                'data-target': '#datetimepicker'
                },
            format='%m/%d/%Y %I:%M %p'), required=False)

    class Meta:
        model = Post
        fields = ['id', 'content']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('file', )

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('file', )