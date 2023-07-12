from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()
url_list = reverse('notes:list')


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(
            title='Title',
            text='text',
            slug='slug',
            author=cls.author
        )

        cls.another_author = User.objects.create(username='another_author')

        cls.author_client = Client()
        cls.another_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_client.force_login(cls.another_author)

    def test_notes_on_page_by_author(self):
        response = self.author_client.get(url_list)
        self.assertIn(self.note, response.context.get('object_list'))

    def test_notes_on_page_by_not_author(self):
        response = self.another_client.get(url_list)
        self.assertNotIn(self.note, response.context.get('object_list'))

    def test_getting_form(self):
        note = Note.objects.filter(author=self.author).first()
        urls = [
            ('notes:add', None),
            ('notes:edit', note.slug),
        ]
        for url, arg in urls:
            url = reverse(url, args=(arg,)) if arg else reverse(url)
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context.get('form'), NoteForm)
