import json
import csv
import math

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from .forms import RabifyForm
from .tasks import run_rabifier


def result(request, ticket):
    task = run_rabifier.AsyncResult(ticket)
    if task.ready():
        value = json.loads(task.get())
        if 'download' in request.GET:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="rabifier_output.csv"'
            writer = csv.writer(response)
            writer.writerow(['seqid', 'is_rab', 'rab_subfamily', 'rab_subfamily_score', 'g_protein', 'evalue_rab',
                             'evalue_non_rab', 'rabf', 'top5'])
            for k, v in value.items():
                writer.writerow([
                    v['id'],
                    v['is_rab'],
                    v['rab_subfamily'][0] if v['rab_subfamily'][0] else '',
                    v['rab_subfamily'][1] if v['rab_subfamily'][1] else '',
                    '|'.join(v['gdomain_regions']),
                    v['evalue_bh_rabs'] if v['evalue_bh_rabs'] else '',
                    v['evalue_bh_non_rabs'] if v['evalue_bh_non_rabs'] is not None else '',
                    '|'.join('{} {} {} {:.2e}'.format(*x) for x in v['rabf_motifs']),
                    '|'.join('{} {:.2e}'.format(name, score) for name, score in v['rab_subfamily_top_5'])
                ])
            return response

        result = {}
        for k, v in value.items():
            # Helper functions for drawing domains
            MAX_IMG_LEN = 200.0
            seq_len = len(v['sequence']['seq'])
            rescale = lambda x: math.ceil(x * MAX_IMG_LEN / seq_len)
            get_rectangle = lambda x: {'x1': rescale(x[0]), 'width': rescale(x[1] - x[0]), 'range': '{}-{}'.format(*x)}
            l = {
                'is_rab': '&#{}'.format(10004 if v['is_rab'] else 10008),
                'rab_subfamily': '{} ({:.2f})'.format(*v['rab_subfamily']) if v['rab_subfamily'][0] else '---',
                'top_subfamilies': ['{} ({:.2g})'.format(name, score) for name, score in v['rab_subfamily_top_5']][1:],
                'evalue_rab': '{:.1e}'.format(v['evalue_bh_rabs']) if v['evalue_bh_rabs'] is not None else '> threshold',
                'evalue_non_rab': '{:.1e}'.format(v['evalue_bh_non_rabs']) if v['evalue_bh_non_rabs'] is not None else '> threshold',
                'rabf': [get_rectangle(x[1:3]) for x in v['rabf_motifs']],
                'gprotein': [get_rectangle(list(map(int, gprot.split('-')))) for gprot in v['gdomain_regions']],
                'img_len': MAX_IMG_LEN
                }
            result[v['id']] = l
        return render(request, 'rabifier/result.html', {'result': result})
    else:
        return render(request, 'rabifier/status.html')


def search(request):
    if request.method == 'POST':
        form = RabifyForm(request.POST, request.FILES)
        if form.is_valid():
            sequences = form.cleaned_data['sequence']
            job = run_rabifier.delay(
                sequences,
                email=form.cleaned_data['email'],
                evalue_rab=form.cleaned_data['evalue_rab'],
                evalue_motif=form.cleaned_data['evalue_motif'],
                num_motif=form.cleaned_data['num_motif'],
                identity=form.cleaned_data['identity'],
                rab_score=form.cleaned_data['rab_score']
            )
            return HttpResponseRedirect(reverse('rabifier:result', kwargs={'ticket': job.id}))
    else:
        form = RabifyForm()

    return render(request, 'rabifier/search.html', {'form': form})
