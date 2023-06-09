from .models import Post

from django import forms

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ['categories', 'author', 'title', 'post_text']
