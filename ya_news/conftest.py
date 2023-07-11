from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def news():
    return News.objects.create(
        title='News',
        text='some text'
    )


@pytest.fixture
def commenter(django_user_model):
    return django_user_model.objects.create(username='commenter')


@pytest.fixture
def comment(commenter, news):
    return Comment.objects.create(
        news=news,
        author=commenter,
        text='comment'
    )


@pytest.fixture
def comment_client(commenter):
    client = Client()
    client.force_login(commenter)
    return client


@pytest.fixture
def comment_id(comment):
    return comment.id


@pytest.fixture
def form_data():
    return {
        'text': 'new text'
    }


@pytest.fixture
def all_news():
    all_news = [News(
        title=f'Новость {index}',
        text='Текст',
        date=datetime.today() - timedelta(days=index)) for index in range(
        settings.NEWS_COUNT_ON_HOME_PAGE + 5
    )]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))
