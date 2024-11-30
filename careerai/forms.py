from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['skills', 'interests', 'experience', 'goals']
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'interests': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'experience': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'goals': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
        }