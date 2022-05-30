
from django.shortcuts import redirect


def page_details(page, user, title=None):
    if title is None:
        title = page.title()

    return {
        'active_page': page,
        'title': title,
        'is_admin': user.is_superuser
    }


def valid_user(function):
    def wrapper(request):
        if 'reward_id' in request.POST.keys():
            if not request.user.is_valid(request.POST['reward_id']):
                return redirect('/settings/')
        return function(request)
    return wrapper

def valid_user_old(function):
    def decorator(function):
        def wrapper(request):
            if request.user.is_valid():
                return function(request)
            return redirect('/settings/')
        return wrapper
    return decorator


def superuser_required(function):
    def wrapper(request):
        if not request.user.is_superuser():
            # @todo message add
            return redirect('/home/')
        return function(request)
    return wrapper


