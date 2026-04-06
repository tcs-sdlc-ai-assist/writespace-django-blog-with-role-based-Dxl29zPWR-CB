from uuid import uuid4

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from blog.models import Post


class BlogListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )
        self.url = reverse('blog-list')

    def test_blog_list_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_blog_list_returns_200_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_blog_list_returns_posts(self):
        Post.objects.create(title='Post One', content='Content one', author=self.user)
        Post.objects.create(title='Post Two', content='Content two', author=self.user)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 2)

    def test_blog_list_empty(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 0)


class BlogDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
        )

    def test_blog_detail_requires_login(self):
        url = reverse('blog-detail', kwargs={'id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_blog_detail_returns_200(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog-detail', kwargs={'id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)

    def test_blog_detail_returns_404_for_invalid_uuid(self):
        self.client.login(username='testuser', password='testpass123')
        fake_uuid = uuid4()
        url = reverse('blog-detail', kwargs={'id': fake_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_blog_detail_can_edit_for_author(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog-detail', kwargs={'id': self.post.id})
        response = self.client.get(url)
        self.assertTrue(response.context['can_edit'])

    def test_blog_detail_can_edit_for_admin(self):
        admin = User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_staff=True,
        )
        self.client.login(username='admin', password='adminpass123')
        url = reverse('blog-detail', kwargs={'id': self.post.id})
        response = self.client.get(url)
        self.assertTrue(response.context['can_edit'])

    def test_blog_detail_cannot_edit_for_non_owner(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
        )
        self.client.login(username='otheruser', password='otherpass123')
        url = reverse('blog-detail', kwargs={'id': self.post.id})
        response = self.client.get(url)
        self.assertFalse(response.context['can_edit'])


class BlogCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )
        self.url = reverse('blog-create')

    def test_blog_create_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_blog_create_get_returns_200(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_blog_create_saves_post_with_correct_author(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, {
            'title': 'New Blog Post',
            'content': 'This is the content of the new blog post.',
        })
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, 'New Blog Post')
        self.assertEqual(post.content, 'This is the content of the new blog post.')
        self.assertEqual(post.author, self.user)
        self.assertEqual(response.status_code, 302)

    def test_blog_create_redirects_to_detail(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, {
            'title': 'New Blog Post',
            'content': 'Content here.',
        })
        post = Post.objects.first()
        expected_url = reverse('blog-detail', kwargs={'id': post.id})
        self.assertRedirects(response, expected_url)

    def test_blog_create_invalid_form(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, {
            'title': '',
            'content': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 0)


class BlogEditViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            first_name='Other User',
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            first_name='Admin User',
            is_staff=True,
        )
        self.post = Post.objects.create(
            title='Original Title',
            content='Original content',
            author=self.user,
        )
        self.url = reverse('blog-edit', kwargs={'id': self.post.id})

    def test_blog_edit_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_blog_edit_owner_can_access(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_blog_edit_non_owner_gets_403(self):
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_blog_edit_admin_can_edit_any(self):
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_blog_edit_owner_can_update(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, {
            'title': 'Updated Title',
            'content': 'Updated content',
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.content, 'Updated content')
        self.assertEqual(response.status_code, 302)

    def test_blog_edit_admin_can_update_any(self):
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.post(self.url, {
            'title': 'Admin Updated Title',
            'content': 'Admin updated content',
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Admin Updated Title')
        self.assertEqual(response.status_code, 302)

    def test_blog_edit_non_owner_post_gets_403(self):
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.post(self.url, {
            'title': 'Hacked Title',
            'content': 'Hacked content',
        })
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Original Title')

    def test_blog_edit_returns_404_for_invalid_uuid(self):
        self.client.login(username='testuser', password='testpass123')
        fake_uuid = uuid4()
        url = reverse('blog-edit', kwargs={'id': fake_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class BlogDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            first_name='Other User',
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            first_name='Admin User',
            is_staff=True,
        )
        self.post = Post.objects.create(
            title='Post to Delete',
            content='Content to delete',
            author=self.user,
        )
        self.url = reverse('blog-delete', kwargs={'id': self.post.id})

    def test_blog_delete_requires_login(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_blog_delete_owner_can_delete(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 0)

    def test_blog_delete_non_owner_gets_403(self):
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Post.objects.count(), 1)

    def test_blog_delete_admin_can_delete_any(self):
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 0)

    def test_blog_delete_get_redirects_to_detail(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        expected_url = reverse('blog-detail', kwargs={'id': self.post.id})
        self.assertRedirects(response, expected_url)
        self.assertEqual(Post.objects.count(), 1)

    def test_blog_delete_returns_404_for_invalid_uuid(self):
        self.client.login(username='testuser', password='testpass123')
        fake_uuid = uuid4()
        url = reverse('blog-delete', kwargs={'id': fake_uuid})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class AdminDashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            first_name='Admin User',
            is_staff=True,
        )
        self.url = reverse('admin-dashboard')

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_admin_dashboard_requires_staff(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_admin_dashboard_accessible_by_staff(self):
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_context_data(self):
        Post.objects.create(title='Post 1', content='Content 1', author=self.user)
        Post.objects.create(title='Post 2', content='Content 2', author=self.admin_user)
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_posts'], 2)
        self.assertEqual(response.context['total_users'], 2)
        self.assertEqual(response.context['total_admins'], 1)
        self.assertEqual(response.context['total_regular_users'], 1)
        self.assertEqual(len(response.context['recent_posts']), 2)

    def test_admin_dashboard_recent_posts_limited_to_five(self):
        for i in range(7):
            Post.objects.create(
                title=f'Post {i}',
                content=f'Content {i}',
                author=self.admin_user,
            )
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['recent_posts']), 5)