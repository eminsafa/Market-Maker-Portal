from django.db import connections
from liquidminers.models.currency import Currency
from liquidminers.models.pair import Pair
from liquidminers.models.user import User
from liquidminers.models.configuration import Configuration
from liquidminers.models.credential import Credential
from liquidminers.models.mixins import Status, Week
from liquidminers.integrations.exchange_factory import ExchangeFactory


def initialize(force=False):
    initialize_usermeta(User.objects.get(username='admin'))
    return None
    if not force:
        if Configuration.is_initialized():
            print('System already initialized.')
            return False

    Pair.objects.all().delete()
    Currency.objects.all().delete()

    cursor = connections['default'].cursor()

    cursor.execute("ALTER SEQUENCE liquidminers_week_id_seq RESTART WITH 1;")
    cursor.execute("ALTER SEQUENCE liquidminers_status_id_seq RESTART WITH 1;")
    cursor.execute("ALTER SEQUENCE liquidminers_currency_id_seq RESTART WITH 1;")
    cursor.execute("ALTER SEQUENCE liquidminers_pair_id_seq RESTART WITH 1;")

    # FOR SQLITE DB (Change NAME param too)
    # cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='MarketMaker_week';")
    # cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='MarketMaker_status';")
    # cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='MarketMaker_currency';")
    # cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='MarketMaker_pair';")

    # @todo system has to have a admin user. Add it on documentation
    admin_user = User.objects.get(username='admin')

    initialize_usermeta(admin_user)
    initialize_database()

    # Exchange Synchronize

    sync_monetum_exchange(admin_user)
    sync_gateio_exchange(admin_user)

    Configuration.set_initialization_status('yes')


def initialize_usermeta(user):

    credentials = Credential.objects.filter(exchange='monetum')
    if len(credentials) != 0:
        Credential.objects.filter(exchange='monetum', user=user).delete()

    Credential.set_credential(
        user,
        'monetum',
        '93XIXE8SYGUOFSP7P0F7I2MBAS42F3GYCBQ9TEMJOPE1LLNDYCTJNNHHWR7JQAW7',
        '64s9kyblva6yxddz7x31vwlslhxmurm8ngj2okewvepezppza2hpvwtjgwxiaf9h'
    )

    credentials = Credential.objects.filter(exchange='gateio')
    if len(credentials) != 0:
        Credential.objects.filter(exchange='gateio', user=user).delete()

    Credential.set_credential(
        user,
        'gateio',
        '011795083abb4e712d54e9f783823ff0',
        'e8d455739c22c9115e2b62c51c81bb354b4b850b2233b13f0ff6c99a6f56ed1e'
    )


def initialize_database():
    # Status
    statuses = {'ACTIVE': 'success', 'PASSIVE': 'danger', 'PENDING': 'warning', 'CANCELLED': 'danger', 'FILLED': 'light',
                'PROCESSED': 'success', 'PROCESSING': 'warning', 'NOT PROCESSED': 'danger'}

    Status.objects.all().delete()
    for s in statuses:
        Status(name=s, style=statuses[s]).save()

    from datetime import timedelta, datetime
    years = [2021, 2022, 2023]

    Week.objects.all().delete()
    for year in years:
        d = datetime(year, 1, 1)  # January 1st
        d = d + timedelta(days=7 - d.weekday())  # First Monday
        while d.year == year:
            s = d + timedelta(days=6)
            s = s.replace(hour=23, minute=59, second=59, microsecond=999999)
            Week(start=d, end=s).save()
            d += timedelta(days=7)


def sync_monetum_exchange(user):
    exchange = ExchangeFactory.get(user, 'monetum')

    # Currency Sync
    result = exchange.get_currencies()
    if 'error' not in result.keys():
        for c in result['currencies']:
            currency_check = Currency.objects.filter(eid=c['currency_id'], exchange='monetum')
            if len(currency_check) == 0:
                Currency(eid=c['currency_id'], name=c['name'], symbol=c['iso'], icon=c['iso'].lower(), exchange='monetum').save()
    # Pair Sync
    result = exchange.get_pairs()
    if 'error' not in result.keys():
        for p in result['pairs']:
            pair_check = Pair.objects.filter(eid=p['pair_id'], exchange='monetum')
            if len(pair_check) == 0:
                from_currency = Currency.objects.get(eid=p['currency_id_from'], exchange='monetum')
                to_currency = Currency.objects.get(eid=p['currency_id_to'], exchange='monetum')
                pair_name = from_currency.symbol + '/' + to_currency.symbol
                Pair(eid=p['pair_id'], name=pair_name, buy_side=from_currency, sell_side=to_currency, exchange='monetum').save()


def sync_gateio_exchange(user):
    exchange = ExchangeFactory.get(user, 'gateio')

    # Currency Sync
    desired_currencies = ['MIMIR', 'USDT', 'USD', 'BNB', 'XRP', 'ETH', 'LTC', 'GT', 'BTC', 'EUR']
    currencies = exchange.get_currencies()
    print(currencies)
    for c in currencies:
        if c in desired_currencies:
            currency_check = Currency.objects.filter(eid=c, exchange='gateio')
            if len(currency_check) == 0:
                Currency(eid=c, name=c, symbol=c, icon=c.lower(), exchange='gateio').save()

    # Pair Sync
    desired_pairs = ['MIMIR_USDT', 'BNB_USDT', 'XRP_USDT', 'MIMIR_ETH', 'LTC_USDT', 'GT_USDT', 'BTC_USDT', 'ETH_USDT']  # We will use only these pairs.
    pairs = exchange.get_pairs()
    for p in pairs:
        if p['id'] in desired_pairs:
            pair_check = Pair.objects.filter(eid=p['id'], exchange='gateio')
            if len(pair_check) == 0:
                a = p['base']
                try:
                    from_currency = Currency.objects.get(eid=p['base'], exchange='gateio')
                    to_currency = Currency.objects.get(eid=p['quote'], exchange='gateio')
                except:
                    print(p['base'] + " or " + p['quote'] + " does not exist!")
                else:
                    pair_name = from_currency.symbol + '/' + to_currency.symbol
                    Pair(eid=p['id'], name=pair_name, buy_side=from_currency, sell_side=to_currency, exchange='gateio').save()
