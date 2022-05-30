from django.shortcuts import HttpResponse

from liquidminers.models.credential import Credential
from liquidminers.integrations.threads.auto_cancel_controller import AutoCancelController
from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.integrations.threads.statistic_controller import StatisticController
from liquidminers.models.order import Order

def test(request):
    StatisticController.daily()

    return HttpResponse('OK')

