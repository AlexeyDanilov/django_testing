from http import HTTPStatus
from pytest_django.asserts import assertRedirects

import pytest
from django.urls import reverse


action_urls = 'url', (('news:edit'), ('news:delete'))


@pytest.mark.django_db
def test_home_page(admin_client):
    url = reverse('news:home')
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user_client, result',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(*action_urls)
def test_get_action_comment(user_client, result, url, comment):
    url = reverse(url, args=(comment.id,))
    response = user_client.get(url)
    assert response.status_code == result


@pytest.mark.parametrize(*action_urls)
def test_action_pages_by_anonim(client, url, comment):
    url = reverse(url, args=(comment.id,))
    response = client.get(url)
    redirect_url = reverse('users:login') + f'?next={url}'
    assertRedirects(response, redirect_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        (reverse('users:login')),
        (reverse('users:logout')),
        (reverse('users:signup')),
        (reverse('news:home')),
        (pytest.lazy_fixture('detail_url'))
    )
)
def test_public_pages_by_anonim(url, client):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
