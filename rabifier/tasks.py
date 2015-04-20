from __future__ import absolute_import

import tempfile
import subprocess

from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def run_rabifier(sequences, **kwargs):
    seq_file = tempfile.NamedTemporaryFile()
    seq_file.write(sequences)
    seq_file.seek(0)
    proc = subprocess.Popen(['/home/jsurkont/.virtualenv/virtual/bin/python',
                             '/home/jsurkont/lab/projects/03/rabifier/rabmyfire.py', seq_file.name, '--outfmt', 'text'],
                            stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out