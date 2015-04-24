# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browser', '0005_auto_20150422_1847'),
    ]

    operations = [
        migrations.CreateModel(
            name='NcbiTaxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('taxon_id', models.IntegerField(unique=True)),
                ('node_rank', models.CharField(max_length=64)),
                ('taxon_name', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
