from datetime import datetime as dt

from django.db import models
from django.utils.translation import gettext_lazy as _

from liquidminers.integrations.price_factory import PriceFactory
from liquidminers.models.mixins import Week


class InvestmentShift(models.Model):
    investment = models.ForeignKey('Investment', on_delete=models.CASCADE, verbose_name=_('ID on Exchange'))
    week = models.ForeignKey(Week, on_delete=models.PROTECT, verbose_name=_('Week'))
    run = models.DateTimeField(auto_now_add=True, null=True)
    stop = models.DateTimeField(null=True)
    worth_at_run = models.FloatField()  # USDT
    worth_at_end = models.FloatField(null=True)  # USDT
    duration = models.IntegerField(null=True)  # Minutes
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @staticmethod
    def activate(investment):
        active_investment_shift = InvestmentShift.get_active_investment_shift(investment)
        if active_investment_shift is None:
            worth = PriceFactory.get_worth(
                investment.pool.pair.buy_side.symbol,
                investment.coin_amount,
                investment.pool.pair.buy_side.symbol,
                investment.fiat_amount
            )

            investment_shift = InvestmentShift(
                investment=investment,
                week=Week.get(dt.now()),
                worth_at_run=worth
            )
            investment_shift.save()
            return investment_shift
        elif active_investment_shift:
            # @todo LOG
            print('ALREADY HAVE ACTIVE INVESTMENT')
            return active_investment_shift

    @staticmethod
    def deactivate(investment):
        active_investment_shift = InvestmentShift.get_active_investment_shift(investment)
        if active_investment_shift not in [None, False]:
            worth = PriceFactory.get_worth(
                investment.pool.pair.buy_side.symbol,
                investment.coin_amount,
                investment.pool.pair.sell_side.symbol,
                investment.fiat_amount
            )

            active_investment_shift.stop = dt.now()
            active_investment_shift.worth_at_end = worth
            active_investment_shift.duration = int((active_investment_shift.stop - active_investment_shift.run).seconds / 60)
            active_investment_shift.save()
            return True
        elif active_investment_shift is None:
            print('NO')
            return False
        else:
            print('ERROR')
            return False

    @staticmethod
    def get_active_investment_shift(investment):
        investment_shifts = InvestmentShift.objects.filter(investment=investment, stop__isnull=True)
        if len(investment_shifts) == 0:
            return None
        elif len(investment_shifts) == 1:
            return investment_shifts[0]
        else:
            # @todo there is a mistake! LOG it.
            print('!!! IMPORTANT ERROR. UNPROCESSED MULTIPLE INVESTMENT SHIFTS !!!')
            return False

