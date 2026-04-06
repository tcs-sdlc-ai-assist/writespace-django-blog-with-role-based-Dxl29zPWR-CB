from django.contrib import admin
from django.urls import path

from accounts.views import landing_page, login_view, logout_view, register_view, user_management
from blog.views import admin_dashboard, blog_create, blog_delete, blog_detail, blog_edit, blog_list

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('users/', user_management, name='user-management'),
    path('blogs/', blog_list, name='blog-list'),
    path('blogs/create/', blog_create, name='blog-create'),
    path('blogs/<uuid:id>/', blog_detail, name='blog-detail'),
    path('blogs/<uuid:id>/edit/', blog_edit, name='blog-edit'),
    path('blogs/<uuid:id>/delete/', blog_delete, name='blog-delete'),
    path('admin-panel/', admin_dashboard, name='admin-dashboard'),
]