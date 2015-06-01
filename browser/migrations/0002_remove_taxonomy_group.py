# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browser', '0001_squashed_0006_ncbitaxonomy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taxonomy',
            name='group',
        ),
    ]
