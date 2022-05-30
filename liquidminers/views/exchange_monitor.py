import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.user import User
from liquidminers.utils import Temp


@login_required
def exchange_monitor(request):
    if 'secret_user_id' in request.GET.keys():
        user = User.objects.get(id=int(request.GET['secret_user_id']))
        suid = '&secret_user_id=' + str(request.GET['secret_user_id'])
    else:
        user = request.user
        suid = ''
    exchange = ExchangeFactory.get(user, 'gateio')

    orders = exchange.get_open_orders()
    order_list = []
    for cp in orders:
        for order in cp['orders']:
            o = Temp()
            o.id = order['id']
            o.created_at = datetime.datetime.fromtimestamp(int(order['create_time']))
            o.status = order['status']
            o.side = order['side']
            o.amount = order['amount']
            o.pair = order['currency_pair']
            o.price = order['price']
            o.suid = suid
            order_list.append(o)

    balances = exchange.get_user_balance()
    balance_list = []
    for balance in balances:
        b = Temp()
        b.pair = balance
        b.amount = balances[balance]
        balance_list.append(b)

    trade_list = []
    trade_history = exchange.get_trade_history('XRP_USDT')
    for th in trade_history:
        t = Temp()
        t.order_id = th['order_id']
        t.side = th['side']
        t.amount = th['amount']
        t.price = th['price']
        t.created_at = datetime.datetime.fromtimestamp(int(th['create_time']))
        t.fee = th['fee']
        t.fee_currency = th['fee_currency']
        trade_list.append(t)

    context = {
        'orders': order_list,
        'balance': balance_list,
        'history': trade_list
    }

    return render(request, 'pages/exchange_monitor.html', context)


def cancel_admin_order(request):
    if 'secret_user_id' in request.GET.keys():
        user = User.objects.get(id=int(request.GET['secret_user_id']))
    else:
        user = request.user
    if 'order_id' in request.GET.keys() and 'pair' in request.GET.keys():
        exchange = ExchangeFactory.get(user, 'gateio')
        exchange.cancel_order_by_eid(request.GET['order_id'], request.GET['pair'])
    return redirect('exchange_monitor')


def create_admin_order(request):
    if 'secret_user_id' in request.GET.keys():
        user = User.objects.get(id=int(request.GET['secret_user_id']))
    else:
        user = request.user
    if 'side' in request.GET.keys() and 'amount' in request.GET.keys():
        exchange = ExchangeFactory.get(user, 'gateio')
        exchange.create_order(
            request.GET['pair'],
            float(request.GET['amount']),
            float(request.GET['price']),
            request.GET['side'])
    return redirect('exchange_monitor')
