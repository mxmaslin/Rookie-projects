from django import forms
from django.contrib.auth.models import User
from .models import Investor


class UserForm(forms.ModelForm):
    username = forms.EmailField(widget=forms.EmailInput(), label='Login (your email)')

    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control input-sm'})


class PersonalDataForm(forms.ModelForm):

    class Meta:
        model = Investor
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control input-sm'})


class InvestorProfileForm(forms.ModelForm):

    class Meta:
        model = Investor
        fields = ('location', 'legal_status', 'is_accredited')
        widgets = {'location': forms.Select, 'legal_status': forms.Select}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            if field != 'is_accredited':
                self.fields[field].widget.attrs.update({'class': 'form-control input-sm'})
