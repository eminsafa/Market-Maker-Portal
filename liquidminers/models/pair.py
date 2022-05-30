import json

from django.db import models
from django.utils.translation import gettext_lazy as _

from liquidminers.models.currency import Currency


class Pair(models.Model):

    eid = models.CharField(max_length=16, null=False, default=1, verbose_name=_('ID on Exchange'))
    name = models.CharField(max_length=32, null=False, default='<PAIR>', verbose_name=_('Name'))
    buy_side = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, related_name='buy_side', verbose_name=_('Buy Side'))
    sell_side = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, related_name='sell_side', verbose_name=_('Sell Side'))
    exchange = models.CharField(max_length=16, null=True, verbose_name=_('Exchange Name'))

    @property
    def text(self):
        return self.buy_side.symbol + self.sell_side.symbol

    @staticmethod
    def get_by_exchange(exchange_name, as_string=True):
        pairs = Pair.objects.filter(exchange=exchange_name)
        result = {}

        for pair in pairs:
            result[pair.eid] = pair.name

        if as_string:
            return json.dumps(result)
        else:
            return result
