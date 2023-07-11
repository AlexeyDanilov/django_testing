from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


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

    def test_notes_on_page_by_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note, response.context.get('object_list'))

    def test_notes_on_page_by_not_author(self):
        self.client.force_login(self.another_author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertNotIn(self.note, response.context.get('object_list'))

    def test_getting_form(self):
        note = Note.objects.filter(author=self.author).first()
        self.client.force_login(self.author)
        urls = [
            ('notes:add', None),
            ('notes:edit', note.slug),
        ]
        for url, arg in urls:
            url = reverse(url, args=(arg,)) if arg else reverse(url)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context.get('form'), NoteForm)
