import datetime

from django.db import models

from liquidminers.models.pair import Pair


class Price(models.Model):
    PRIME = 'usdt'
    PRIMES = ['usd', 'btc', 'eur', 'eth']

    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, null=True)
    pair_text = models.CharField(max_length=32, null=True)
    price = models.FloatField(null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @staticmethod
    def get_worth():
        pass

    @staticmethod
    def get_cached(pair_text, time_interval=1, strict=False):
        # TIME INTERVAL in MINUTES
        time_diff = datetime.datetime.now() - datetime.timedelta(minutes=time_interval)
        prices = Price.objects.filter(pair_text=pair_text, updated_at__gte=time_diff)
        if len(prices) > 0:
            return prices[0].price
        elif not strict:
            prices = Price.objects.filter(pair_text=pair_text, updated_at__gte=time_diff)
            if len(prices) > 0:
                return prices[0].price
            else:
                return None
        else:
            return None

    @staticmethod
    def save_price(pair, price):
        prices = Price.objects.filter(pair=pair)
        if len(prices) == 1:
            prices[0].price = price
            prices[0].save()
        elif len(prices) > 1:
            price = prices[0].price
            prices.delete()
            Price(pair=pair, pair_text=pair.text, price=price).save()
        else:
            Price(pair=pair, pair_text=pair.text, price=price).save()

    @staticmethod
    def currency_converter(from_currency, to_currency):
        # USDT -> EUR
        # ETH -> EUR
        # ETH -> USDT (TWO WAY)
        # P1P91IPI9SH1JZSI
        # {'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency.'}
        #crypto_primes = ["USDT", "ETH", "BTC"]
        #from_currency = from_currency.upper()
        #to_currency = to_currency.upper()
        #if from_currency == "EUR" and to_currency in crypto_primes:
        #    return 1 / Price.currency_price(to_currency, from_currency)
        #elif from_currency == "USD" and to_currency in crypto_primes:
        #    return 1 / Price.currency_price(to_currency, from_currency)
        #else:
        #    return Price.currency_price(from_currency, to_currency)
        pass
