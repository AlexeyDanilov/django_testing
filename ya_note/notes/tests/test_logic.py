from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    FORM_DATA = {
        'title': 'News',
        'text': 'text about',
        'slug': 'news'
    }

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Note',
            text='text',
            slug='slug',
            author=cls.author
        )
        cls.note_count = Note.objects.count()
        cls.create_url = reverse('notes:add')
        cls.update_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_anonimous_user(self):
        response = self.client.post(self.create_url, data=self.FORM_DATA)
        expected_count = Note.objects.count()
        self.assertEqual(self.note_count, expected_count)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=/add/')

    def test_auth_user(self):
        response = self.author_client.post(
            self.create_url,
            data=self.FORM_DATA
        )
        note_count = Note.objects.count()
        expected_count = self.note_count + 1
        self.assertEqual(note_count, expected_count)
        self.assertRedirects(response, reverse('notes:success'))

    def test_repeat_slug(self):
        self.FORM_DATA['slug'] = 'slug'
        self.author_client.post(self.create_url, data=self.FORM_DATA)
        expected_count = Note.objects.count()
        self.assertEqual(expected_count, self.note_count)

    def test_update_note_by_author(self):
        self.author_client.post(self.update_url, data=self.FORM_DATA)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.FORM_DATA['text'])
        self.assertEqual(self.note.title, self.FORM_DATA['title'])
        self.assertEqual(self.note.slug, self.FORM_DATA['slug'])

    def test_update_by_not_author(self):
        response = self.reader_client.post(
            self.update_url,
            data=self.FORM_DATA
        )
        self.note.refresh_from_db()
        updated_note = Note.objects.first()
        self.assertEqual(self.note.title, updated_note.title)
        self.assertEqual(self.note.text, updated_note.text)
        self.assertEqual(self.note.slug, updated_note.slug)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_note_by_author(self):
        self.author_client.delete(self.delete_url)
        expected_count = Note.objects.count()
        self.assertEqual(expected_count, self.note_count - 1)

    def test_delete_not_by_not_author(self):
        response = self.reader_client.delete(self.delete_url)
        expected_count = Note.objects.count()
        self.assertEqual(expected_count, self.note_count)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_auto_slug(self):
        Note.objects.all().delete()
        self.FORM_DATA.pop('slug')
        self.author_client.post(self.create_url, data=self.FORM_DATA)
        note = Note.objects.last()
        self.assertEqual(note.slug, slugify(note.title))
