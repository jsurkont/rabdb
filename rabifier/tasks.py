from __future__ import absolute_import

from django.core.mail import send_mail
from django.conf import settings

import tempfile
import subprocess

from celery import shared_task


@shared_task
def run_rabifier(sequences, **kwargs):
    seq_file = tempfile.NamedTemporaryFile()
    seq_file.write(sequences)
    seq_file.seek(0)
    proc = subprocess.Popen([settings.RABMYFIRE_PYTHON,
                             settings.RABMYFIRE_BIN,
                             seq_file.name,
                             '--outfmt', 'json',
                             '--bh_evalue', str(kwargs['evalue_rab']),
                             '--motif_evalue', str(kwargs['evalue_motif']),
                             '--motif_number', str(kwargs['num_motif']),
                             '--subfamily_identity', str(kwargs['identity']),
                             '--subfamily_score', str(kwargs['rab_score'])
                             ],
                            stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if kwargs.get('email', None):
        send_mail('Your Rab predictions are ready',
                  'To check you Rab predictions follow this link http://localhost:8000/rabifier/{}'.format(run_rabifier.request.id),
                  settings.EMAIL_HOST_USER, [kwargs['email']])
    return out