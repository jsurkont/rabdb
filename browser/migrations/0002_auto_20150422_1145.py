# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('browser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='log10_evalue_nonrab',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
