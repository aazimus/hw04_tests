from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
                  "group": group, "posts": posts, "page": page, "paginator": paginator})


@login_required
def new_post(request):
    post_form = PostForm(request.POST or None)
    if not post_form.is_valid():
        return render(request, "new.html", {'form': post_form})
    in_new_post = post_form.save(commit=False)
    in_new_post.author = request.user
    in_new_post.save()
    return redirect('index')


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post_count = post_list.count()
    author = user
    return render(
        request,
        'profile.html',
        {'user': user,
         'page': page,
         'post_count': post_count, 'author': author},
    )


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    post_list = Post.objects.filter(author=user)
    post_count = post_list.count()
    return render(
        request,
        'post.html',
        {'post': post,
         'user': user,
         'post_count': post_count,
         'author': author,
         })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author.username != request.user.username:
        return redirect(reverse('profile', args=[post.author.username]))
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect(reverse('post_edit', kwargs={
                        'username': post.author.username, 'post_id': post_id}))
    return render(request, 'new.html', {
                  'form': form, 'post': post, 'edit': True})
