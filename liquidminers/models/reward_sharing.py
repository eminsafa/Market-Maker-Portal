import datetime

from django.db import models
from django.db.models import Sum

from liquidminers.models.investment import Investment
from liquidminers.models.mixins import Week
from liquidminers.models.reward_calculation import RewardCalculation
from liquidminers.models.transaction import Transaction


class RewardSharing(models.Model):
    investment = models.ForeignKey('liquidminers.Investment', on_delete=models.CASCADE, null=True)
    calculation = models.ForeignKey(RewardCalculation, on_delete=models.CASCADE, null=True)
    amount = models.FloatField(null=False, default=0.0)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    paid = models.BooleanField(null=False, default=False)

    @staticmethod
    def get_user_balance(user):
        result = {}
        reward_sharings = RewardSharing.objects.filter(investment__user=user, paid=False)
        for reward_sharing in reward_sharings:
            currency = reward_sharing.investment.pool.currency
            if currency.symbol not in result.keys():
                result[currency.symbol] = reward_sharing.amount
            else:
                result[currency.symbol] += reward_sharing.amount
        return result

    @staticmethod
    def get_user_account_statement(investment):
        result = {'PAID': {}, 'UNPAID': {}}  # we can add 'processing'

        unpaid = RewardSharing.objects.filter(investment=investment, paid=False).aggregate(Sum('amount'))
        if unpaid['amount__sum'] is None:
            unpaid['amount__sum'] = 0
        result['UNPAID'] = unpaid['amount__sum']

        paid = RewardSharing.objects.filter(investment=investment, paid=True).aggregate(Sum('amount'))
        if paid['amount__sum'] is None:
            paid['amount__sum'] = 0
        result['PAID'] = paid['amount__sum']

        return result

    @staticmethod
    def get_reward_sharings(pool, user, limit=100):
        investments = Investment.objects.filter(pool=pool, user=user, status__name='ACTIVE')
        if len(investments) == 0:
            investments = Investment.objects.filter(pool=pool, user=user)
        investment = investments[0]
        start_week = Week.get(pool.start_date).id
        sharings = RewardSharing.objects.filter(investment=investment).order_by('-id')[:10][::-1]

        wallet_address = investment.wallet_address
        for s in sharings:
            s.week_number = s.week.id - start_week + 1
            s.transaction = Transaction.get_status(pool, s.week)
            s.wallet_address = wallet_address[0:4]
            s.duration = s.calculation.duration
        return {'sharings': sharings}
