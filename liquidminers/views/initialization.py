from django.shortcuts import render

from liquidminers.integrations.initializer import initialize
from liquidminers.views.utils import page_details


def initialization(request):
    context = {}
    context = {**context, **page_details('initialization', request.user)}
    initialize()
    return render(request, 'pages/home.html', context)
