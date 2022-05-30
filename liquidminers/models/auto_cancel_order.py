from django.db import models

from liquidminers.models.mixins import Status

class AutoCancelOrder(models.Model):
    investment = models.ForeignKey('Investment', on_delete=models.CASCADE, null=True)
    pair = models.ForeignKey('Pair', on_delete=models.CASCADE, null=True)  # investment has data
    config = models.ForeignKey('OrderConfig', on_delete=models.CASCADE, null=True)

    bid_price = models.FloatField(null=False, default=0)
    ask_price = models.FloatField(null=False, default=0)
    status = models.ForeignKey('Status', on_delete=models.CASCADE, null=True)
    queue = models.IntegerField(null=False, default=1)

    expire_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @staticmethod
    def get(investment, queue):
        cancel_orders = AutoCancelOrder.objects.filter(investment=investment, queue=queue)

        if len(cancel_orders) == 1:
            return cancel_orders[0]
        elif len(cancel_orders) > 1:
            order = cancel_orders[0]
            for order in range(1, cancel_orders):
                cancel_orders[order].delete()
            return order
        else:
            order = AutoCancelOrder(
                investment=investment,
                pair=investment.pool.pair,
                queue=queue,
                status=Status.objects.get(name='ACTIVE')
            )
            order.save()
            return order
