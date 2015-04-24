# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gprotein', models.CharField(max_length=32)),
                ('log10_evalue_rab', models.FloatField()),
                ('log10_evalue_nonrab', models.FloatField(blank=True)),
                ('rabf', models.CharField(max_length=256)),
                ('israb', models.BooleanField()),
                ('rab_subfamily', models.CharField(max_length=16)),
                ('rab_subfamily_score', models.FloatField()),
                ('rab_subfamily_top5', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protein', models.CharField(unique=True, max_length=32)),
                ('transcript', models.CharField(unique=True, max_length=32)),
                ('gene', models.CharField(max_length=64)),
                ('uniprot', models.CharField(max_length=32, blank=True)),
                ('description', models.TextField()),
                ('seq', models.TextField()),
                ('comment', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taxon', models.IntegerField(unique=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('name_common', models.CharField(max_length=128, blank=True)),
                ('group', models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='annotation',
            name='protein',
            field=models.ForeignKey(to='browser.Protein'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='taxonomy',
            field=models.ForeignKey(to='browser.Taxonomy'),
        ),
    ]
