from django import forms
from django.urls import reverse

from posts.models import Group, Post

from .test_settings import Settings

# Making constant urls
NEWPOST_URL = reverse('new_post')


class TestFormClass(Settings):
    def test_can_create_new_post(self):
        """ Test ability to create new posts """
        text = 'AYA YA YA'
        form_data = {
            'text': text,
            'group': self.group.id,
        }
        # Delete all posts except a new one (we'll create it soon)
        Post.objects.all().delete()
        # Send the form
        response = self.authorized_client.post(
            NEWPOST_URL,
            data=form_data,
            follow=True
        )
        page = response.context.get('page')
        self.assertEqual(len(page), 1)
        self.assertEqual(page[0].text, text)
        self.assertEqual(page[0].group, self.group)
        self.assertEqual(page[0].author, self.user)
        self.assertEqual(response.status_code, 200)

    def test_can_edit_existing_post(self):
        """ Test ability to edit existing posts """
        new_group = Group.objects.create(
            title='JatetskiyGus',
            slug='jat_gus',
            description='Some description',
        )
        form_data = {
            'text': 'Eto noviy text',
            'group': new_group.id,
        }
        # Send the form
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group, new_group)
        self.assertEqual(response.status_code, 200)

    def test_form_pages_for_context(self):
        """ Test pages with forms for correct context """
        form_fields = {
            'group': forms.ChoiceField,
            'text': forms.CharField,
        }
        urls = [
            NEWPOST_URL,
            self.POST_EDIT_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for field, type_of_field in form_fields.items():
                    # Get form fields from the context
                    form_field = response.context.get('form').fields.get(field)
                    self.assertIsInstance(form_field, type_of_field)

    def test_user_edits_correct_post(self):
        """ Test if post in editform instance is the one we want to edit """
        response = self.authorized_client.get(self.POST_EDIT_URL)
        # Is it a correct post?
        self.assertEqual(
            response.context.get('post'),
            self.post
        )

    def test_img_is_loaded_correctly(self):
        """ Test image is being loaded correctly """
        path_to_image = 'media/posts/wifu.jpg'
        # Delete all posts except a new one (we'll create it soon)
        Post.objects.all().delete()
        with open(path_to_image, 'rb') as img:
            form_data = {
                'text': 'Пост с картинкой',
                'group': self.group.id,
                'image': img
            }
            response = self.authorized_client.post(
                NEWPOST_URL,
                data=form_data,
                follow=True
            )
        page = response.context.get('page')
        self.assertEqual(len(page), 1)
        self.assertIsNotNone(page[0].image)

    def test_not_img_is_not_being_loaded(self):
        """ Test if form doesnt send a not image file """
        path_to_mp3 = 'media/posts/La_music.mp3'
        # Delete all posts except a new one (we'll create it soon)
        Post.objects.all().delete()
        with open(path_to_mp3, 'rb') as mp3:
            form_data = {
                'text': 'Пост с кракозяброй',
                'image': mp3
            }
            response = self.authorized_client.post(
                NEWPOST_URL,
                data=form_data,
                follow=True
            )
        page = response.context.get('page')
        self.assertEqual(len(page), 1)
        self.assertIsNone(page[0].image)

    def test_authorized_can_add_comment(self):
        """ Test if authorized user can add comments """
        form_data = {
            'text': 'Офигенный пост, моей маме понравилось!'
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        comment = response.context.get('comments')[0]
        self.assertEqual(comment.text, form_data['text'])
