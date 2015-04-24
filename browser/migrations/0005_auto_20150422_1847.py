# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browser', '0004_auto_20150422_1804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ncbitaxonomy',
            name='parent',
        ),
        migrations.DeleteModel(
            name='NcbiTaxonomy',
        ),
    ]
