from liquidminers.utils import singleton
from liquidminers.models.price import Price
from liquidminers.models.pair import Pair
from liquidminers.integrations.exchange_factory import ExchangeFactory

@singleton
class PriceController:

    @staticmethod
    def currency_price(from_currency, to_currency, exchange_name=None) -> float:
        if from_currency in ['USDT', 'USD'] and to_currency in ['USDT', 'USD']:
            return 1.0
        elif from_currency == to_currency:
            return 1.0
        price = Price.get_cached(from_currency + to_currency, 5)
        if price is None:
            if exchange_name is not None:
                pairs = Pair.objects.filter(buy_side__symbol=from_currency, sell_side__symbol=to_currency, exchange=exchange_name)
            else:
                pairs = Pair.objects.filter(buy_side__symbol=from_currency, sell_side__symbol=to_currency)

            if len(pairs) > 0:
                pair = pairs[0]
            else:
                return 0.0

            if exchange_name is not None:
                exchange = ExchangeFactory.get_admin_exchange(exchange_name)
            else:
                exchange = ExchangeFactory.get_admin_exchange(pair.exchange)

            current_price = exchange.get_price(pair.eid, False).price
            Price.save_price(pair, current_price)
            return current_price
        else:
            return price

    @staticmethod
    def get_worth(crypto_side, crypto_amount, fiat_side, fiat_amount) -> float:
        crypto_value = PriceFactory.currency_price(crypto_side, 'USDT') * float(crypto_amount)
        fiat_value = PriceFactory.currency_price(fiat_side, 'USDT') * float(fiat_amount)
        return float(crypto_value + fiat_value)


class PriceFactory:

    @staticmethod
    def currency_price(from_currency, to_currency, exchange_name=None):
        price_controller = PriceController()
        return price_controller.currency_price(from_currency, to_currency, exchange_name)

    @staticmethod
    def get_worth(crypto_side, crypto_amount, fiat_side, fiat_amount):
        price_controller = PriceController()
        return price_controller.get_worth(crypto_side, crypto_amount, fiat_side, fiat_amount)
