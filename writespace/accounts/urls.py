from django.urls import path

from accounts.views import landing_page, login_view, logout_view, register_view, user_management

urlpatterns = [
    path('', landing_page, name='landing-page'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('users/', user_management, name='user-management'),
]