# Generated by Django 2.2.6 on 2020-12-11 17:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20201208_2009'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписчик', 'verbose_name_plural': 'Подписчики'},
        ),
    ]