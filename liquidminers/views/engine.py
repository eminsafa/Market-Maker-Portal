from liquidminers.integrations.thread_factory import ThreadFactory
from liquidminers.models.log import Log
from django.shortcuts import HttpResponse


def engine(request):
    context = {}
    Log.cleaner()
    ThreadFactory.run()

    return HttpResponse('ENGINE')

