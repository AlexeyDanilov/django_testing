from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.parametrize(
    'user_client, count',
    (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('comment_client'), 1)
    )
)
@pytest.mark.django_db
def test_create_comment(user_client, count, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    user_client.post(url, data=form_data)
    assert news.comment_set.count() == count


def test_stop_words(comment_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] += BAD_WORDS[0]
    response = comment_client.post(url, data=form_data)
    assertFormError(
        response=response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert news.comment_set.count() == 0


def test_author_can_edit_comment(comment_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = comment_client.post(url, data=form_data)
    expected_url = reverse(
        'news:detail', kwargs={'pk': comment.news.pk}
    ) + '#comments'
    comment.refresh_from_db()
    assertRedirects(response, expected_url)
    assert comment.text == form_data.get('text')


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        form_data,
        comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, data=form_data)
    old_text = comment.text
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == old_text


@pytest.mark.parametrize(
    'user_client, count', (
        (pytest.lazy_fixture('comment_client'), 0),
        (pytest.lazy_fixture('admin_client'), 1)
    )
)
def test_who_can_delete_comment(user_client, comment, count):
    url = reverse('news:delete', args=(comment.id,))
    user_client.post(url)
    assert Comment.objects.count() == count
