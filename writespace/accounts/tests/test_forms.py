import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from accounts.forms import CreateUserForm, LoginForm, RegisterForm
from blog.forms import BlogForm


class TestLoginForm(TestCase):

    def test_valid_login_form(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'testpass123',
        })
        assert form.is_valid()

    def test_login_form_missing_username(self):
        form = LoginForm(data={
            'username': '',
            'password': 'testpass123',
        })
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_login_form_missing_password(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': '',
        })
        assert not form.is_valid()
        assert 'password' in form.errors

    def test_login_form_missing_all_fields(self):
        form = LoginForm(data={})
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'password' in form.errors


class TestRegisterForm(TestCase):

    def test_valid_register_form(self):
        form = RegisterForm(data={
            'display_name': 'Test User',
            'username': 'testuser',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        assert form.is_valid()

    def test_register_form_password_mismatch(self):
        form = RegisterForm(data={
            'display_name': 'Test User',
            'username': 'testuser',
            'password1': 'securepass123',
            'password2': 'differentpass456',
        })
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_register_form_unique_username(self):
        User.objects.create_user(username='existinguser', password='pass123')
        form = RegisterForm(data={
            'display_name': 'Another User',
            'username': 'existinguser',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_register_form_unique_username_case_insensitive(self):
        User.objects.create_user(username='ExistingUser', password='pass123')
        form = RegisterForm(data={
            'display_name': 'Another User',
            'username': 'existinguser',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_register_form_missing_display_name(self):
        form = RegisterForm(data={
            'display_name': '',
            'username': 'testuser',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        assert not form.is_valid()
        assert 'display_name' in form.errors

    def test_register_form_missing_username(self):
        form = RegisterForm(data={
            'display_name': 'Test User',
            'username': '',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_register_form_missing_passwords(self):
        form = RegisterForm(data={
            'display_name': 'Test User',
            'username': 'testuser',
            'password1': '',
            'password2': '',
        })
        assert not form.is_valid()
        assert 'password1' in form.errors
        assert 'password2' in form.errors

    def test_register_form_save_creates_user(self):
        form = RegisterForm(data={
            'display_name': 'New Writer',
            'username': 'newwriter',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        assert form.is_valid()
        user = form.save()
        assert user.pk is not None
        assert user.username == 'newwriter'
        assert user.first_name == 'New Writer'
        assert user.check_password('securepass123')


class TestCreateUserForm(TestCase):

    def test_valid_create_user_form(self):
        form = CreateUserForm(data={
            'display_name': 'New User',
            'username': 'newuser',
            'password': 'securepass123',
            'role': 'user',
        })
        assert form.is_valid()

    def test_valid_create_admin_form(self):
        form = CreateUserForm(data={
            'display_name': 'New Admin',
            'username': 'newadmin',
            'password': 'securepass123',
            'role': 'admin',
        })
        assert form.is_valid()

    def test_create_user_form_missing_display_name(self):
        form = CreateUserForm(data={
            'display_name': '',
            'username': 'newuser',
            'password': 'securepass123',
            'role': 'user',
        })
        assert not form.is_valid()
        assert 'display_name' in form.errors

    def test_create_user_form_missing_username(self):
        form = CreateUserForm(data={
            'display_name': 'New User',
            'username': '',
            'password': 'securepass123',
            'role': 'user',
        })
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_create_user_form_missing_password(self):
        form = CreateUserForm(data={
            'display_name': 'New User',
            'username': 'newuser',
            'password': '',
            'role': 'user',
        })
        assert not form.is_valid()
        assert 'password' in form.errors

    def test_create_user_form_missing_role(self):
        form = CreateUserForm(data={
            'display_name': 'New User',
            'username': 'newuser',
            'password': 'securepass123',
            'role': '',
        })
        assert not form.is_valid()
        assert 'role' in form.errors

    def test_create_user_form_invalid_role(self):
        form = CreateUserForm(data={
            'display_name': 'New User',
            'username': 'newuser',
            'password': 'securepass123',
            'role': 'superadmin',
        })
        assert not form.is_valid()
        assert 'role' in form.errors

    def test_create_user_form_unique_username(self):
        User.objects.create_user(username='takenname', password='pass123')
        form = CreateUserForm(data={
            'display_name': 'New User',
            'username': 'takenname',
            'password': 'securepass123',
            'role': 'user',
        })
        assert not form.is_valid()
        assert 'username' in form.errors

    def test_create_user_form_save_regular_user(self):
        form = CreateUserForm(data={
            'display_name': 'Regular User',
            'username': 'regularuser',
            'password': 'securepass123',
            'role': 'user',
        })
        assert form.is_valid()
        user = form.save()
        assert user.pk is not None
        assert user.username == 'regularuser'
        assert user.first_name == 'Regular User'
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password('securepass123')

    def test_create_user_form_save_admin_user(self):
        form = CreateUserForm(data={
            'display_name': 'Admin User',
            'username': 'adminuser',
            'password': 'securepass123',
            'role': 'admin',
        })
        assert form.is_valid()
        user = form.save()
        assert user.pk is not None
        assert user.username == 'adminuser'
        assert user.first_name == 'Admin User'
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.check_password('securepass123')


class TestBlogForm(TestCase):

    def test_valid_blog_form(self):
        form = BlogForm(data={
            'title': 'My First Blog Post',
            'content': 'This is the content of my first blog post.',
        })
        assert form.is_valid()

    def test_blog_form_missing_title(self):
        form = BlogForm(data={
            'title': '',
            'content': 'This is the content of my blog post.',
        })
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_blog_form_missing_content(self):
        form = BlogForm(data={
            'title': 'My Blog Post',
            'content': '',
        })
        assert not form.is_valid()
        assert 'content' in form.errors

    def test_blog_form_missing_all_fields(self):
        form = BlogForm(data={})
        assert not form.is_valid()
        assert 'title' in form.errors
        assert 'content' in form.errors

    def test_blog_form_title_max_length(self):
        form = BlogForm(data={
            'title': 'x' * 201,
            'content': 'Some content here.',
        })
        assert not form.is_valid()
        assert 'title' in form.errors

    def test_blog_form_title_at_max_length(self):
        form = BlogForm(data={
            'title': 'x' * 200,
            'content': 'Some content here.',
        })
        assert form.is_valid()