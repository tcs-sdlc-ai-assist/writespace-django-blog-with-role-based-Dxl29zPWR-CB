import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class TestLandingPage(TestCase):
    def test_landing_page_accessible_without_login(self):
        client = Client()
        response = client.get(reverse('landing'))
        assert response.status_code == 200

    def test_landing_page_contains_writespace(self):
        client = Client()
        response = client.get(reverse('landing'))
        assert b'WriteSpace' in response.content


class TestLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123',
            first_name='Regular',
            is_staff=False,
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            first_name='Admin',
            is_staff=True,
            is_superuser=True,
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        assert response.status_code == 200

    def test_login_redirects_regular_user_to_blogs(self):
        response = self.client.post(reverse('login'), {
            'username': 'regularuser',
            'password': 'testpass123',
        })
        assert response.status_code == 302
        assert response.url == '/blogs/'

    def test_login_redirects_admin_user_to_admin_panel(self):
        response = self.client.post(reverse('login'), {
            'username': 'adminuser',
            'password': 'testpass123',
        })
        assert response.status_code == 302
        assert response.url == '/admin-panel/'

    def test_login_shows_error_on_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'regularuser',
            'password': 'wrongpassword',
        })
        assert response.status_code == 200
        assert b'Invalid username or password.' in response.content

    def test_login_redirects_authenticated_regular_user(self):
        self.client.login(username='regularuser', password='testpass123')
        response = self.client.get(reverse('login'))
        assert response.status_code == 302
        assert response.url == '/blogs/'

    def test_login_redirects_authenticated_admin_user(self):
        self.client.login(username='adminuser', password='testpass123')
        response = self.client.get(reverse('login'))
        assert response.status_code == 302
        assert response.url == '/admin-panel/'


class TestRegisterView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_renders(self):
        response = self.client.get(reverse('register'))
        assert response.status_code == 200

    def test_register_creates_user_with_is_staff_false(self):
        response = self.client.post(reverse('register'), {
            'display_name': 'New User',
            'username': 'newuser',
            'password1': 'securepass123!',
            'password2': 'securepass123!',
        })
        assert response.status_code == 302
        assert response.url == '/blogs/'
        user = User.objects.get(username='newuser')
        assert user.first_name == 'New User'
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_register_enforces_password_match(self):
        response = self.client.post(reverse('register'), {
            'display_name': 'New User',
            'username': 'newuser',
            'password1': 'securepass123!',
            'password2': 'differentpass456!',
        })
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()
        assert b'Passwords do not match.' in response.content

    def test_register_enforces_unique_username(self):
        User.objects.create_user(username='existinguser', password='testpass123')
        response = self.client.post(reverse('register'), {
            'display_name': 'Another User',
            'username': 'existinguser',
            'password1': 'securepass123!',
            'password2': 'securepass123!',
        })
        assert response.status_code == 200
        assert b'A user with that username already exists.' in response.content

    def test_register_redirects_authenticated_user(self):
        User.objects.create_user(username='loggedin', password='testpass123')
        self.client.login(username='loggedin', password='testpass123')
        response = self.client.get(reverse('register'))
        assert response.status_code == 302
        assert response.url == '/blogs/'


class TestLogoutView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )

    def test_logout_requires_login(self):
        response = self.client.post(reverse('logout'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_logout_redirects_to_landing(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        assert response.status_code == 302
        assert response.url == '/'


class TestUserManagement(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            first_name='Admin',
            is_staff=True,
            is_superuser=True,
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpass123',
            first_name='Regular',
            is_staff=False,
        )

    def test_user_management_requires_staff(self):
        self.client.login(username='regularuser', password='testpass123')
        response = self.client.get(reverse('user-management'))
        assert response.status_code == 403

    def test_user_management_requires_login(self):
        response = self.client.get(reverse('user-management'))
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_user_management_accessible_by_staff(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('user-management'))
        assert response.status_code == 200

    def test_user_management_creates_regular_user(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('user-management'), {
            'display_name': 'Created User',
            'username': 'createduser',
            'password': 'newpass123!',
            'role': 'user',
        })
        assert response.status_code == 302
        assert response.url == '/users/'
        created = User.objects.get(username='createduser')
        assert created.first_name == 'Created User'
        assert created.is_staff is False
        assert created.is_superuser is False

    def test_user_management_creates_admin_user(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('user-management'), {
            'display_name': 'New Admin',
            'username': 'newadmin',
            'password': 'newpass123!',
            'role': 'admin',
        })
        assert response.status_code == 302
        assert response.url == '/users/'
        created = User.objects.get(username='newadmin')
        assert created.is_staff is True
        assert created.is_superuser is True

    def test_user_management_deletes_non_superuser(self):
        self.client.login(username='admin', password='testpass123')
        user_to_delete = User.objects.create_user(
            username='deleteme',
            password='testpass123',
            is_staff=False,
            is_superuser=False,
        )
        user_id = user_to_delete.pk
        response = self.client.post(reverse('user-management'), {
            'delete_user_id': user_id,
        })
        assert response.status_code == 302
        assert response.url == '/users/'
        assert not User.objects.filter(pk=user_id).exists()

    def test_default_admin_cannot_be_deleted(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('user-management'), {
            'delete_user_id': self.admin_user.pk,
        })
        assert response.status_code == 200
        assert b'Cannot delete the default admin user.' in response.content
        assert User.objects.filter(pk=self.admin_user.pk).exists()

    def test_user_management_lists_all_users(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('user-management'))
        assert response.status_code == 200
        assert b'admin' in response.content
        assert b'regularuser' in response.content