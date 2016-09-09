# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0002_auto_20160223_0254'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenestate',
            name='machine_state',
            field=models.IntegerField(default=0, choices=[(0, b'START'), (1, b'CHECK_RESULT'), (2, b'CHECK_SET'), (3, b'END_NORMAL'), (4, b'END_FAILURE'), (5, b'WAIT_INFORM')]),
        ),
        migrations.AddField(
            model_name='scenestate',
            name='target_singular',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='scenestate',
            name='action',
            field=models.IntegerField(default=0, choices=[(1, b'INITIAL'), (2, b'INFORM'), (3, b'ACCEPT'), (4, b'REJECT'), (5, b'MOVE_BACK')]),
        ),
    ]
