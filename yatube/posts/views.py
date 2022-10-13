from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .utils import get_paginator


def index(request):
    context = get_paginator(request, Post.objects.all())
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_paginator(request, group.posts.all()))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = author.following.exists()
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_paginator(request, author.posts.all()))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'post_id': post_id,
        'comments': post.comments.all(),
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if request.method == 'POST':
        if form.is_valid():
            post_object = form.save(commit=False)
            post_object.author = request.user
            post_object.save()
            return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html',
                  {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.user.id is not post.author.id:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    context = {
        'form': form,
        'is_edit': is_edit,
        'post_id': post_id
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)


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
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if (
            (user != author) and (Follow.objects.filter
                                  (user=user, author=author).count() == 0)
    ):
        Follow.objects.create(
            user=user,
            author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')


@login_required
def follow_index(request):
    """View-функция страницы, куда будут выведены посты авторов,
    на которых подписан текущий пользователь"""
    posts = Post.objects.filter(author__following__user=request.user)
    count = Follow.objects.count()
    context = dict(
        posts=posts,
        count=count,
    )
    context.update(get_paginator(request, posts))
    return render(request, 'posts/follow.html', context)
