import json
import math
import re

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404, HttpResponse
from networkx.readwrite import json_graph

from .models import Annotation, NcbiTaxonomy, Taxonomy
from .forms import RabBrowserForm, RabProfileForm, TaxonomyTreeForm


def index(request):
    if request.method == 'POST':
        form = RabBrowserForm(request.POST)
        if form.is_valid():
            sp = form.cleaned_data['species']
            tx = form.cleaned_data['taxon']
            sf = form.cleaned_data['rab_subfamily']
            if sp != 'all':
                taxon = sp
            else:
                taxon = tx
            return HttpResponseRedirect(reverse('browser:browse', kwargs={'tax': taxon, 'sf': sf}))

    else:
        form = RabBrowserForm()

    return render(request, 'browser/index.html', {'form': form})


def details(request, **kwargs):
    ann = get_object_or_404(Annotation, protein__protein=kwargs['protein_id'])

    if 'download' in request.GET:
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}.fasta"'.format(ann.protein.protein)
        cut_seq = lambda s: '\n'.join(s[i: i+80] for i in range(0, len(s), 80))
        response.write('>{} {} {}\n{}'.format(ann.protein.protein, ann.taxonomy.name.replace(' ', '_'),
                                              ann.rab_subfamily, cut_seq(ann.protein.seq)))
        return response

    # Helper functions for drawing domains
    MAX_IMG_LEN = 300.0
    seq_len = len(ann.protein.seq)
    rescale = lambda x: math.ceil(x * MAX_IMG_LEN / seq_len)
    get_rectangle = lambda x: {'x1': rescale(x[0]), 'width': rescale(x[1] - x[0]), 'range': '{}-{}'.format(*x)}

    data = {
        'species': ann.taxonomy.name,
        'protein': ann.protein.protein,
        'gene': ann.protein.gene,
        'rab_subfamily': '{}{} ({:.2f})'.format(ann.rab_subfamily[0].upper(), ann.rab_subfamily[1:],
                                                 ann.rab_subfamily_score),
        'top_subfamilies': ['{} ({:.2g})'.format(*(float(y) if y[0].isdigit() else y[0].upper() + y[1:] for y in x.split()))
                            for x in ann.rab_subfamily_top5.split('|')][1:],
        'evalue_rab': '0' if ann.log10_evalue_rab < -323 else '{:.1e}'.format(10**ann.log10_evalue_rab),
        'evalue_non_rab': '>1e-10' if ann.log10_evalue_nonrab is None else '0' if ann.log10_evalue_nonrab < -323 else '{:.1e}'.format(10**ann.log10_evalue_nonrab),
        'rabf_text': ', '.join('({}, {}-{}, {})'.format(*x.split()) for x in ann.rabf.split('|')),
        'rabf': [get_rectangle(list(map(int, x.split()[1:3]))) for x in ann.rabf.split('|')],
        'sequence': ann.protein.seq,
        'gprotein': [get_rectangle(list(map(int, gprot.split('-')))) for gprot in ann.gprotein.split()],
        'img_len': MAX_IMG_LEN
    }
    return render(request, 'browser/annotation.html', {'annotation': data})


def browse(request, **kwargs):
    info = {'rab': kwargs['sf']}
    try:
        if kwargs['tax'] == 'all':
            if kwargs['sf'] != 'all':
                annotations = Annotation.objects.all().order_by('taxonomy__name').filter(rab_subfamily=kwargs['sf'])
            else:
                annotations = Annotation.objects.all().order_by('taxonomy__name')
        else:
            annotations = Annotation.objects.filter(taxonomy__taxon=kwargs['tax'])
            if annotations:
                info['taxon_name'] = Taxonomy.objects.get(taxon=kwargs['tax']).name
                if kwargs['sf'] != 'all':
                    annotations = annotations.filter(rab_subfamily=kwargs['sf'])
                annotations = sorted(annotations, key=lambda ann: [int(c) if c.isdigit() else c.lower() for c in
                                                                   re.split('([0-9]+)', ann.rab_subfamily)])
            else:
                graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(NcbiTaxonomy.objects.get(taxon_id=kwargs['tax']))[0])
                leaves = [graph.node[x]['data']['taxon_id'] for x, d in graph.out_degree().items() if d == 0]
                info['taxon_name'] = [graph.node[x]['data']['taxon_name'] for x, d, in graph.in_degree().items() if d == 0][0]
                annotations = Annotation.objects.filter(taxonomy__taxon__in=leaves)
                if kwargs['sf'] != 'all':
                    annotations = annotations.filter(rab_subfamily=kwargs['sf'])

    except Annotation.DoesNotExist:
        raise Http404('No annotations')
    except NcbiTaxonomy.DoesNotExist:
        raise Http404('Taxon does not exist.')

    if len(annotations) == 1:
        return HttpResponseRedirect(reverse('browser:details', kwargs={'protein_id': annotations[0].protein.protein}))

    if 'download' in request.GET:
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}.fasta"'.format(kwargs['tax'])
        cut_seq = lambda s: '\n'.join(s[i: i+80] for i in range(0, len(s), 80))
        sequences = ('>{} {} {}\n{}'.format(ann.protein.protein, ann.taxonomy.name.replace(' ', '_'),
                                            ann.rab_subfamily, cut_seq(ann.protein.seq)) for ann in annotations)
        response.write('\n'.join(sequences))
        return response

    paginator = Paginator(annotations, 25, orphans=5)
    page = request.GET.get('page')
    try:
        annotations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        annotations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        annotations = paginator.page(paginator.num_pages)

    return render(request, 'browser/browser.html', {'annotations': annotations, 'info': info})


