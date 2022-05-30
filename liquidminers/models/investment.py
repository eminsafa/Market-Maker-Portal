from django.db import models

from liquidminers.models.investment_shift import InvestmentShift
from liquidminers.models.mixins import Status
from liquidminers.models.user import User
from liquidminers.models.order_config import OrderConfig
from liquidminers.models.auto_cancel_order import AutoCancelOrder


class Investment(models.Model):
    # Form Data
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pool = models.ForeignKey('Pool', on_delete=models.CASCADE, null=True)
    wallet_address = models.TextField(null=False, default=0)
    coin_amount = models.FloatField(null=False, default=0)  # Balance 1 / Base Balance Allocation
    fiat_amount = models.FloatField(null=True, default=0)  # Balance 2 / Quote Balance Allocation

    # Configuration
    order_pair_count = models.IntegerField(null=False, default=1)
    auto_cancel_active = models.BooleanField(null=False, default=False)
    stop_bot_active = models.BooleanField(null=False, default=False)
    renew_time = models.IntegerField(null=False, default=60)
    renew_unfilled_orders = models.BooleanField(null=False, default=True)
    order_config = models.ManyToManyField(OrderConfig, related_name='order_config')
    auto_cancel_order = models.ManyToManyField(AutoCancelOrder, related_name='auto_cancel_order')
    param_update_check = models.BooleanField(null=True, default=False)  # updated investment

    # Trade Engine Parameters
    total_value = models.FloatField(null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    lock_at = models.DateTimeField(auto_now=True, null=True)
    thread_id = models.CharField(max_length=10, null=False, default='RELEASED')
    trigger_at = models.DateTimeField(auto_now_add=True, null=True)

    # pair is in Reward Model

    @staticmethod
    def get_total_all():
        total = 0.0
        investments = Investment.objects.all()
        for i in investments:
            total += i.total_value
        return float(total)

    def get_total_earnings(self):
        reward_sharings = None  # @todo RewardSharing.objects.filter(investment=self)
        total = 0.0
        for r in reward_sharings:
            total += r.amount
        return float(total)

    def release(self):
        self.thread_id = "RELEASED"
        self.save()
