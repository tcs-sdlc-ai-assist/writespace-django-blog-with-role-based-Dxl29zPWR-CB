from django.urls import path

from blog.views import (
    admin_dashboard,
    blog_create,
    blog_delete,
    blog_detail,
    blog_edit,
    blog_list,
)

urlpatterns = [
    path('blogs/', blog_list, name='blog-list'),
    path('blog/<uuid:id>/', blog_detail, name='blog-detail'),
    path('write/', blog_create, name='blog-create'),
    path('edit/<uuid:id>/', blog_edit, name='blog-edit'),
    path('delete/<uuid:id>/', blog_delete, name='blog-delete'),
    path('admin-panel/', admin_dashboard, name='admin-dashboard'),
]