from django import forms

class addForm(forms.Form):

    frame = forms.CharField(label='Frame', widget=forms.Textarea(attrs={'class' : 'form-control'}))