# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100L)),
                ('description', models.CharField(max_length=2000L, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxonomyLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table_name', models.CharField(max_length=255L, blank=True)),
                ('description_field', models.CharField(max_length=255L, db_column=b'descriptionField', blank=True)),
                ('id_field', models.CharField(max_length=255L, db_column=b'idField', blank=True)),
                ('name_field', models.CharField(max_length=255L, db_column=b'nameField', blank=True)),
                ('label', models.CharField(max_length=255L, blank=True)),
                ('default', models.BooleanField(default=True)),
                ('dataset_structure', models.ForeignKey(to='entity.Entity', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxonomyLevelGraph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('foreign_key_upper', models.CharField(max_length=255L)),
                ('lower', models.ForeignKey(related_name='lower', to='taxonomy.TaxonomyLevel')),
                ('upper', models.ForeignKey(related_name='upper', to='taxonomy.TaxonomyLevel')),
            ],
        ),
        migrations.AddField(
            model_name='taxonomylevel',
            name='upper_levels',
            field=models.ManyToManyField(related_name='lower_levels', through='taxonomy.TaxonomyLevelGraph', to='taxonomy.TaxonomyLevel'),
        ),
        migrations.AddField(
            model_name='taxonomy',
            name='first_level',
            field=models.ForeignKey(to='taxonomy.TaxonomyLevel'),
        ),
    ]
