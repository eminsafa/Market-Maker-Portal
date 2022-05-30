from django.shortcuts import render


def under_construction(request):
    return render(request, 'pages/under_construction.html')
