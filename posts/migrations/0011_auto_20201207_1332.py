# Generated by Django 2.2.6 on 2020-12-07 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',)},
        ),
    ]
