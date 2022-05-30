import datetime

from django.db import models
from django.db.models import Q
from django.db.models import Sum

from liquidminers.integrations.price_factory import PriceFactory
from liquidminers.models.currency import Currency
from liquidminers.models.investment import Investment
from liquidminers.models.investment_shift import InvestmentShift
from liquidminers.models.mixins import Status, Week
from liquidminers.models.order import Order
from liquidminers.models.pair import Pair
from liquidminers.models.reward_sharing import RewardSharing
from liquidminers.models.utils import lazy_property, date_formatter
from liquidminers.models.weekly_reward import WeeklyReward


class Pool(models.Model):
    # Form Data
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=32, null=True)
    amount = models.FloatField(null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=False, default=datetime.date.today)
    end_date = models.DateField(null=False, default=datetime.date.today)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    exchange = models.CharField(max_length=32, null=True, default='monetum')
    campaign_detail = models.TextField(max_length=150, null=True)
    rules = models.TextField(max_length=50, null=True)
    reward_detail = models.TextField(max_length=50, null=True)
    max_spread = models.FloatField(null=True, default=0.01)
    weekly_amount = models.ManyToManyField(WeeklyReward)
    user = models.ForeignKey('liquidminers.user', on_delete=models.CASCADE, null=True)

    @lazy_property
    def campaign_duration(self):
        return len(self.weekly_amount.all())

    @lazy_property
    def bot_count(self):
        bot_count = Investment.objects.filter(status__name='ACTIVE', pool=self).count()
        if isinstance(bot_count, int):
            return bot_count
        return 0

    @lazy_property
    def close_date(self):
        return date_formatter(self.end_date)

    @lazy_property
    def close_time(self):
        return date_formatter(self.end_date)

    @lazy_property
    def liquidity(self):
        investments = Investment.objects.filter(status__name='ACTIVE', pool_id=self.id).aggregate(Sum('total_value'))
        if investments['total_value__sum'] is None:
            investments['total_value__sum'] = 0
        pool_liquidity = round(investments['total_value__sum'], 2)
        return pool_liquidity

    @lazy_property
    def monthly_yield(self):
        return 0

    @lazy_property
    def weekly_yield(self) -> float:
        # (Weekly Rewards_DollarValue / Total Liquidity ) * 100
        liquidity = self.get_liquidity()
        if liquidity == 0.0:
            return 0.0
        else:
            dt = datetime.datetime.now()
            if len(self.weekly_amount.all()) > 0:
                weekly_reward = self.weekly_amount.get(week=Week.get(dt)).amount
                weekly_reward_value = weekly_reward * PriceFactory.currency_price(self.pair.buy_side.symbol, self.pair.sell_side.symbol, self.exchange)
                return round((weekly_reward_value / liquidity) * 100.0, 2)
            else:
                return 0.0

    @lazy_property
    def hourly_yield(self):
        return round(self.weekly_yield / 7, 2)

    def get_liquidity(self) -> float:
        liquidity = InvestmentShift.objects.filter(investment__pool=self, stop__isnull=True).aggregate(Sum('worth_at_run'))
        if liquidity['worth_at_run__sum'] is None:
            liquidity['worth_at_run__sum'] = 0
        return round(liquidity['worth_at_run__sum'], 2)

    def get_current_week(self, safe=True):
        current_week = Week.get(datetime.datetime.now())
        if safe:
            if datetime.date.today().__gt__(self.end_date):
                week = Week.get(self.end_date)
        week = current_week.id - Week.get(self.start_date).id + 1
        if week < 1:
            # @todo week
            # Log(type='error', message='Week calculation error. MM.get_week_of_reward').save()
            week = 1
        return week

    def get_reward_sharings_total(self):
        # @todo make it short
        reward_total = 0
        start_week = Week.get(datetime.datetime.now()).id - 1
        reward_sharings = RewardSharing.objects.filter(week_id__gte=start_week)
        for r in reward_sharings:
            reward_total += r.amount  # @todo convert to usd if not usd.
        return reward_total

    # @todo check if it returns worth as USDT
    def get_share_in_pool(self, investment_worth):
        total_liquidity = self.liquidity
        if self.liquidity < 1:
            if investment_worth < 1:
                return 100
            else:
                total_liquidity = investment_worth
        else:
            total_liquidity += investment_worth
        return round(investment_worth / total_liquidity * 100, 3)

    def get_investments_total(self):
        investments = Investment.objects.filter(pool=self).aggregate(Sum('total_value'))
        if investments['total_value__sum'] is None:
            investments['total_value__sum'] = 0
        return float(investments['total_value__sum'])

    def get_weeks(self):
        start_week = Week.get(self.start_date).id
        end_week = Week.get(self.end_date).id
        weeks = []
        for w in range(start_week, end_week + 1):
            weeks.append(w)
        return weeks

    #  For total spent time
    def get_spent_time(self, week):
        week_start = week.start.timestamp()
        week_end = week.end.timestamp()
        investment_shifts = InvestmentShift.objects.filter(Q(stop__isnull=True) | Q(stop__gte=week_start), investment__pool=self, run__lte=week_end)
        total = 0
        for i in investment_shifts:
            if week_start > i.run.timestamp():
                relative_time = week_start
            else:
                relative_time = i.run.timestamp()
            total += week_end - relative_time
        return float(round(total / 1000.0, 2))

    def get_user_spent_time(self, week, user):
        week_start = week.start.timestamp()
        week_end = week.end.timestamp()
        investment_shifts = InvestmentShift.objects.filter(Q(stop__isnull=True) | Q(stop__gte=week_start), investment__pool=self, investment__user=user, run__lte=week_end)
        total = 0
        for i in investment_shifts:
            if week_start > i.run.timestamp():
                relative_time = week_start
            else:
                relative_time = i.run.timestamp()
            total += week_end - relative_time
        return float(round(total / 1000.0, 2))

    def get_order_count(self):
        investments = Investment.objects.filter(pool=self)
        number_of_orders = 0
        for i in investments:
            number_of_orders += len(Order.objects.filter(investment=i))
        return number_of_orders

    def is_user_invested(self, user):
        investments = Investment.objects.filter(user=user, pool=self, status__name='ACTIVE')
        if len(investments) > 0:
            return True
        else:
            return False

    @staticmethod
    def check_start_time():
        pools = Pool.objects.filter(status__name='PENDING', start_date__lte=datetime.date.today())
        for p in pools:
            p.status = Status.objects.get(name='ACTIVE')
            p.save()
