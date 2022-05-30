import hashlib
import hmac
import json
import time

import requests

from liquidminers.models.log import Log, APILog
from liquidminers.integrations.exchanges.exchange import Exchange
from liquidminers.models.price import Price
from liquidminers.models.pair import Pair


class Gateio(Exchange):

    _base_url = "https://api.gateio.ws/api/v4"
    _currencies = {1: 'BTC', 2: 'BCH', 3: 'USDT', 4: 'ETH', 5: 'EUR'}

    def __init__(self, user):
        super().__init__(user, 'gateio')

    def authenticate(self, method, url, query_string=None, payload_string=None):
        # [{'currency_pair': 'MIMIR_USDT', 'total': 1, 'orders': [{'id': '93162838961', 'text': 'apiv4', 'create_time': '1636814229', 'update_time': '1636814229', 'create_time_ms': 1636814229732, 'update_time_ms': 1636814229732, 'status': 'open', 'currency_pair': 'MIMIR_USDT', 'type': 'limit', 'account': 'spot', 'side': 'sell', 'amount': '46.587638', 'price': '1.21376', 'time_in_force': 'gtc', 'iceberg': '0', 'left': '46.587638', 'fill_price': '0', 'filled_total': '0', 'fee': '0', 'fee_currency': 'USDT', 'point_fee': '0', 'gt_fee': '0', 'gt_discount': False, 'rebated_fee': '0', 'rebated_fee_currency': 'MIMIR'}]}]
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(self._api_private_key.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': self._api_public_key, 'Timestamp': str(t), 'SIGN': sign}

    def api(self, endpoint, params='', method='POST', body=None, jsoned=True):
        try:
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            sign_headers = self.authenticate(method, '/api/v4' + endpoint, params, body)
            if params != '':
                params = '?' + params
            headers.update(sign_headers)
            r = requests.request(method, self._base_url + endpoint + params, headers=headers, data=body)

            try:
                APILog(user=self.user, endpoint=endpoint, params=params, method=method, response=r.text).save()
            except Exception as e:
                Log.on(f"ENDPOINT: {endpoint}, PARAMS: {params}, METHOD: {method}", 'API_LOG_ERROR')

            if jsoned:
                return r.json()

            return r
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            Log.on(f"API=ENDPOINT: {endpoint}, PARAMS: {params}, METHOD: {method} ---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'API_ERROR')
        # SAMPLE ERROR: {'label': 'MISSING_REQUIRED_PARAM', 'message': 'Missing required parameter: order_d_t_o'}
        # SAMPLE ERROR: {'label': 'INVALID_SIGNATURE', 'message': 'Signature mismatch'}
        # SAMPLE ERROR: {'label': 'BALANCE_NOT_ENOUGH', 'message': 'Not enough balance'}

    def get_currencies(self):
        endpoint = '/spot/currencies'
        response = self.api(endpoint, '', 'GET')
        result = []
        for i in response:
            if not i['trade_disabled']:
                result.append(i['currency'])
        return result

    def get_pairs(self):
        endpoint = '/spot/currency_pairs'
        return self.api(endpoint, '', 'GET')

    def get_price(self, pair_eid, cache_check=True):
        endpoint = '/spot/tickers'
        pair = Pair.objects.get(eid=pair_eid)
        if cache_check:
            cached_price = Price.get_cached(pair)
            if cached_price is not None:
                r = Temp()
                r.price = cached_price
                return r

        response = self.api(endpoint, 'currency_pair='+str(pair_eid), 'GET')

        r = Temp()
        r.price = float(response[0]['last'])
        Price.save_price(pair, r.price)
        return r

    def create_order(self, pair_eid, amount, price, side):
        r_amount = round(amount, 7)
        if r_amount > amount:
            r_amount -= 0.0000001

        body = {
            'currency_pair': pair_eid,
            'type': 'limit',
            'account': 'spot',
            'side': side,
            'amount': r_amount,
            'price': price,
        }

        response = self.api('/spot/orders', '', 'POST', json.dumps(body))
        if 'label' in response.keys() and 'message' in response.keys():
            Log.on('OrderCreatingError-1 - Exchange: Gate.io', 'ERROR', self.user)
            Log.on(f"OrderCreatingError-2 --> {json.dumps(response)}", 'ERROR', self.user)
            return False
        else:
            print('\u001B[32m' + '<<< ORDER CREATED >>>' + '\u001B[0m')
            return response['id']

    def get_dynamic_price(self, pair_eid, bid_spread, ask_spread, implementation_counter=0):
        price = self.get_price(pair_eid).price
        buy_price = price * (1.0 - float(bid_spread))
        sell_price = price * (1.0 + float(ask_spread))

        if buy_price > sell_price:
            Log(type='error', message='Critical Error: Buy Price is greater than sell price! IMPLEMENTATION COUNTER: '+str(implementation_counter)).save()
            new_implementation_counter = implementation_counter + 1
            if new_implementation_counter < 10:
                return self.get_dynamic_price(pair_eid, bid_spread, ask_spread, new_implementation_counter)
            else:
                Log(type='error', message='Critical Error: Too much implementation!').save()
                return 0, 9999999999
        else:
            if buy_price == 0 or sell_price == 0:
                return self.get_dynamic_price(pair_eid, bid_spread, ask_spread)
            else:
                return buy_price, sell_price, price

    def update_order_status(self, order):
        status = self.get_order_status(order)
        order.set_status(status)

    def get_order_status(self, order):
        # @todo get if partially filled
        response = self.api('/spot/orders/'+str(order.eid), 'currency_pair='+str(order.investment.pool.pair.eid), 'GET')
        if 'label' in response.keys() and 'message' in response.keys():
            if response['label'] == 'ORDER_NOT_FOUND':
                order.set_status('CANCELLED')
                return 'CANCELLED'
            else:
                Log.on(f'ORDER STATUS GET ERROR OID: {order.id}', 'EXC_ERROR')
                print('>>>>> ERROR OCCURRED WHILE GETTING ORDER STATUS <<<<<')
                return None
        else:
            status = response['status']
            if status == 'closed':
                order.set_status('FILLED')
                return 'FILLED'
            elif status == 'cancelled':
                order.set_status('CANCELLED')
                return 'CANCELLED'
            elif status == 'open':
                return 'OPEN'

    def cancel_order(self, order):
        response = self.api('/spot/orders/'+str(order.eid), 'currency_pair='+str(order.investment.pool.pair.eid), 'DELETE')
        print("Order Cancel Response", response)
        self.update_order_status(order)
        try:
            if 'label' in response.keys() and 'message' in response.keys():
                return False
            else:
                return True
        except Exception as e:
            Log.on(f"CANCEL ORDER ERROR: OID: {order.id} --> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'EXC_ERROR')
            return False

    def get_user_balance(self):
        response = self.api('/spot/accounts', '', 'GET')
        result = {}
        if type(response) != dict:
            for d in response:
                if float(d['available']) > 0:
                    result[d['currency']] = float(d['available'])
        else:
            return False
        return result

    def get_trade_history(self, pair_eid):
        response = self.api('/spot/my_trades', 'currency_pair='+str(pair_eid), 'GET')
        print(response)
        return response

    @staticmethod
    def authenticate_static(method, url, private_key, public_key, query_string=None, payload_string=None):
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(private_key.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': public_key, 'Timestamp': str(t), 'SIGN': sign}

    @staticmethod
    def api_static(endpoint, private_key, public_key, params='', method='POST', body=None, jsoned=True):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        sign_headers = Gateio.authenticate_static(method, '/api/v4' + endpoint, private_key, public_key, params, body)
        if params != '':
            params = '?' + params
        headers.update(sign_headers)
        r = requests.request(method, Gateio._base_url + endpoint + params, headers=headers, data=body)
        if jsoned:
            return r.json()

        return r

    @staticmethod
    def check_credentials(private_key, public_key):
        response = Gateio.api_static('/wallet/total_balance', private_key, public_key, '', 'GET')
        if 'label' in response.keys() and 'message' in response.keys():
            return response['message']
        else:
            return True

    # TESTS

    def get_user_balance_test(self):
        x= self.api('/wallet/total_balance', '', 'GET')
        print(x)
        return x

    def get_trade_history(self, pair_eid):
        return self.api('/spot/my_trades', 'currency_pair='+pair_eid, 'GET')

    def get_open_orders(self):
        return self.api('/spot/open_orders', '', 'GET')

    def cancel_all_orders(self):
        url = '/spot/orders'
        query_param = 'currency_pair=MIMIR_USDT'
        response = self.api(url, query_param, 'DELETE')
        print(response)
        return response

    def cancel_order_by_eid(self, order_eid, pair):
        response = self.api('/spot/orders/'+str(order_eid), 'currency_pair='+str(pair), 'DELETE')
        print("Order Cancel Response", response)
        try:
            if 'label' in response.keys() and 'message' in response.keys():
                return False
            else:
                return True
        except:
            return False


class Temp:
    pass

