from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Skill, Interest

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['experience', 'goals', 'skills', 'interests', 'preferred_work_style', 
                 'bio', 'current_role', 'desired_role']
        widgets = {
            'skills': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'interests': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'goals': forms.Textarea(attrs={'rows': 4}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }