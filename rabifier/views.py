import json

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from .forms import RabifyForm
from .tasks import run_rabifier


def result(request, ticket):
    task = run_rabifier.AsyncResult(ticket)
    if task.ready():
        value = json.loads(task.get())
        result = {}
        print(value)
        for k, v in value.items():
            l = {
                'is_rab': '&#{}'.format(10004 if v['is_rab'] else 10008),
                'rab_subfamily': v['rab_subfamily'][0] if v['rab_subfamily'][0] else '',
                'rab_subfamily_score': '{:.2f}'.format(v['rab_subfamily'][1]) if v['rab_subfamily'][1] else '',
                'g_protein': ', '.join(v['gprotein_domain_regions']),
                'evalue_rab': '{:.1e}'.format(v['evalue_bh_rabs']) if v['evalue_bh_rabs'] else '',
                'evalue_non_rab': '{:.1e}'.format(v['evalue_bh_non_rabs']) if v['evalue_bh_non_rabs'] else '',
                'rabf': ', '.join('({}, {}-{}, {:.2e})'.format(*x) for x in v['rabf_motifs']),
                'top5': ', '.join('({}, {:.2g})'.format(name, score) for name, score in v['rab_subfamily_top_5'])
                }
            result[v['id']] = l
        return render(request, 'rabifier/result.html', {'result': result, 'ticket': ticket})
    else:
        return render(request, 'rabifier/status.html')


def search(request):
    if request.method == 'POST':
        form = RabifyForm(request.POST, request.FILES)
        if form.is_valid():
            sequences = form.cleaned_data['sequence']
            #if form.cleaned_data['sequence']:
            #    sequences = form.cleaned_data['sequence']
            #elif form.cleaned_data['fastafile']:
            #    sequences = form.cleaned_data['fastafile'].read()
            #else:
            #    sequences = ''
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
