import re

from django import forms
from networkx.readwrite import json_graph

from .models import Taxonomy, Annotation, NcbiTaxonomy


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def get_rab_sf():
    return [(x, x.title()) for x in natural_sort(
        [ann['rab_subfamily'] for ann in Annotation.objects.values('rab_subfamily').distinct()])]


def filter_taxa():
    graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(NcbiTaxonomy.objects.get(taxon_id=1))[0])
    nodes = [graph.node[x]['data'] for x, d in graph.out_degree().items() if d > 0]
    pattern = re.compile('^[A-Z][a-z]+$')
    ranks = {'no rank', 'kingdom', 'phylum', 'order', 'subkingdom'}
    id_name = []
    for x in nodes:
        if x['node_rank'] in ranks and pattern.findall(x['taxon_name']):
            id_name.append((x['taxon_id'], x['taxon_name']))
    return sorted(id_name, key=lambda x: x[1])


class RabBrowserForm(forms.Form):
    rab_subfamily = forms.ChoiceField(choices=[('all', 'All')] + get_rab_sf(), label='Rab subfamily', required=False)
    species = forms.ChoiceField(choices=[('all', 'All')] + [(x.taxon, x.name) for x in
                                                            Taxonomy.objects.all().order_by('name')],
                                label='Species',
                                required=False)
    taxon = forms.ChoiceField(choices=[('all', 'All')] + filter_taxa(), label='Taxon', required=False)

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
    rab_subfamily = forms.ChoiceField(
        choices=[('', '---')] + get_rab_sf(), label='Rab subfamily', required=True)
    taxon = forms.ChoiceField(choices=[('', '---')] + filter_taxa(), label='Taxon', required=True)

    def clean(self):
        cleaned_data = super(RabProfileForm, self).clean()
        sf = cleaned_data.get('rab_subfamily')
        tx = cleaned_data.get('taxon')

        if not all([sf, tx]):
            raise forms.ValidationError('Select both Rab subfamily AND taxon.')


class TaxonomyTreeForm(forms.Form):
    taxon = forms.ChoiceField(choices=[('', '---')] + filter_taxa(), label='Taxon', required=True)
