from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from liquidminers.forms import CustomUserCreationForm
from liquidminers.models.user import User
from .utils import page_details


def register(request):
    context = {}

    context = {**context, **page_details('home', request.user, 'Home')}

    if request.method == 'POST':
        data = request.POST
        if len(User.objects.filter(email=data['email'])) != 0:
            return {'error': 'This e-mail already registered!'}
        if data['password1'] != data['password2']:
            return {'error': 'Passwords does not match!'}
        try:
            user = User.objects.create_user(data['email'], data['email'], data['password1'])
            user.set_salt()
            user.save()
        except:
            # @todo logger
            # Log(type='ERROR', message='Could not registered due to user creation!').save()
            return {'error': 'User could not registered!'}

        context['success'] = 'User created'
        messages.success(request, "You've registered successfully.")
        return redirect('login')
    else:
        form = CustomUserCreationForm()
        context['form'] = form

    return render(request, 'pages/register.html', context)
