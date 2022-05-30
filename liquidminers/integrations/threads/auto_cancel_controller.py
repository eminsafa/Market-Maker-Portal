from django.db.models import Q

from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.auto_cancel_order import AutoCancelOrder
from liquidminers.models.investment_log import InvestmentLog
from liquidminers.models.log import Log
from liquidminers.models.mixins import Status
from liquidminers.models.order import Order
from liquidminers.models.pair import Pair
from liquidminers.utils import singleton


@singleton
class AutoCancelControllerAbstract:

    def __init__(self):
        self._cache_price_duration = 20  # in seconds

    def main(self):
        pairs = AutoCancelOrder.objects.filter(status__name='ACTIVE').values('pair').distinct()

        for pair_id in pairs:
            pair = Pair.objects.get(id=pair_id['pair'])
            admin_exchange = ExchangeFactory.get_admin_exchange(pair.exchange)
            _, _, price = admin_exchange.get_dynamic_price(pair.eid, 0, 0)
            auto_cancel_orders = AutoCancelOrder.objects.filter(Q(ask_price__lte=price) | Q(bid_price__gte=price), pair=pair, status__name='ACTIVE', investment__status__name='ACTIVE')
            for auto_cancel_order in auto_cancel_orders:
                exchange = ExchangeFactory.get(auto_cancel_order.investment.user, auto_cancel_order.investment.pool.exchange)
                if auto_cancel_order.investment.stop_bot_active:
                    auto_cancel_order.investment.status = Status.objects.get(name='PASSIVE')
                    for order_config in auto_cancel_order.investment.order_config.all():
                        buy_orders = Order.objects.filter(status__name='ACTIVE', config=order_config, side='buy')
                        for bo in buy_orders:
                            exchange.cancel_order(bo)
                        Log.on(f"Auto Cancel Intervened. All orders cancelled.", 'INFO')
                        InvestmentLog.log(auto_cancel_order.investment, 'Auto Cancel', f"Auto Cancel Triggered. All orders cancelled.")
                        sell_orders = Order.objects.filter(status__name='ACTIVE', config=order_config, side='sell')
                        for so in sell_orders:
                            exchange.cancel_order(so)
                        Log.on(f"Auto Cancel Intervened. All orders cancelled.", 'INFO')
                        InvestmentLog.log(auto_cancel_order.investment, 'Auto Cancel', f"Auto Cancel Triggered. All orders cancelled.")
                else:
                    buy_orders = Order.objects.filter(status__name='ACTIVE', config=auto_cancel_order.config, side='buy')
                    for bo in buy_orders:
                        exchange.cancel_order(bo)
                        Log.on(f"Auto Cancel Intervened. Order ID# {bo.id}", 'INFO')
                        InvestmentLog.log(auto_cancel_order.investment, 'Auto Cancel', f"Auto Cancel Triggered. Order #{bo.id} cancelled.")
                    sell_orders = Order.objects.filter(status__name='ACTIVE', config=auto_cancel_order.config, side='sell')
                    for so in sell_orders:
                        exchange.cancel_order(so)
                        Log.on(f"Auto Cancel Intervened. Order ID# {so.id}", 'INFO')
                        InvestmentLog.log(auto_cancel_order.investment, 'Auto Cancel', f"Auto Cancel Triggered. Order #{so.id} cancelled.")


class AutoCancelController:

    @staticmethod
    def main():
        try:
            auto_cancel_controller = AutoCancelControllerAbstract()
            auto_cancel_controller.main()
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            Log.on(f"AUTO CANCEL -> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", "AC_ERROR")
