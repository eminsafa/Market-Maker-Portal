from django.db import models

from liquidminers.models.investment import Investment
from liquidminers.models.mixins import Status
from liquidminers.models.utils import cached

class Order(models.Model):

    # Form Data
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True)
    pool = models.ForeignKey('liquidminers.Pool', on_delete=models.CASCADE, null=True)
    config = models.ForeignKey('liquidminers.OrderConfig', on_delete=models.CASCADE, null=True)
    eid = models.CharField(max_length=32, null=False, default=1)
    amount = models.FloatField(null=True)
    price = models.FloatField(null=True)
    side = models.CharField(max_length=9, default='BUY', null=True)
    worth = models.FloatField(null=False, default=0.0)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    trigger_at = models.DateTimeField(auto_now_add=True, null=True)  # @todo 50 saniye sonrası
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    thread_id = models.CharField(max_length=10, null=False, default='DEFAULT')
    temp = ''
    # reward is in Investment Model
    # pair is in Reward Model that in Investment

    def set_status(self, name):
        if name == 'OPEN':
            name = 'ACTIVE'
        self.status = Status.objects.get(name=name)
        self.save()

    @property
    def amount_rounded(self):
        return round(self.amount, 2)

    @cached
    def price_rounded(self):
        return round(self.price, 4)

    @staticmethod
    def get_all(pool, user):
        investments = Investment.objects.filter(pool=pool, user=user, status__name='ACTIVE')
        if len(investments) > 0:
            investment = investments[0]
        else:
            return {'orders': []}
        pool = investment.pool
        orders = Order.objects.filter(investment=investment).order_by('-id')[:20]
        for o in orders:
            o.reward = pool
            if o.side == 'buy':
                o.side = 'Buy'
                o.side_style = 'success'
            else:
                o.side = 'Sell'
                o.side_style = 'danger'
        return {'orders': orders}

    @staticmethod
    def get_sell_order_count(investment):
        return Order.objects.filter(investment=investment, side='sell').count()

    @staticmethod
    def get_buy_order_count(investment):
        return Order.objects.filter(investment=investment, side='buy').count()
