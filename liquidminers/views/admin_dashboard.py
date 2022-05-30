import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.investment import Investment
from liquidminers.models.order import Order
from liquidminers.models.reward_sharing import RewardSharing
from liquidminers.models.user import User
from liquidminers.utils import Temp
from liquidminers.views.utils import page_details


@login_required
def admin_dashboard(request):
    context = {}

    context = {**context, **page_details('admin_dashboard', request.user, 'Admin Dashboard')}
    context = {**context, **pool_table_admin()}

    exchange = ExchangeFactory.get(request.user, 'monetum')
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    context['data'] = []
    counter = 0
    context['total_investment'] = round(Investment.get_total_all(), 2)
    context['investments'] = []
    now = datetime.datetime.now()
    c_year = now.year
    c_month = now.month
    for i in range(6):
        a = Temp()
        investments = Investment.objects.filter(created_at__year=c_year, created_at__month=c_month)
        total = 0
        for n in investments:
            total += n.total_value
        a.total = total
        a.month = months[c_month - 1]
        if c_month == 1:
            c_month = 13
            c_year -= 1
        c_month -= 1
        context['investments'].append(a)
    context['investments'].reverse()
    users = User.objects.all()
    context['customers'] = len(users)

    rewards = RewardSharing.objects.all()
    rew_total = 0
    for i in rewards:
        rew_total += i.amount
    context['reward_total'] = rew_total

    context['order_count'] = Order.objects.filter(status__name='FILLED').count()
    return render(request, 'pages/admin_dashboard.html', context)


def pool_table_admin():
    # Filters: Pair / Exchange / Month - Week
    # Week | Month |  User Id | Exchange User ID | Pool Name | share of the pool | Nr sellOrders | Nr buyOrders | Pool rewards | Reward address
    reward_sharings = RewardSharing.objects.all()
    data = []
    for rs in reward_sharings:
        temp = Temp()
        temp.week = rs.week.id
        temp.month = rs.week.start.strftime("%B")
        temp.user_id = rs.investment.user.id
        temp.exchange_user_id = 0  # @todo implement
        temp.pool_name = rs.investment.pool.name
        temp.share_of_pool = rs.investment.pool.get_share_in_pool(rs.investment.fiat_amount)  # @todo make it stable
        temp.sell_order_count = Order.get_sell_order_count(rs.investment)
        temp.buy_order_count = Order.get_buy_order_count(rs.investment)
        temp.reward_amount = rs.amount
        temp.reward_currency = rs.investment.pool.currency.symbol
        temp.wallet_address = rs.investment.wallet_address
        data.append(temp)
    return {"pool_admin_table_data": data}
