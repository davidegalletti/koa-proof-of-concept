# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255L, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='KUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('login', models.CharField(max_length=255L, blank=True)),
                ('password', models.CharField(max_length=255L, blank=True)),
                ('name', models.CharField(max_length=255L, blank=True)),
                ('surname', models.CharField(max_length=255L, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PermissionHolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('methods', models.ManyToManyField(to='application.Method', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255L, blank=True)),
                ('permission_holder', models.OneToOneField(to='userauthorization.PermissionHolder')),
                ('users', models.ManyToManyField(to='userauthorization.KUser')),
            ],
        ),
        migrations.AddField(
            model_name='kuser',
            name='permission_holder',
            field=models.OneToOneField(to='userauthorization.PermissionHolder'),
        ),
        migrations.AddField(
            model_name='group',
            name='permission_holder',
            field=models.OneToOneField(to='userauthorization.PermissionHolder'),
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(to='userauthorization.KUser'),
        ),
    ]
