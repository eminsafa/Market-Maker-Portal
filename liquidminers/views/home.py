import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from liquidminers.models.currency import Currency
from liquidminers.models.mixins import Status
from liquidminers.models.mixins import Week
from liquidminers.models.pair import Pair
from liquidminers.models.pool import Pool
from liquidminers.models.statistic import Statistic
from liquidminers.models.weekly_reward import WeeklyReward
from liquidminers.utils import get_secure_num
from liquidminers.views.utils import page_details


@login_required
def home(request):
    context = {}

    context = {**context, **page_details('home', request.user, 'Home')}

    if request.method == 'POST':
        if request.user.is_authenticated:
            context = {**context, **create_pool(request.POST, request.user)}
        else:
            context['error'] = 'User have logged in.'

    context['total_liquidity'] = Statistic.get_total_liquidity()
    context['number_of_bots'] = Statistic.get_bot_count()
    context['day_volume'] = Statistic.get_day_volume()
    context['weekly_yield'] = Statistic.get_weekly_yield_avg()
    context['hourly_yield'] = Statistic.get_hourly_yield_avg()
    context['pools'] = Pool.objects.filter(status__name='ACTIVE')
    context['monetum_pairs'] = Pair.get_by_exchange('monetum')
    context['gateio_pairs'] = Pair.get_by_exchange('gateio')
    context['monetum_currencies'] = Currency.get_by_exchange('monetum')
    context['gateio_currencies'] = Currency.get_by_exchange('gateio')
    Pool.check_start_time()
    context['pools'] = Pool.objects.filter(status__name__in=['ACTIVE', 'PENDING'])

    return render(request, 'pages/home.html', context)


def create_pool(data, user):
    dates = data['end-date'].split('/')
    pair = Pair.objects.get(eid=data['pair'])
    duration_weeks = int(data['campaign_duration']) * 4
    start_date = datetime.date(int(dates[2]), int(dates[1]), int(dates[0]))
    end_date = start_date + datetime.timedelta(weeks=duration_weeks)
    max_spread = min(0.99, max(0.01, abs(get_secure_num(data, 'max_spread')) / 100))
    pool = Pool(
        name=data['name'],
        amount=data['amount'],
        pair=pair,
        exchange=pair.exchange,
        currency=Currency.objects.get(eid=data['currency']),
        status=Status.objects.get(name='PENDING'),
        start_date=start_date,
        end_date=end_date,
        campaign_detail=data['campaign_detail'],
        rules=data['rules'],
        reward_detail=data['reward_detail'],
        max_spread=max_spread,
        user=user
    )
    pool.save()
    total = 0
    first_week = Week.get(pool.start_date).id

    for week in range(duration_weeks):
        input_id = 'week_' + str(week + 1)
        if input_id in data:
            amount = int(data['week_' + str(week + 1)])
            if amount < 0:
                amount = 0
        else:
            amount = 0
        total += int(amount)
        campaign_week_payment = WeeklyReward(amount=amount, week_id=first_week + week)  # @todo week id needed
        campaign_week_payment.save()
        pool.weekly_amount.add(campaign_week_payment)
    pool.amount = total
    pool.save()

    return {'success': 'Reward created successfully.'}
