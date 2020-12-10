from django.urls import reverse

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
NEWPOST_REDIRECT_URL = f"{ reverse('login') }?next={ NEWPOST_URL }"


class StaticURLTests(Settings):
    def test_urls_give_correct_code_for_everybody(self):
        """Test if pages are shown to the everybody"""
        urls = [
            HOMEPAGE_URL,
            GROUP_URL,
            ABOUT_URL,
            TERMS_URL,
            PROFILE_URL,
            self.POST_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    200
                )

    def test_urls_give_correct_code_for_authorized(self):
        """Test if pages are shown to the authorized users"""
        urls = [
            NEWPOST_URL,
            self.POST_EDIT_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    200
                )

    def test_redirect_for_anonym(self):
        """Test if anonyms are being redirected"""
        urls_redirects = {
            self.POST_EDIT_URL: self.POSTEDIT_REDIRECT_URL,
            NEWPOST_URL: NEWPOST_REDIRECT_URL,
            self.ADD_COMMENT_URL: self.COMMENT_REDIRECT_URL,
        }
        for url, redirect in urls_redirects.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    redirect
                )

    def test_redirect_for_other_user_editing_url(self):
        """Test if some other user is being redirected"""
        response = self.stranger_client.get(self.POST_EDIT_URL, follow=True)
        self.assertRedirects(response, self.POST_URL)

    def test_urls_uses_correct_template(self):
        """Test if urls shows users a correct html template"""
        templates_url_names = {
            HOMEPAGE_URL: 'posts/index.html',
            GROUP_URL: 'group.html',
            NEWPOST_URL: 'posts/new_post.html',
            self.POST_EDIT_URL: 'posts/new_post.html',
            self.POST_URL: 'posts/profile.html',
            PROFILE_URL: 'posts/profile.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_show_404(self):
        response = self.authorized_client.get(PROFILE_URL+'/data/')
        self.assertEqual(response.status_code, 404)
