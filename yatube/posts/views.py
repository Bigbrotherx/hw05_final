from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache

from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm
from .utils import add_paginator


def index(request):
    '''Функция рендера главной страницы проекта'''
    template = 'posts/index.html'
    posts = Post.objects.select_related(
        'author',
        'group',
    )
    page_obj = add_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    '''Функция рендера страниц с поставми запрошенной группы'''
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('author',)
    page_obj = add_paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    '''Функция рендера страницы профиля пользователя'''
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group',)
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user).exists()
    )
    page_obj = add_paginator(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }

    return render(request, template, context)


def post_detail(request, post_id):
    '''Функция рендера страницы выбранного поста'''
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('post__group',)
    form = CommentForm(None)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, template, context)


@login_required
def post_create(request):
    '''Функция создания нового поста'''
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()

        return redirect('posts:profile', username=request.user.username)

    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    '''Функция редактирования поста'''
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:

        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id)

    return render(request, template, {'form': form,
                                      'is_edit': is_edit,
                                      'post_id': post_id})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    '''Страница избранных постов'''
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = add_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    '''Подписка на автора'''
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.update_or_create(user=request.user, author=author)
    cache.clear()

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    '''Отписка от автора'''
    Follow.objects.filter(
        user=request.user, author__username=username
    ).delete()
    cache.clear()

    return redirect('posts:profile', username=username)
