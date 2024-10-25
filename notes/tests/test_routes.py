from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Roman')
        cls.reader = User.objects.create(username='Left')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_logined_user(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
        )
        slug = self.notes.slug
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (slug,)),
            ('notes:edit', (slug,)),
            ('notes:delete', (slug,)),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user):
                    response = self.client.get(reverse(
                        name,
                        args=args,
                    ))
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        slug = self.notes.slug
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (slug,)),
            ('notes:edit', (slug,)),
            ('notes:delete', (slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
