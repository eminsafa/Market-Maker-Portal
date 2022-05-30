from liquidminers.views.utils import page_details
from liquidminers.models.statistic import Statistic
from django.shortcuts import render


def stats(request):
    context = {}

    context = {**context, **page_details('Manager', request.user, 'Statistics')}
    #- 1) Volume by days / months - line chart
    #- 2) Token price by days/months - line chart (need to ask)
    #- 3) Number of bots by days / months - line chart
    #- 4) Liquidity by days and months - line chart
    #- 5) Total liquidity by days / months - line chart (only visible by admin)
    duration = 20
    if 'duration' in request.GET.keys():
        try:
            print(request.GET['duration'])
            duration = int(request.GET['duration'])
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            duration = 20

    period = 1
    if 'period' in request.GET.keys():
        try:
            print(request.GET['period'])
            period = int(request.GET['period'])
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            period = 1

    if duration < period:
        duration = period

    context['volume_chart'] = Statistic.get_chart_data('volume', duration, period, 'gateio')
    context['bot_count_chart'] = Statistic.get_chart_data('bot_count', duration, period, 'gateio')
    context['liquidity_chart'] = Statistic.get_chart_data('liquidity', duration, period, 'gateio')

    print(context)

    return render(request, 'pages/manager/home.html', context)
