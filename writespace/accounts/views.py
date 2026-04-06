from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import CreateUserForm, LoginForm, RegisterForm
from blog.models import Post


def landing_page(request):
    latest_posts = Post.objects.select_related('author').order_by('-created_at')[:3]
    return render(request, 'landing.html', {'latest_posts': latest_posts})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin-panel/')
        return redirect('/blogs/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('/admin-panel/')
                return redirect('/blogs/')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/blogs/')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/blogs/')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/')
    return redirect('/')


@login_required
def user_management(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to access this page.')

    if request.method == 'POST':
        if 'delete_user_id' in request.POST:
            user_id = request.POST.get('delete_user_id')
            user_to_delete = get_object_or_404(User, pk=user_id)
            if user_to_delete.is_superuser:
                form = CreateUserForm()
                users = User.objects.all().order_by('date_joined')
                return render(request, 'accounts/user_management.html', {
                    'form': form,
                    'users': users,
                    'error': 'Cannot delete the default admin user.',
                })
            user_to_delete.delete()
            return redirect('/users/')
        else:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/users/')
    else:
        form = CreateUserForm()

    users = User.objects.all().order_by('date_joined')
    return render(request, 'accounts/user_management.html', {
        'form': form,
        'users': users,
    })