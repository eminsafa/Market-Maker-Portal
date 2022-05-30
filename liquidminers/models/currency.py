import json

from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):

    eid = models.CharField(max_length=16, null=False, default=1, verbose_name=_('ID on Exchange'))
    symbol = models.CharField(max_length=16, verbose_name=_('Symbol'))
    name = models.CharField(max_length=32, verbose_name=_('Name'))
    icon = models.CharField(max_length=16, null=True, default='none', verbose_name=_('Icon'))
    exchange = models.CharField(max_length=16, null=True, verbose_name=_('Exchange Name'))

    @staticmethod
    def get_by_exchange(exchange_name, as_string=True):
        currencies = Currency.objects.filter(exchange=exchange_name)
        result = {}

        for currency in currencies:
            result[currency.eid] = currency.name

        if as_string:
            return json.dumps(result)
        else:
            return result
