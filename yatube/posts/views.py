from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache

from .models import Post, Group, Comment, Follow, User
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
    posts = Post.objects.select_related(
        'author',
    ).filter(group=group)
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
    posts = Post.objects.select_related(
        'group',
    ).filter(author=author)
    following = Follow.objects.filter(
        author=author, user=request.user.id).exists()
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
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(
        request.POST or None,
    )
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.post = post
        new_comment.author = request.user
        new_comment.save()

        return redirect('posts:post_detail', post_id=post_id)
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
        edited_post = form.save(commit=False)
        edited_post.author = request.user
        edited_post.save()

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
    followed_authors = Follow.objects.filter(
            user=request.user.id).values_list('author')
    posts = Post.objects.filter(author__in=followed_authors)
    page_obj = add_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    '''Подписка на автора'''
    user = get_object_or_404(User, id=request.user.id)
    author = get_object_or_404(User, username=username)
    if user.id != author.id:
        Follow.objects.update_or_create(
            user=user,
            author=author
        )
    cache.clear()

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    '''Отписка от автора'''
    user = get_object_or_404(User, id=request.user.id)
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
            user=user,
            author=author
        ).delete()
    cache.clear()

    return redirect('posts:profile', username=username)
