from django.shortcuts import render, get_list_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404
from networkx.readwrite import json_graph

from .models import Annotation, NcbiTaxonomy
from .forms import RabBrowserForm


def index(request):
    if request.method == 'POST':
        form = RabBrowserForm(request.POST, request.FILES)
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
