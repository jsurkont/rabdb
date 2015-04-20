from django import forms


class RabifyForm(forms.Form):
    #a = forms.IntegerField(label='a')
    #b = forms.IntegerField(label='b')

    sequence = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows': 20, 'cols': 100}), label="Sequence(s)")

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
