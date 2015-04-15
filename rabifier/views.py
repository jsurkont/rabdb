from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from .forms import RabifyForm
from .tasks import add


def index(request, ticket):
    return HttpResponse("Hello, world. You're at the rabifier index. Ticket numer: {}".format(ticket))


def result(request, ticket):
    task = add.AsyncResult(ticket)
    #print(task, task.ready())
    value = task.get()  # FIXME dangerous, get() is waiting for the process to finish
    return render(request, 'rabifier/result.html', {'result': value, 'ticket': ticket})


def search(request):
    if request.method == 'POST':
        form = RabifyForm(request.POST)
        if form.is_valid():
            a = form.cleaned_data['a']
            b = form.cleaned_data['b']
            job = add.delay(a, b)
            return HttpResponseRedirect(reverse('rabifier:result', kwargs={'ticket': job.id}))
    else:
        form = RabifyForm()

    return render(request, 'rabifier/search.html', {'form': form})
