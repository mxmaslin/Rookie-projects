from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.shortcuts import render, HttpResponse, HttpResponseRedirect

from .models import Entry, Comment, Author
from .forms import EntryForm, CommentForm, UserForm, LoginForm


def index(request):
    entry_list = Entry.objects.all().order_by('-date')

    paginator = Paginator(entry_list, 5)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        entries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        entries = paginator.page(paginator.num_pages)

    return render(request, 'guestbook/index.html', {'entries': entries})


def view_entry(request, entry_pk):
    try:
        entry = Entry.objects.get(pk=entry_pk)
    except ObjectDoesNotExist:
        return HttpResponse('Запись, которую вы пытаетесь просмотреть, не существует')
    comments = entry.comment_set.all()
    return render(request, 'guestbook/entry.html', {'entry': entry, 'comments': comments})


@login_required
def add_entry(request):
    if request.method == 'POST':
        entry_form = EntryForm(request.POST)
        if entry_form.is_valid():
            entry = entry_form.save(commit=False)
            content = entry.content
            author = Author.objects.get(user=request.user)
            Entry.objects.create(content=content, author=author)
            return HttpResponseRedirect(reverse('guestbook:index'))
    else:
        entry_form = EntryForm()
    return render(request, 'guestbook/add-entry.html', {'entry_form': entry_form})


@login_required
def add_comment(request, entry_pk):
    try:
        entry = Entry.objects.get(pk=entry_pk)
    except ObjectDoesNotExist:
        return HttpResponse('Запись, которую вы пытаетесь прокомментировать, не существует')

    entry = Entry.objects.get(pk=entry_pk)
    comments = entry.comment_set.all()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            content = comment.content
            author = Author.objects.get(user=request.user)
            Comment.objects.create(content=content, author=author, entry=entry)
            return HttpResponseRedirect(reverse('guestbook:index'))
    else:
        comment_form = CommentForm()
    return render(request, 'guestbook/add-comment.html', {'comment_form': comment_form, 'entry': entry, 'comments': comments})


def author_entries(request, username):
    user = User.objects.get(username=username)
    author = Author.objects.get(user=user)
    entries = author.entry_set.all()
    return render(request, 'guestbook/author.html', {'entries': entries, 'username': username})


def unique_name(request):
    if request.method == 'GET':
        name = request.GET.get('username', '')
        print(Author.objects.filter(user__username=name).exists())
    return HttpResponse(Author.objects.filter(user__username=name).exists())


def registration(request):
    username = ''

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            username = user.username
            password = user.password
            user = User.objects.create_user(username=username, password=password)
            author = Author(user=user)
            author.save()
            author = authenticate(username=username, password=password)
            login(request, author)
            return HttpResponseRedirect(reverse('guestbook:index'))
    else:
        user_form = UserForm()
    return render(request, 'guestbook/registration.html', {'user_form': user_form, 'username': username})


def author_login(request):
    next = ''
    if request.GET:
        next = request.GET['next']
        print('next is ' + next)

    print("next is " + next)

    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect(reverse('guestbook:index'))
    return render(request, 'guestbook/login.html', {'login_form': form})


@login_required
def author_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('guestbook:index'))
