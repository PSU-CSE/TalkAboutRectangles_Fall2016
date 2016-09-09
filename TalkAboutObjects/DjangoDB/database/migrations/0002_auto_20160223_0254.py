# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scenestate',
            name='actions_taken',
        ),
        migrations.AddField(
            model_name='scenestate',
            name='action',
            field=models.IntegerField(default=0, choices=[(1, b'INITIAL'), (2, b'INFORM'), (3, b'ACCEPT'), (4, b'REJECT')]),
        ),
        migrations.AddField(
            model_name='scenestate',
            name='system_output',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='scenestate',
            name='user_input',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='scenestate',
            name='scene',
            field=models.ForeignKey(related_name='scene_state', to='database.Scene'),
        ),
        migrations.DeleteModel(
            name='Action',
        ),
    ]
