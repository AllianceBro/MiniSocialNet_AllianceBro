from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class Settings(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a test Group object
        Group.objects.create(
            title='DungeonMasters',
            slug='D_M',
            description='Some description',
        )
        cls.group = Group.objects.get(slug='D_M')

        # Сreate site for flatpages
        cls.site = Site(pk=1, domain='Beidou.com', name='Beidou.com')
        cls.site.save()
        # Сreate flatpage about author
        cls.about_author = FlatPage.objects.create(
            url=reverse('about'),
            title='Об авторе',
            content='Немного о себе',
            registration_required=False,
        )
        cls.about_author.sites.add(cls.site)
        # Create flatpage about technolgies
        cls.about_spec = FlatPage.objects.create(
            url=reverse('terms'),
            title='Об технологиях',
            content='Джанга переджанга',
            registration_required=False,
        )
        cls.about_spec.sites.add(cls.site)

    def setUp(self):
        # Test guest client
        self.guest_client = Client()
        # Test authorized client
        self.user = User.objects.create(username='Leatherman')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Test second authorized user
        self.stranger_user = User.objects.create(username='Stranger')
        self.stranger_client = Client()
        self.stranger_client.force_login(self.stranger_user)
        # Create a test post
        post_text = 'Что то написано'
        self.post = Post.objects.create(
            text=post_text,
            author=self.user,
            group=self.group,
        )
        # Making urls
        self.POST_URL = reverse('post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        })
        self.POST_EDIT_URL = reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        })
        self.ADD_COMMENT_URL = reverse('add_comment', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        })
        self.COMMENT_REDIRECT_URL = (
            f"{ reverse('login') }"
            f"?next={ self.ADD_COMMENT_URL }"
        )
        self.POSTEDIT_REDIRECT_URL = (
            f"{ reverse('login') }"
            f"?next={ self.POST_EDIT_URL }"
        )
        # Clear cache everytime we run a test
        cache.clear()
