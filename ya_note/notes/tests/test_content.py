from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        Note.objects.bulk_create(
            Note(
                title=f'title {i}',
                text=f'text {i}',
                slug=f'slug{i}',
                author=cls.author
            ) for i in range(5))
        cls.another_author = User.objects.create(username='another_author')
        Note.objects.bulk_create(
            Note(
                title=f'title {i}',
                text=f'text {i}',
                slug=f'slug{i}',
                author=cls.another_author
            ) for i in
            range(5, 11))

    def test_count_notes_on_page(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        notes_count_by_author = self.author.note_set.count()
        response = self.client.get(url)
        notes_count_from_page = len(response.context.get('object_list'))
        self.assertEqual(notes_count_by_author, notes_count_from_page)

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
