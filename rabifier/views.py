from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from .forms import RabifyForm
from .tasks import run_rabifier


def result(request, ticket):
    task = run_rabifier.AsyncResult(ticket)
    if task.ready():
        value = task.get()
        return render(request, 'rabifier/result.html', {'result': value, 'ticket': ticket})
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
