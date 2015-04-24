# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('browser', '0003_ncbi_taxonomy'),
    ]

    operations = [
        migrations.CreateModel(
            name='NcbiTaxonomy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(unique=True)),
                ('node_rank', models.CharField(max_length=64)),
                ('taxon_name', models.CharField(max_length=128)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='browser.NcbiTaxonomy', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='ncbi_taxonomy',
            name='parent',
        ),
        migrations.DeleteModel(
            name='NCBI_Taxonomy',
        ),
    ]
