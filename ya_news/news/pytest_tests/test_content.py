from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.urls import reverse

from news.models import Comment


@pytest.mark.django_db
def test_count_news_on_home_page(all_news, client):
    url = reverse('news:home')
    response = client.get(url)
    assert len(
        response.context.get('object_list')
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorting_news(all_news, client):
    url = reverse('news:home')
    response = client.get(url)
    news = response.context.get('object_list')
    assert news[0].date > news[1].date


@pytest.mark.django_db
def test_sorting_comment(client, news, commenter, comment):
    comment = Comment.objects.create(
        news=news,
        author=commenter,
        text='new comment'
    )
    comment.created = datetime.today() + timedelta(days=1)
    comment.save()
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context.get('news')
    comments = news.comment_set.all()
    assert comments[0].created < comments[1].created


@pytest.mark.parametrize(
    'url, result',
    (
        ('news:detail', True),
        ('news:edit', False)
    )
)
def test_form_in_context_for_not_commenter(url, result, comment, admin_client):
    url = reverse(url, args=(comment.id,))
    response = admin_client.get(url)
    assert ('form' in response.context) is result
