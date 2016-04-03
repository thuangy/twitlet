from .models import UserProfile, Tweetlet
from django.contrib.auth.models import User
from django import forms
import datetime
from django.utils import timezone

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')

class TweetletForm(forms.ModelForm):
    





    #user = forms.CharField(widget=forms.HiddenInput(), initial=user.username)
    #user = username
    #user = forms.CharField(widget=forms.HiddenInput(), initial="")
    #user = forms.CharField()
    message = forms.CharField(max_length=50, help_text="Please enter your Tweetlet message. ", initial=" ")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    pub_date = forms.DateTimeField(widget=forms.HiddenInput(), initial=timezone.now())
    #user = forms.CharField(widget=forms.HiddenInput())

    """def __init__(self, *args, **kwargs):
       self.request = kwargs.pop('request', None)
       return super(TweetletForm, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
       kwargs['commit']=False
       obj = super(TweetletForm, self).save(*args, **kwargs)
       if self.request:
           obj.user = self.request.username
       obj.save()
       return obj"""


    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Tweetlet
        #exclude = ('user', 'views', 'likes')
        fields = ('message', 'pub_date')
        #exclude = ('user',)