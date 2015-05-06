import json

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404, HttpResponse
from networkx.readwrite import json_graph

from .models import Annotation, NcbiTaxonomy
from .forms import RabBrowserForm, RabProfileForm


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

    data = {
        'species': ann.taxonomy.name,
        'protein': ann.protein.protein,
        'gene': ann.protein.gene,
        'rab_subfamily': ann.rab_subfamily,
        'rab_subfamily_score': '{:.2f}'.format(ann.rab_subfamily_score),
        'gprotein': ann.gprotein,
        'evalue_rab': '{:.1e}'.format(10**ann.log10_evalue_rab),
        'evalue_non_rab': '{:.1e}'.format(10**ann.log10_evalue_nonrab) if ann.log10_evalue_nonrab else '>1e-10',
        'rabf': ', '.join('({}, {}-{}, {})'.format(*x.split()) for x in ann.rabf.split('|')),
        'top5': ', '.join('({}, {:.2g})'.format(*(float(y) if y[0].isdigit() else y for y in x.split()))
                          for x in ann.rab_subfamily_top5.split('|')),
        'sequence': ann.protein.seq
    }
    return render(request, 'browser/annotation.html', {'annotation': data})


def browse(request, **kwargs):
    info = {}
    try:
        if kwargs['tax'] == 'all':
            annotations = Annotation.objects.all().order_by('taxonomy__name')
        else:
            annotations = Annotation.objects.filter(taxonomy__taxon=kwargs['tax'])
            if annotations:
                info['taxon_name'] = annotations[0].taxonomy.name
            else:
                graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(NcbiTaxonomy.objects.get(taxon_id=kwargs['tax']))[0])
                leaves = [graph.node[x]['data']['taxon_id'] for x, d in graph.out_degree().items() if d == 0]
                info['taxon_name'] = [graph.node[x]['data']['taxon_name'] for x, d, in graph.in_degree().items() if d == 0][0]
                annotations = Annotation.objects.filter(taxonomy__taxon__in=leaves)

        sf = kwargs['sf']
        if sf != 'all':
            annotations = annotations.filter(rab_subfamily=sf)
    except Annotation.DoesNotExist:
        raise Http404('No annotations')
    except NcbiTaxonomy.DoesNotExist:
        raise Http404('Taxon does not exist.')

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
        form = RabProfileForm(request.POST)
        if form.is_valid():
            tx = form.cleaned_data['taxon']
            sf = form.cleaned_data['rab_subfamily']
            return HttpResponseRedirect(reverse('browser:profile_result', kwargs={'tax': tx, 'sf': sf}))
    else:
        form = RabProfileForm()
    return render(request, 'browser/profile_index.html', {'form': form})


def profile_result(request, **kwargs):
    graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(NcbiTaxonomy.objects.get(taxon_id=kwargs['tax']))[0])
    leaves = [graph.node[x]['data']['taxon_id'] for x, d in graph.out_degree().items() if d == 0]
    profile_info = {'leaf_number': len(leaves)}
    return render(request, 'browser/profile_result.html', {'profile_info': json.dumps(profile_info)})


def profile_data(request, **kwargs):
    graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(NcbiTaxonomy.objects.get(taxon_id=kwargs['tax']))[0])
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
        if graph.out_degree([node])[node] == 0:
            graph.node[node]['is_leaf'] = True
        else:
            graph.node[node]['is_leaf'] = False
        del(graph.node[node]['data'])
    return HttpResponse(json.dumps(json_graph.tree_data(graph, root_node)))
