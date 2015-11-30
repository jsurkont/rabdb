from __future__ import absolute_import

from django.core.mail import send_mail
from django.conf import settings

import tempfile
import json

from celery import shared_task
from rabifier.rabmyfire import Rabmyfire


@shared_task
def run_rabifier(sequences, **kwargs):
    seq_file = tempfile.NamedTemporaryFile()
    seq_file.write(sequences)
    seq_file.seek(0)
    classifier = Rabmyfire(
        bh_evalue=kwargs['evalue_rab'],
        motif_evalue=kwargs['evalue_motif'],
        motif_number=kwargs['num_motif'],
        subfamily_identity=kwargs['identity'],
        subfamily_score=kwargs['rab_score']
    )
    out = json.dumps({putative_rab.seqrecord.id: putative_rab.to_dict() for putative_rab in classifier(seq_file.name)})

    if kwargs.get('email', None):
        send_mail('Your Rab predictions are ready',
                  'To check you Rab predictions follow this link http://localhost:8000/rabifier_app/{}'.format(run_rabifier.request.id),
                  settings.EMAIL_HOST_USER, [kwargs['email']])
    return out
