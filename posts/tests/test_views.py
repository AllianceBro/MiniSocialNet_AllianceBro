from django.core.cache import cache
from django.urls import reverse

from posts.models import Follow, Post

from .test_settings import Settings

# Making constant urls
USERNAME = 'Leatherman'
GROUP_SLUG = 'D_M'
HOMEPAGE_URL = reverse('index')
ABOUT_URL = reverse('about')
TERMS_URL = reverse('terms')
NEWPOST_URL = reverse('new_post')
GROUP_URL = reverse('group_post', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('profile', kwargs={'username': USERNAME})
FOLLOW_URL = reverse('profile_follow', kwargs={'username': USERNAME})
UNFOLLOW_URL = reverse('profile_unfollow', kwargs={'username': USERNAME})
FOLLOW_INDEX_URL = reverse('follow_index')


class PostPagesTest(Settings):
    def test_have_post_in_the_context(self):
        """Test if there is a post in the context"""
        self.stranger_client.get(FOLLOW_URL)
        urls = [
            HOMEPAGE_URL,
            GROUP_URL,
            PROFILE_URL,
            FOLLOW_INDEX_URL,
            self.POST_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.stranger_client.get(url)
                if response.context.get('post'):
                    post = response.context.get('post')
                else:
                    page = response.context.get('page')
                    self.assertEqual(len(page), 1)
                    post = page[0]
                self.assertEqual(post, self.post)

    def test_have_group_in_context(self):
        """Test if there is a group in the context"""
        urls = [
            GROUP_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.context.get('group'),
                    self.group
                )

    def test_urls_for_paginator(self):
        """Test if url has correct paginator"""
        urls = [
            PROFILE_URL,
            HOMEPAGE_URL,
            GROUP_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.context.get('paginator').per_page,
                    10
                )

    def test_about_flatpage_context(self):
        """Test about flatpage context"""
        response = self.authorized_client.get(ABOUT_URL)
        self.assertEqual(
            response.context.get('flatpage').content,
            'Немного о себе'
        )
        self.assertEqual(
            response.context.get('flatpage').title,
            'Об авторе'
        )

    def test_terms_flatpage_context(self):
        """Test terms flatpage context"""
        response = self.authorized_client.get(TERMS_URL)
        self.assertEqual(
            response.context.get('flatpage').content,
            'Джанга переджанга'
            )
        self.assertEqual(
            response.context.get('flatpage').title,
            'Об технологиях'
        )

    def test_cache_for_index(self):
        """Test correct cache work in index"""
        response = self.authorized_client.get(HOMEPAGE_URL)
        page_cached = response.content
        Post.objects.create(
            text='Noviy Post',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(HOMEPAGE_URL)
        page_new = response.content
        self.assertEqual(page_cached, page_new)
        cache.clear()
        response = self.authorized_client.get(HOMEPAGE_URL)
        page_brand_new = response.content
        self.assertNotEqual(page_cached, page_brand_new)

    def test_can_subscribe_and_unfollow(self):
        """Test if authorized user can subscribe"""
        self.stranger_client.get(FOLLOW_URL)
        self.assertTrue(
            Follow.objects.filter(
                user=self.stranger_user,
                author=self.user
            ).exists()
        )

    def test_can_unsubscribe(self):
        """Test if authorized user can unsubscribe"""
        Follow.objects.create(
            user = self.stranger_user,
            author = self.user
        )
        self.stranger_client.get(UNFOLLOW_URL)
        self.assertFalse(
            Follow.objects.filter(
                user=self.stranger_user,
                author=self.user
            ).exists()
        )

    def test_show_favorite_authors_posts(self):
        """Test if favorite author posts show to subscriber"""
        self.stranger_client.get(FOLLOW_URL)
        response = self.stranger_client.get(FOLLOW_INDEX_URL)
        post = response.context.get('page')[0]
        self.assertEqual(post, self.post)

    def test_dont_show_unfavorite_authors_posts(self):
        """Test other user's favorite list (return must be empty)"""
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        page = response.context.get('page')
        self.assertEqual(len(page), 0)