def profile(request):
    if request.method == 'POST':
        form_profile = RabProfileForm(request.POST, prefix='profile')
        form_tree = TaxonomyTreeForm(request.POST, prefix='tree')
        if 'show_profile' in request.POST and form_profile.is_valid():
            tx = form_profile.cleaned_data['taxon']
            sf = form_profile.cleaned_data['rab_subfamily']
            return HttpResponseRedirect(reverse('browser:profile_result', kwargs={'tax': tx, 'sf': sf}))
        elif 'show_tree' in request.POST and form_tree.is_valid():
            tx = form_tree.cleaned_data['taxon']
            return HttpResponseRedirect(reverse('browser:taxonomy', kwargs={'tax': tx}))
    else:
        form_profile = RabProfileForm(prefix='profile')
        form_tree = TaxonomyTreeForm(prefix='tree')
    return render(request, 'browser/profile_index.html', {'form': form_profile, 'form_tree': form_tree})


def profile_result(request, **kwargs):
    graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(get_object_or_404(NcbiTaxonomy, taxon_id=kwargs['tax']))[0])
    info = {'taxon_name': [graph.node[x]['data']['taxon_name'] for x, d, in graph.in_degree().items() if d == 0][0],
            'sf': kwargs['sf']}
    tax = int(kwargs['tax'])
    root_node = None
    for node, node_data in graph.nodes_iter(data=True):
        if node_data['data']['taxon_id'] == tax:
            root_node = node
            break
    if not root_node:
        raise Http404('Tree root not found')

    leaves = [graph.node[x]['data']['taxon_id'] for x, d in graph.out_degree().items() if d == 0]
    taxa_with_rab = {x.taxonomy.taxon for x in
                     Annotation.objects.filter(taxonomy__taxon__in=leaves).filter(rab_subfamily=kwargs['sf'])}
    for node in graph.nodes_iter():
        graph.node[node]['has_rab'] = True if graph.node[node]['data']['taxon_id'] in taxa_with_rab else False
        graph.node[node]['browse_rabs_url'] = '/browser/tax/{}/sf/{}'.format(graph.node[node]['data']['taxon_id'],
                                                                             kwargs['sf'])
        graph.node[node]['name'] = graph.node[node]['data']['taxon_name']
        del(graph.node[node]['data'])
    return render(request, 'browser/profile_result.html',
                  {'info': info, 'data': json.dumps(json_graph.tree_data(graph, root_node))})


def taxonomy(request, **kwargs):
    graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(get_object_or_404(NcbiTaxonomy, taxon_id=kwargs['tax']))[0])
    info = {'taxon_name': [graph.node[x]['data']['taxon_name'] for x, d, in graph.in_degree().items() if d == 0][0]}
    root_node = None
    for node, node_data in graph.nodes_iter(data=True):
        if node_data['data']['taxon_id'] == int(kwargs['tax']):
            root_node = node
            break
    if not root_node:
        raise Http404('Tree root not found')

    for node in graph.nodes_iter():
        graph.node[node]['browse_rabs_url'] = '/browser/tax/{}/sf/all'.format(graph.node[node]['data']['taxon_id'])
        graph.node[node]['name'] = graph.node[node]['data']['taxon_name']
        del(graph.node[node]['data'])

    return render(request, 'browser/taxonomy.html',
                  {'info': info, 'data': json.dumps(json_graph.tree_data(graph, root_node))})
