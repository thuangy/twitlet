# -*- coding: utf-8 -*-
# Generated by Django 1.10.dev20160115151452 on 2016-01-17 01:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitlet', '0005_tweetlet_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweetlet',
            name='user',
        ),
    ]
