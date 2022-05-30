from django.db import models


class OrderConfig(models.Model):
    investment = models.ForeignKey('Investment', on_delete=models.CASCADE, null=True)
    balance_allocation = models.FloatField(null=False, default=0)
    bid_spread = models.FloatField(null=False, default=0)
    ask_spread = models.FloatField(null=False, default=0)
    auto_cancel_bid_deviation = models.FloatField(null=False, default=0)
    auto_cancel_ask_deviation = models.FloatField(null=False, default=0)
    queue = models.IntegerField(null=False, default=1)
    buy_filled = models.BooleanField(null=True, default=False)
    sell_filled = models.BooleanField(null=True, default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
