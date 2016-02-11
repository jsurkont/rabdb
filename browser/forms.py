from django import forms


class RabBrowserForm(forms.Form):

    rab_subfamily = forms.ChoiceField(choices=(), label='Rab subfamily', required=False)
    species = forms.ChoiceField(choices=(), label='Species', required=False)
    taxon = forms.ChoiceField(choices=(), label='Taxon', required=False)

    def __init__(self, rab_subfamily_choices, species_choices, taxon_choices, *args, **kwargs):
        super(RabBrowserForm, self).__init__(*args, **kwargs)
        self.fields['rab_subfamily'].choices = rab_subfamily_choices
        self.fields['species'].choices = species_choices
        self.fields['taxon'].choices = taxon_choices

    def clean(self):
        cleaned_data = super(RabBrowserForm, self).clean()
        sf = cleaned_data.get('rab_subfamily')
        sp = cleaned_data.get('species')
        tx = cleaned_data.get('taxon')

        if sp != 'all' and tx != 'all':
            raise forms.ValidationError('Select either species OR taxon')
        elif all(x == 'all' for x in (sf, sp, tx)):
            raise forms.ValidationError('Select either Rab subfamily OR(and) species or taxon.')


class RabProfileForm(forms.Form):
    rab_subfamily = forms.ChoiceField(choices=(), label='Rab subfamily', required=True)
    taxon = forms.ChoiceField(choices=(), label='Taxon', required=True)

    def __init__(self, rab_subfamily_choices, taxon_choices, *args, **kwargs):
        super(RabProfileForm, self).__init__(*args, **kwargs)
        self.fields['rab_subfamily'].choices = rab_subfamily_choices
        self.fields['taxon'].choices = taxon_choices

    def clean(self):
        cleaned_data = super(RabProfileForm, self).clean()
        sf = cleaned_data.get('rab_subfamily')
        tx = cleaned_data.get('taxon')

        if not all([sf, tx]):
            raise forms.ValidationError('Select both Rab subfamily AND taxon.')


class TaxonomyTreeForm(forms.Form):
    taxon = forms.ChoiceField(choices=(), label='Taxon', required=True)

    def __init__(self, taxon_choices, *args, **kwargs):
        super(TaxonomyTreeForm, self).__init__(*args, **kwargs)
        self.fields['taxon'].choices = taxon_choices
