from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea, PasswordInput
from .models import Entry, Comment


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', max_length=20)
    password = forms.CharField(
        label='Пароль', widget=forms.PasswordInput(), max_length=20)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Неправильная пара логин-пароль")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class EntryForm(ModelForm):

    class Meta:
        model = Entry
        fields = ('content', )
        labels = {'content': 'Текст записи:'}
        widgets = {
            'content': Textarea(attrs={'cols': 80, 'rows': 10, 'class': 'form-control'})
        }


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('content', )
        labels = {'content': 'Текст комментария:'}
        widgets = {
            'content': Textarea(attrs={'cols': 70, 'rows': 1, 'class': 'form-control'})
        }


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
            'password': PasswordInput(attrs={})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control', 'style': 'width:25%'})
