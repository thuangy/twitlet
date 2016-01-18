# -*- coding: utf-8 -*-
# Generated by Django 1.10.dev20160115151452 on 2016-01-16 23:49
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('twitlet', '0003_tweetlet'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweetlet',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 16, 23, 49, 15, 404993, tzinfo=utc), verbose_name='date published'),
            preserve_default=False,
        ),
    ]