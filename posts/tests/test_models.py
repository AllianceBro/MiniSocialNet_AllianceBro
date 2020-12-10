from .test_settings import Settings


class PostModelTest(Settings):
    def test_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        post = self.post
        field_help_txt = {
            'text': 'Не оставляй это поле пустым',
            'group': 'Выбери из уже существующих',
        }
        for value, expected in field_help_txt.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_str_func_of_models(self):
        """Check __str__ funcs"""
        post = self.post
        group = self.group
        post_str_data = [
            post.text[0:15],
            post.author.username,
            post.pub_date.strftime('%d/%m/%Y'),
            post.group.title
        ]
        res = '|'.join(post_str_data)
        self.assertEqual(str(post), res)
        self.assertEqual(str(group), group.title)
