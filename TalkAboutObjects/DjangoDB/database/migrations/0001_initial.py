# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_input', models.CharField(max_length=256)),
                ('system_output', models.CharField(max_length=256)),
                ('action', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Rectangle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('r', models.IntegerField()),
                ('g', models.IntegerField()),
                ('b', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Scene',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('num_objects', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SceneState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actions_taken', models.ManyToManyField(to='database.Action', null=True)),
                ('previous_state', models.ForeignKey(to='database.SceneState', null=True)),
                ('rectangles', models.ManyToManyField(related_name='rectangles', null=True, to='database.Rectangle')),
                ('scene', models.ForeignKey(to='database.Scene')),
                ('selected_rectangles', models.ManyToManyField(related_name='selected_rectangles', null=True, to='database.Rectangle')),
            ],
        ),
    ]
