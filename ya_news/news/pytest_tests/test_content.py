from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News

url_home = reverse('news:home')


@pytest.mark.django_db
def test_count_news_on_home_page(all_news, client):
    response = client.get(url_home)
    assert len(
        response.context.get('object_list')
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorting_news(all_news, client):
    response = client.get(url_home)
    news = response.context.get('object_list')
    ids = [item.id for item in news]
    news_from_db = list(News.objects.values_list('id', flat=True)[:10])
    assert ids == news_from_db


@pytest.mark.django_db
def test_sorting_comment(client, news, commenter, comment, detail_url):
    comment = Comment.objects.create(
        news=news,
        author=commenter,
        text='new comment'
    )
    comment.created = datetime.today() + timedelta(days=1)
    comment.save()
    response = client.get(detail_url)
    news = response.context.get('news')
    comments = news.comment_set.all()
    assert comments[0].created < comments[1].created


@pytest.mark.parametrize(
    'user_client, result',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),

    )
)
@pytest.mark.django_db
def test_form_in_context_for_not_commenter(detail_url, result, user_client):
    response = user_client.get(detail_url)
    assert ('form' in response.context) is result
    if result:
        assert isinstance(response.context.get('form'), CommentForm)
