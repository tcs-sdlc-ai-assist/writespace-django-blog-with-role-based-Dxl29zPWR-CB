from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from blog.forms import BlogForm
from blog.models import Post


@login_required
def blog_list(request):
    posts = Post.objects.select_related('author').order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})


@login_required
def blog_detail(request, id):
    post = get_object_or_404(Post.objects.select_related('author'), id=id)
    can_edit = request.user.is_staff or post.author == request.user
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'can_edit': can_edit,
    })


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog-detail', id=post.id)
    else:
        form = BlogForm()
    return render(request, 'blog/blog_create.html', {'form': form})


@login_required
def blog_edit(request, id):
    post = get_object_or_404(Post.objects.select_related('author'), id=id)
    if not (request.user.is_staff or post.author == request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog-detail', id=post.id)
    else:
        form = BlogForm(instance=post)
    return render(request, 'blog/blog_edit.html', {'form': form, 'post': post})


@login_required
def blog_delete(request, id):
    post = get_object_or_404(Post.objects.select_related('author'), id=id)
    if not (request.user.is_staff or post.author == request.user):
        return HttpResponseForbidden()
    if request.method == 'POST':
        post.delete()
        return redirect('blog-list')
    return redirect('blog-detail', id=post.id)


def staff_check(user):
    return user.is_staff


@login_required
@user_passes_test(staff_check)
def admin_dashboard(request):
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    total_admins = User.objects.filter(is_staff=True).count()
    total_regular_users = total_users - total_admins
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]
    return render(request, 'blog/admin_dashboard.html', {
        'total_posts': total_posts,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_regular_users': total_regular_users,
        'recent_posts': recent_posts,
    })