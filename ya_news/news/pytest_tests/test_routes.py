from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_client',
    (
        (pytest.lazy_fixture('client')),
        (pytest.lazy_fixture('admin_client'))
    ),
)
def test_home_page(user_client):
    url = reverse('news:home')
    response = user_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page_for_anonim(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user_client, result',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize('url', (('news:edit'), ('news:delete')))
def test_get_action_comment(user_client, result, url, comment):
    url = reverse(url, args=(comment.id,))
    response = user_client.get(url)
    assert response.status_code == result


@pytest.mark.parametrize('page', (('news:edit'), ('news:delete')))
def test_action_pages_by_anonim(client, page, comment):
    url = reverse(page, args=(comment.id,))
    response = client.get(url)
    redirect_url = reverse('users:login') + f'?next={url}'
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'page',
    (
        ('users:login'),
        ('users:logout'),
        ('users:signup')
    )
)
def test_auth_pages_by_anonim(page, client):
    url = reverse(page)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
