import json

from django.shortcuts import render, get_list_or_404
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
            if sp != 'all':
                taxon = sp
            else:
                taxon = tx
            url = reverse('browser:browse', kwargs={'tax': taxon})
            sf = form.cleaned_data['rab_subfamily']
            if sf:
                return HttpResponseRedirect('{}?sf={}'.format(url, sf))
            else:
                return HttpResponseRedirect(url)

    else:
        form = RabBrowserForm()

    return render(request, 'browser/index.html', {'form': form})


def details(request, **kwargs):
    p = get_list_or_404(Annotation, protein__protein=kwargs['protein_id'])[0]
    return render(request, 'browser/annotation.html', {'annotation': p})


def browse(request, **kwargs):
    try:
        if kwargs['tax'] == 'all':
            annotations = Annotation.objects.all().order_by('taxonomy__name')
        else:
            annotations = Annotation.objects.filter(taxonomy__taxon=kwargs['tax'])
            if not annotations:
                graph = json_graph.tree_graph(NcbiTaxonomy.dump_bulk(NcbiTaxonomy.objects.get(taxon_id=kwargs['tax']))[0])
                leaves = [graph.node[x]['data']['taxon_id'] for x, d in graph.out_degree().items() if d == 0]
                annotations = Annotation.objects.filter(taxonomy__taxon__in=leaves)
        sf = request.GET.get('sf', None)
        if sf:
            annotations = annotations.filter(rab_subfamily=sf)
    except Annotation.DoesNotExist:
        raise Http404('No annotations')
    except NcbiTaxonomy.DoesNotExist:
        raise Http404('Taxon does not exist.')

    paginator = Paginator(annotations, 20)
    page = request.GET.get('page')
    try:
        annotations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        annotations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        annotations = paginator.page(paginator.num_pages)

    return render(request, 'browser/browser.html', {'annotations': annotations, 'sf': sf})


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
        graph.node[node]['browse_rabs_url'] = '/browser/tax/{}/?sf={}'.format(graph.node[node]['data']['taxon_id'],
                                                                              kwargs['sf'])
        graph.node[node]['name'] = graph.node[node]['data']['taxon_name']
        if graph.out_degree([node])[node] == 0:
            graph.node[node]['is_leaf'] = True
        else:
            graph.node[node]['is_leaf'] = False
        del(graph.node[node]['data'])
    return HttpResponse(json.dumps(json_graph.tree_data(graph, root_node)))
