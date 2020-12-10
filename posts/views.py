from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    paginator = Paginator(Post.objects.all(), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {
        'paginator': paginator,
        'page': page,
    })


def group_post(request, slug):
    """Return a group page with posts"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'paginator': paginator,
        'page': page,
    })


@login_required
def new_post(request):
    """Return a new post page with form"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/new_post.html', {'form': form})
    # Change data in instance of our form
    form.instance.author = request.user
    form.save()
    return redirect('index')


def profile(request, username):
    """Return a user's profile page"""
    user = get_object_or_404(User, username=username)
    paginator = Paginator(user.posts.all(), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_following = (
        request.user.is_authenticated and
        Follow.objects.filter(author=user, user=request.user)
    )
    context = {
        'author': user,
        'paginator': paginator,
        'page': page,
        'is_following': is_following,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    """Return one particular post with comments and comment's form"""
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    is_following = (
        request.user.is_authenticated and
        Follow.objects.filter(author=user, user=request.user)
    )
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/profile.html', {
            'form': form,
            'author': user,
            'post': post,
            'is_following': is_following,
        })
    form.instance.author = request.user
    form.instance.post = post
    form.save()
    return redirect('post', user.username, post.id)


@login_required
def post_edit(request, username, post_id):
    """Return an edit page for a particular post"""
    # If user really is the author
    if request.user.username != username:
        return redirect('profile', username)
    post = get_object_or_404(Post, id=post_id, author=user)
    user = get_object_or_404(User, username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/new_post.html', {
            'form': form,
            'author': user,
            'post': post,
        })
    form.save()
    # Go back to the post
    return redirect('post', user.username, post.id)


@login_required
def add_comment(request, username, post_id):
    """Return an adding comment page for post"""
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('post', user.username, post.id)
    form.instance.author = request.user
    form.instance.post = post
    form.save()
    return redirect('post', user.username, post.id)


@login_required
def follow_index(request):
    """Return user's favorite author's posts"""
    post_list = Post.objects.select_related('author').filter(
        author__following__user=request.user
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'paginator': paginator,
        'page': page
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Do a subscribtion of the user to the author"""
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
        author=author,
        user=request.user
    ).exists():
        Follow.objects.create(author=author, user=request.user)
    return redirect('profile', author.username)


@login_required
def profile_unfollow(request, username):
    """Unfollow the user from the author"""
    author = get_object_or_404(User, username=username)
    # Check if the user is a follower of the author
    get_object_or_404(Follow, user=request.user, author=author)
    Follow.objects.get(author=author, user=request.user).delete()
    return redirect('profile', author.username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
