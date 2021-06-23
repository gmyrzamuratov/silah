from django import forms
from .models import Project

class newForm(forms.Form):

    title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'class' : 'form-control'}))

class editForm(forms.ModelForm):

    id = forms.IntegerField(widget=forms.HiddenInput)
    title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'class' : 'form-control'}))

    class Meta:
        model = Project
        fields = ['id', 'title']