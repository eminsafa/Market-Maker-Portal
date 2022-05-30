from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from liquidminers.forms import CustomPasswordChangeForm
from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.configuration import Configuration
from liquidminers.models.credential import Credential
from liquidminers.views.utils import page_details


@login_required
def settings(request):
    context = {}

    context = {**context, **page_details('settings', request.user, 'Settings')}

    if context['is_admin']:
        if 'trade-engine' in request.GET:
            Configuration.set_trade_engine_status(request.GET['trade-engine'])
        trade_engine_status = Configuration.is_trade_engine_active()
        if trade_engine_status:
            context['trade_engine_status'] = 'Active'
            context['trade_engine_status_style'] = 'success'
            context['trade_engine_btn'] = 'on'
        else:
            context['trade_engine_status'] = 'Passive'
            context['trade_engine_status_style'] = 'warning'
            context['trade_engine_btn'] = 'off'

    form = CustomPasswordChangeForm(request.user)
    context['form'] = form

    if request.method == 'POST':
        # API UPDATE
        if 'exchange-name' in request.POST:
            exchange_name = request.POST['exchange-name']
            credential_check = ExchangeFactory.check_credentials(exchange_name, request.POST['api_private_key'], request.POST['api_public_key'])
            if credential_check is True:
                ExchangeFactory.delete(request.user, exchange_name)
                Credential.set_credential(request.user, exchange_name, request.POST['api_public_key'], request.POST['api_private_key'])
                context['success'] = 'API Credential added successfully. Please check your information below.'
            else:
                if credential_check is not False:
                    context['error'] = 'Error! ' + credential_check
                else:
                    context['error'] = 'API Credential not added! Cannot connect exchange. Please check your information below.'
        elif 'old_password' in request.POST:
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                context['success'] = 'Password updated successfully!'
            else:
                context['error'] = 'Password cannot changed!'

    context = {**context, **get_all_exchange_credentials(request.user)}
    return render(request, 'pages/settings.html', context)


def set_trade_engine_status(status_text):
    if status_text == 'on':
        print('ACTIVE')
        # @todo change this
        # self._run_thread = True
    elif status_text == 'off':
        print('PASSIVE')
        # @todo change this
        # self._run_thread = False


def get_all_exchange_credentials(user):
    exchanges = ExchangeFactory.get_exchange_list()
    result = {}
    for exchange in exchanges:
        if ExchangeFactory.get(user, exchange) is not False:
            credential = Credential.objects.get(user=user, exchange=exchange)
            result[exchange + '_public_key'] = credential.public_key_decrypted
            result[exchange + '_private_key'] = credential.private_key
    return result
