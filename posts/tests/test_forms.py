from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Group, Post

from .test_settings import Settings

# Making constants
NEWPOST_URL = reverse('new_post')


class TestFormClass(Settings):
    def test_can_create_new_post(self):
        """Test ability to create new posts"""
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
        """Test ability to edit existing posts"""
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
        # Get post from the 'post_page' (there is only one post on the page)
        post = response.context.get('post')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, new_group)
        self.assertEqual(response.status_code, 200)

    def test_form_pages_for_context(self):
        """Test pages with forms for correct context"""
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
        """Test if post in editform instance is the one we want to edit"""
        response = self.authorized_client.get(self.POST_EDIT_URL)
        # Is it a correct post?
        self.assertEqual(
            response.context.get('post'),
            self.post
        )

    def test_image_is_loaded_correctly(self):
        """Test image is being loaded correctly"""
        # Delete all posts except a new one (we'll create it soon)
        Post.objects.all().delete()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded= SimpleUploadedFile(
            name='wifu.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост с картинкой',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            NEWPOST_URL,
            data=form_data,
            follow=True
        )
        page = response.context.get('page')
        self.assertEqual(len(page), 1)
        self.assertIsNotNone(page[0].image)
        self.assertEqual(page[0].image.size, uploaded.size)

    def test_authorized_can_add_comment(self):
        """Test if authorized user can add comments"""
        form_data = {
            'text': 'Офигенный пост, моей маме понравилось!'
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        comment_list = response.context.get('comments')
        self.assertEqual(len(comment_list), 1)
        self.assertEqual(comment_list[0].text, form_data['text'])
        self.assertEqual(comment_list[0].author, self.user)
        self.assertEqual(comment_list[0].post, self.post)
