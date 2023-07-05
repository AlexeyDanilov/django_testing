from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='title',
            text='text',
            slug='title',
            author=cls.author
        )

    def test_availability_static_pages(self):
        urls = {
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        }
        for url, param in urls:
            with self.subTest():
                url = reverse(url, args=param)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_action_routes(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for user, status in user_statuses:
            self.client.force_login(user)

            for url, args in urls:
                with self.subTest():
                    url = reverse(url, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_routes(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )

        for url, args in urls:
            with self.subTest():
                url = reverse(url, args=args)
                self.client.force_login(self.reader)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect(self):
        urls = (
            'notes:list', 'notes:success', 'notes:add',
        )

        for url in urls:
            with self.subTest():
                response = self.client.get(reverse(url))
                redirect = reverse('users:login') + f'?next={reverse(url)}'
                self.assertRedirects(response, redirect)
