import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from blog.models import Post


class TestPostModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test User',
        )

    def test_create_post_with_uuid_primary_key(self):
        post = Post.objects.create(
            title='Test Post',
            content='This is test content.',
            author=self.user,
        )
        self.assertIsInstance(post.id, uuid.UUID)
        self.assertIsNotNone(post.id)

    def test_uuid_is_unique_per_post(self):
        post1 = Post.objects.create(
            title='Post One',
            content='Content one.',
            author=self.user,
        )
        post2 = Post.objects.create(
            title='Post Two',
            content='Content two.',
            author=self.user,
        )
        self.assertNotEqual(post1.id, post2.id)

    def test_string_representation(self):
        post = Post.objects.create(
            title='My Blog Post',
            content='Some content here.',
            author=self.user,
        )
        self.assertEqual(str(post), 'My Blog Post')

    def test_string_representation_with_special_characters(self):
        title = 'Post with "quotes" & <special> chars'
        post = Post.objects.create(
            title=title,
            content='Content.',
            author=self.user,
        )
        self.assertEqual(str(post), title)

    def test_ordering_by_created_at_descending(self):
        post1 = Post.objects.create(
            title='First Post',
            content='First content.',
            author=self.user,
        )
        post2 = Post.objects.create(
            title='Second Post',
            content='Second content.',
            author=self.user,
        )
        post3 = Post.objects.create(
            title='Third Post',
            content='Third content.',
            author=self.user,
        )
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], post3)
        self.assertEqual(posts[1], post2)
        self.assertEqual(posts[2], post1)

    def test_meta_ordering(self):
        self.assertEqual(Post._meta.ordering, ['-created_at'])

    def test_meta_verbose_name(self):
        self.assertEqual(Post._meta.verbose_name, 'post')
        self.assertEqual(Post._meta.verbose_name_plural, 'posts')

    def test_author_foreign_key_relationship(self):
        post = Post.objects.create(
            title='Author Test',
            content='Testing author relationship.',
            author=self.user,
        )
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.author.username, 'testuser')

    def test_author_related_name(self):
        Post.objects.create(
            title='Related Post 1',
            content='Content 1.',
            author=self.user,
        )
        Post.objects.create(
            title='Related Post 2',
            content='Content 2.',
            author=self.user,
        )
        self.assertEqual(self.user.posts.count(), 2)
        titles = list(self.user.posts.values_list('title', flat=True))
        self.assertIn('Related Post 1', titles)
        self.assertIn('Related Post 2', titles)

    def test_author_cascade_delete(self):
        post = Post.objects.create(
            title='Cascade Test',
            content='Testing cascade delete.',
            author=self.user,
        )
        post_id = post.id
        self.user.delete()
        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_author_is_required(self):
        with self.assertRaises(IntegrityError):
            Post.objects.create(
                title='No Author',
                content='This post has no author.',
                author=None,
            )

    def test_title_is_required(self):
        post = Post(
            title='',
            content='Content without title.',
            author=self.user,
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_content_is_required(self):
        post = Post(
            title='Title without content',
            content='',
            author=self.user,
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_title_max_length(self):
        max_length = Post._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_title_exceeds_max_length(self):
        post = Post(
            title='A' * 201,
            content='Content.',
            author=self.user,
        )
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_title_at_max_length(self):
        post = Post(
            title='A' * 200,
            content='Content.',
            author=self.user,
        )
        post.full_clean()

    def test_created_at_auto_set(self):
        before = timezone.now()
        post = Post.objects.create(
            title='Timestamp Test',
            content='Testing auto timestamp.',
            author=self.user,
        )
        after = timezone.now()
        self.assertIsNotNone(post.created_at)
        self.assertGreaterEqual(post.created_at, before)
        self.assertLessEqual(post.created_at, after)

    def test_created_at_not_updated_on_save(self):
        post = Post.objects.create(
            title='No Update Test',
            content='Original content.',
            author=self.user,
        )
        original_created_at = post.created_at
        post.title = 'Updated Title'
        post.save()
        post.refresh_from_db()
        self.assertEqual(post.created_at, original_created_at)

    def test_content_allows_long_text(self):
        long_content = 'A' * 10000
        post = Post.objects.create(
            title='Long Content',
            content=long_content,
            author=self.user,
        )
        post.refresh_from_db()
        self.assertEqual(post.content, long_content)

    def test_id_is_not_editable(self):
        id_field = Post._meta.get_field('id')
        self.assertFalse(id_field.editable)

    def test_id_is_primary_key(self):
        id_field = Post._meta.get_field('id')
        self.assertTrue(id_field.primary_key)

    def test_multiple_authors_can_have_posts(self):
        user2 = User.objects.create_user(
            username='anotheruser',
            password='testpass123',
        )
        post1 = Post.objects.create(
            title='Post by user 1',
            content='Content.',
            author=self.user,
        )
        post2 = Post.objects.create(
            title='Post by user 2',
            content='Content.',
            author=user2,
        )
        self.assertEqual(self.user.posts.count(), 1)
        self.assertEqual(user2.posts.count(), 1)
        self.assertEqual(post1.author, self.user)
        self.assertEqual(post2.author, user2)