import datetime
from django.db.models import Sum
from django.db.models import Q
from liquidminers.models.investment_shift import InvestmentShift
from liquidminers.models.investment import Investment
from liquidminers.integrations.price_factory import PriceFactory
from liquidminers.models.pool import Pool
from liquidminers.models.order import Order
from django.db import models
from liquidminers.utils import Temp


class Statistic(models.Model):

    name = models.CharField(max_length=32, null=False, default='statistic')
    lookup_id = models.IntegerField(null=True, default=0)
    value = models.FloatField(null=True)
    datetime = models.DateTimeField(auto_now=False, auto_created=False, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @staticmethod
    def get_statistic(name, time_interval=1, lookup_id=None):
        time_diff = datetime.datetime.now() - datetime.timedelta(minutes=time_interval)
        if lookup_id is None:
            statistics = Statistic.objects.filter(name=name, updated_at__gte=time_diff)
        else:
            statistics = Statistic.objects.filter(name=name, updated_at__gte=time_diff, lookup_id=lookup_id)
        if len(statistics) > 0:
            return statistics[0].value
        else:
            return None

    @staticmethod
    def save_statistic(name, value, lookup_id=None, datetime=None):
        if lookup_id is None:
            statistics = Statistic.objects.filter(name=name)
            lookup_id = 0
        else:
            statistics = Statistic.objects.filter(name=name, lookup_id=lookup_id, datetime=datetime)
        if len(statistics) == 1:
            statistics[0].value = value
            statistics[0].save()
        elif len(statistics) > 1:
            statistics.delete()
            Statistic(name=name, value=value, lookup_id=lookup_id, datetime=datetime).save()
        else:
            Statistic(name=name, value=value, lookup_id=lookup_id, datetime=datetime).save()

    @staticmethod
    def get_total_liquidity() -> float:
        statistic = Statistic.get_statistic('total_liquidity', 10)
        if statistic is not None:
            return statistic
        else:
            total_liquidity = 0.0
            pools = Pool.objects.filter(status__name='ACTIVE')
            for p in pools:
                total_liquidity += Statistic.get_liquidity_of_pool(p.id)
            Statistic.save_statistic('total_liquidity', total_liquidity)
        return total_liquidity

    @staticmethod
    def get_liquidity_of_pool(pool_id) -> float:
        statistic = Statistic.get_statistic('pool_liquidity', 10, pool_id)
        if statistic is not None:
            return statistic
        else:
            #liquidity = InvestmentShift.objects.filter(pool_id=pool_id, end__isnull=True).aggregate(Sum('worth_at_run'))
            # @todo make this stable
            #pool_liquidity = round(liquidity['worth_at_run__sum'], 2)
            investments = Investment.objects.filter(status__name='ACTIVE', pool_id=pool_id).aggregate(Sum('total_value'))
            if investments['total_value__sum'] is None:
                investments['total_value__sum'] = 0
            pool_liquidity = round(investments['total_value__sum'], 2)
            Statistic.save_statistic('pool_liquidity', pool_liquidity, pool_id)
            return pool_liquidity

    @staticmethod
    def get_bot_count_of_pool(pool_id) -> int:
        return Investment.objects.filter(status__name='ACTIVE', pool_id=pool_id).count()

    @staticmethod
    def get_bot_count() -> int:
        return Investment.objects.filter(status__name='ACTIVE').count()

    @staticmethod
    def get_day_volume() -> float:
        statistic = Statistic.get_statistic('day_volume', 1)
        if statistic is not None:
            return statistic
        else:
            date_from = datetime.datetime.now() - datetime.timedelta(days=1)
            orders = Order.objects.filter(created_at__gte=date_from).aggregate(Sum('worth'))
            if orders['worth__sum'] is None:
                orders['worth__sum'] = 0
            day_volume = round(orders['worth__sum'], 2)
            Statistic.save_statistic('day_volume', day_volume)
            return day_volume

    @staticmethod
    def get_day_volume_of_pool(pool_id) -> float:
        statistic = Statistic.get_statistic('pool_day_volume', 60, pool_id)
        if statistic is not None:
            return statistic
        else:
            date_from = datetime.datetime.now() - datetime.timedelta(days=1)
            orders = Order.objects.filter(created_at__gte=date_from, pool_id=pool_id).aggregate(Sum('worth'))
            if orders['worth__sum'] is None:
                orders['worth__sum'] = 0
            day_volume = round(orders['worth__sum'], 2)
            Statistic.save_statistic('pool_day_volume', day_volume, pool_id)
            return day_volume

    @staticmethod
    def get_total_reward():
        statistic = Statistic.get_statistic('total_reward', 120)
        if statistic is not None:
            return statistic
        else:
            pools = Pool.objects.filter(status__name='ACTIVE')
            total_reward = 0
            for p in pools:
                worth = PriceFactory.currency_price(p.currency.name, 'USDT')
                total_reward += worth
            Statistic.save_statistic('total_reward', total_reward)
            return total_reward

    @staticmethod
    def get_weekly_yield_avg():
        statistic = Statistic.get_statistic('weekly_yield_avg', 120)
        if statistic is not None:
            return statistic
        else:
            pools = Pool.objects.filter(status__name='ACTIVE')
            total_yield = 0
            for p in pools:
                total_yield += p.weekly_yield
            Statistic.save_statistic('weekly_yield_avg', total_yield)
            return round(total_yield, 2)

    @staticmethod
    def get_weekly_yield_of_pool(pool_id):
        statistic = Statistic.get_statistic('pool_weekly_yield', 120, pool_id)
        if statistic is not None:
            return statistic
        else:
            pools = Pool.objects.filter(id=pool_id)
            total_yield = 0
            for p in pools:
                total_yield += p.weekly_yield
            Statistic.save_statistic('pool_weekly_yield', total_yield, pool_id)
            return round(total_yield, 2)

    @staticmethod
    def get_hourly_yield_avg():
        return round(Statistic.get_weekly_yield_avg() / 7, 2)

    @staticmethod
    def get_chart_data(chart, duration, period, exchange):
        result = []
        day = datetime.date.today()
        for i in range(int(duration/period)):
            if i != 0:
                day = day - datetime.timedelta(days=period)
            date_start = datetime.datetime.combine(day, datetime.time(00, 00, 00))
            date_end = datetime.datetime.combine(day, datetime.time(23, 59, 59))
            item = Temp()
            item.date = day.strftime("%d %B, %Y")
            if chart == 'volume':
                item.value = Statistic.get_volume_for_chart(date_start, date_end, exchange)
            elif chart == 'bot_count':
                item.value = Statistic.get_bot_count_for_chart(date_start, date_end, exchange)
            elif chart == 'liquidity':
                item.value = Statistic.get_liquidity_for_chart(date_start, date_end, exchange)
            result.append(item)
        return reversed(result)

    @staticmethod
    def get_volume_for_chart(date_start, date_end, exchange):
        volume = Order.objects.filter(created_at__gte=date_start, created_at__lte=date_end, investment__pool__exchange=exchange).aggregate(Sum('worth'))
        if volume['worth__sum'] is None:
            volume['worth__sum'] = 0
        return round(volume['worth__sum'], 2)

    @staticmethod
    def get_bot_count_for_chart(date_start, date_end, exchange):
        investments = InvestmentShift.objects.filter(
            Q(stop__isnull=True) | Q(stop__gte=date_start),
            run__lte=date_end,
            investment__status__name='ACTIVE',
            investment__pool__exchange=exchange
        ).distinct('investment')
        return len(investments)

    @staticmethod
    def get_liquidity_for_chart(date_start, date_end, exchange):
        investments = InvestmentShift.objects.filter(
            Q(stop__isnull=True) | Q(stop__gte=date_start),
            run__lte=date_end,
            investment__pool__exchange=exchange
        ).aggregate(Sum('worth_at_run'))

        if investments['worth_at_run__sum'] is None:
            investments['worth_at_run__sum'] = 0
        return round(investments['worth_at_run__sum'], 2)