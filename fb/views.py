from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseForbidden

from fb.models import UserPost, UserPostComment, UserProfile
from fb.forms import (
    UserPostForm, UserPostCommentForm, UserLogin, UserProfileForm, SearchForm
)


@login_required
def index(request):
    posts = UserPost.objects.all()
    search_form = SearchForm()
    if request.method == 'GET':
        form = UserPostForm()
    elif request.method == 'POST':
        form = UserPostForm(request.POST, request.FILES or None)
        if form.is_valid():
            user_post = form.save(commit=False)
            user_post.author = request.user
            user_post.save()

    context = {
        'posts': posts,
        'form': form,
        'search_form': search_form,
    }
    return render(request, 'index.html', context)


@login_required
def search_view(request):
    search_form = SearchForm()
    context = {
        'search_form': search_form
    }
    if request.method == 'GET':
        q = request.GET.get('q')
        if q:
            users = UserProfile.objects.filter(user__username__contains=q)
            posts = UserPost.objects.filter(text__contains=q)
            context = {
                'users': users,
                'posts':posts,
                'search_form': search_form,
            }

    return render(request, 'search.html', context)


@login_required
def post_details(request, pk):
    post = UserPost.objects.get(pk=pk)
    search_form = SearchForm()
    if request.method == 'GET':
        form = UserPostCommentForm()
    elif request.method == 'POST':
        form = UserPostCommentForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            comment = UserPostComment(text=cleaned_data['text'],
                                      post=post,
                                      author=request.user)
            comment.save()

    comments = UserPostComment.objects.filter(post=post)

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'search_form': search_form,
    }

    return render(request, 'post_details.html', context)


def login_view(request):
    if request.method == 'GET':
        login_form = UserLogin()
        context = {
            'form': login_form,
        }
        return render(request, 'login.html', context)
    if request.method == 'POST':
        login_form = UserLogin(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = {
                'form': login_form,
                'message': 'Wrong user and/or password!',
            }
            return render(request, 'login.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


@login_required
def profile_view(request, user):
    search_form = SearchForm()
    posts = UserPost.objects.filter(author = request.user)
    visited_person = User.objects.get(username = user)
    ok = False
    for friend in request.user.profile.friends.all():
        if friend == visited_person:
            ok = True
    context = {
        'search_form': search_form,
        'profile': visited_person.profile,
        'ok': ok,
        'posts' : posts,
    }
    if request.method == 'GET':
        return render(request, 'profile.html', context)
    else:
        friend = User.objects.get(username = user)
        request.user.profile.friends.add(friend)
        return redirect(reverse('profile', args=[user]))



@login_required
def edit_profile_view(request, user):
    search_form = SearchForm()
    profile = UserProfile.objects.get(user__username=user)
    if not request.user == profile.user:
        return HttpResponseForbidden()
    if request.method == 'GET':
        data = {
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'gender': profile.gender,
            'date_of_birth': profile.date_of_birth,
        }
        avatar = SimpleUploadedFile(
            profile.avatar.name, profile.avatar.file.read()) \
            if profile.avatar else None
        file_data = {'avatar': avatar}
        form = UserProfileForm(data, file_data)
    elif request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.user.first_name = form.cleaned_data['first_name']
            profile.user.last_name = form.cleaned_data['last_name']
            profile.user.save()

            profile.gender = form.cleaned_data['gender']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            if form.cleaned_data['avatar']:
                profile.avatar = form.cleaned_data['avatar']
            profile.save()

            return redirect(reverse('profile', args=[profile.user.username]))
    context = {
        'form': form,
        'profile': profile,
        'search_form': search_form,
    }
    return render(request, 'edit_profile.html', context)


@login_required
def like_view(request, pk):
    post = UserPost.objects.get(pk=pk)
    post.likers.add(request.user)
    post.save()
    if 'next_url' in request.GET:
        return redirect(request.GET.get('next_url'))
    else:
        return redirect(reverse('post_details', args=[post.pk]))
