from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class CustomPasswordChangeForm(PasswordChangeForm):
    pass


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
