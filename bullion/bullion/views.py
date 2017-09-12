from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from datetime import datetime
from ipware.ip import get_ip

from .models import Investor, Document
from .forms import UserForm, PersonalDataForm, InvestorProfileForm


def auth_login(request):
    next = ''
    if request.GET:
        next = request.GET['next']

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            request.session['password'] = password
            is_profile_created_already = Investor.objects.filter(user=user).exists()
            if is_profile_created_already:
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse('materials'))
            else:
                return HttpResponseRedirect(reverse('details_personal'))
        else:
            messages.error(request, 'Invalid login details supplied.')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


@login_required
def details_personal(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        personal_data_form = PersonalDataForm(request.POST)

        if user_form.is_valid() and personal_data_form.is_valid():

            user = user_form.save(commit=False)
            username = user.username
            password = request.session.get('password')
            email = username

            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            user = authenticate(username=username, password=password)
            login(request, user)

            personal_data = personal_data_form.save(commit=False)
            name = personal_data.name

            registration_date = datetime.now()

            ip = get_ip(request)
            if ip == '127.0.0.1':
                country = 'Land of Oz'
                city = 'Emerald City'
            else:
                g = GeoIP2()
                country = g.country(ip)['country_name']
                city = '{}, {}'.format(g.city(ip)['city'], g.city(ip)['region'])

            investor, created = Investor.objects.update_or_create(user=request.user, defaults={'email': email, 'name': name, 'registration_date': registration_date, 'ip_address': ip, 'country': country, 'city': city})

            return HttpResponseRedirect(reverse('details_investor'))
    else:
        user_form = UserForm()
        personal_data_form = PersonalDataForm()
    return render(request, 'details-personal.html', {'user_form': user_form, 'personal_data_form': personal_data_form })


@login_required
def details_investor(request):
    investor = Investor.objects.get(user=request.user)
    registered = investor.is_registered

    if investor.location or investor.legal_status:
        registered = True
    else:
        registered = False

    if request.method == 'POST':
        investor_profile_form = InvestorProfileForm(request.POST)
        if investor_profile_form.is_valid():

            profile_form = investor_profile_form.save(commit=False)
            legal_status = profile_form.legal_status
            location = profile_form.location
            is_accredited = profile_form.is_accredited

            investor, created = Investor.objects.update_or_create(user=request.user, defaults={'legal_status': legal_status, 'location': location, 'is_accredited': is_accredited })

            return HttpResponseRedirect(reverse('materials'))
    else:
        investor_profile_form = InvestorProfileForm()
    return render(request, 'details-investor.html', {'investor_profile_form': investor_profile_form, 'registered': registered})


@login_required
def materials(request):
    investor = Investor.objects.get(user=request.user)
    registered = investor.is_registered

    location = investor.location
    legal_status = investor.legal_status
    accredited = investor.is_accredited
    documents = Document.objects.filter(reader_location=location, reader_legal_status=legal_status, is_reader_accredited=accredited) | Document.objects.filter(reader_location=location, reader_legal_status='NOTSP', is_reader_accredited=accredited)
    return render(request, 'materials.html', {'investor': investor, 'documents': documents, 'registered': registered})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required
def profile(request):
    investor = Investor.objects.get(user=request.user)
    registered = investor.is_registered

    if request.method == 'POST':
        personal_data_form = PersonalDataForm(request.POST)
        investor_profile_form = InvestorProfileForm(request.POST)

        if personal_data_form.is_valid() and investor_profile_form.is_valid():

            personal_data = personal_data_form.save(commit=False)
            name = personal_data.name

            investor_profile = investor_profile_form.save(commit=False)
            legal_status = investor_profile.legal_status
            location = investor_profile.location
            is_accredited = investor_profile.is_accredited

            investor.name = name
            investor.legal_status = legal_status
            investor.location = location
            investor.is_accredited = is_accredited
            investor.save()

            return HttpResponseRedirect(reverse('materials'))
    else:
        investor_name = Investor.objects.get(user=request.user).name
        personal_data = {'name': investor_name}
        personal_data_form = PersonalDataForm(initial=personal_data)
        investor_data = {}

        if investor.location and investor.legal_status:
            investor_data = {'location': investor.location, 'legal_status': investor.legal_status, 'is_accredited': investor.is_accredited}
        investor_profile_form = InvestorProfileForm(initial=investor_data)
    return render(request, 'profile.html', {'personal_data_form': personal_data_form, 'investor_profile_form': investor_profile_form, 'registered': registered})
