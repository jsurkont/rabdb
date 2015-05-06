import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django import forms
from Bio import SeqIO

from django.conf import settings


def validate_fasta(text):
    ids = set()
    non_alphabet_pattern = re.compile('[^a-zA-Z]')
    for seq in SeqIO.parse(StringIO(text), 'fasta'):
        if seq.id in ids:
            raise forms.ValidationError('FASTA format error: Repeated sequence ID %(seqid)s', params={'seqid': seq.id})
        else:
            ids.add(seq.id)
        if non_alphabet_pattern.findall(str(seq.seq)):
            raise forms.ValidationError('FASTA format error: Wrong characters in %(seqid)s', params={'seqid': seq.id})
        if len(seq) < 20:
            raise forms.ValidationError('FASTA format error: Sequence %(seqid)s too short, sequences must have at least'
                                        ' 20 amino acids ', params={'seqid': seq.id})
    if len(ids) < 1:
        raise forms.ValidationError('Please input at least one FASTA formatted sequence')
    elif len(ids) > settings.RABMYFIRE_MAX_SEQUENCES:
        raise forms.ValidationError('Input supported for a maximum of %(maxseq)s sequences',
                                    params={'maxseq': settings.RABMYFIRE_MAX_SEQUENCES})


class RabifyForm(forms.Form):
    sequence = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows': 20, 'cols': 100}),
                               required=False, label='Sequence(s)', validators=[validate_fasta])
    fastafile = forms.FileField(required=False)

    evalue_rab = forms.FloatField(
        label='Rab e-value', initial=1e-10, help_text='e-value threshold for best hit search')
    evalue_motif = forms.FloatField(
        label='Motif e-value', initial=1e-04, help_text='e-value threshold for motif search')
    num_motif = forms.IntegerField(
        label='Number of Motifs', initial=1, min_value=0, max_value=5, help_text='minimum number of RabF motifs')
    identity = forms.FloatField(
        label='Percent identity', initial=0.4, min_value=0, max_value=1,
        help_text='minimum sequence identity with subfamily\'s best hit')
    rab_score = forms.FloatField(
        label='Subfamily score', initial=0.2, min_value=0, max_value=1, help_text='minimum subfamily score')
    email = forms.EmailField(required=False, label='e-mail', help_text='send notification when the task is ready')

    def clean(self):
        cleaned_data = super(RabifyForm, self).clean()
        sequence = cleaned_data.get('sequence')
        fastafile = cleaned_data.get('fastafile')

        if not any([sequence, fastafile]):
            raise forms.ValidationError('Sequence information missing. Insert sequences into the text field or '
                                        'upload a file.')
        elif all([sequence, fastafile]):
            raise forms.ValidationError('Use either the text field OR upload a file.')

        if fastafile:
            if fastafile._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File size error: file too big, maximum file size %(filesize)s MB',
                                            params={'filesize': settings.MAX_UPLOAD_SIZE / 1024**2})
            cleaned_data['sequence'] = fastafile.read()
            validate_fasta(cleaned_data.get('sequence'))
