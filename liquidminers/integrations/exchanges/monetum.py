import hashlib
import hmac
import json

import requests

from liquidminers.models.log import Log, APILog
from .exchange import Exchange


class Monetum(Exchange):

    _base_url = "https://monetum.exchange/api/v1/"
    _currencies = {1: 'BTC', 2: 'BCH', 3: 'USDT', 4: 'ETH', 5: 'EUR'}

    def __init__(self, user):
        super().__init__(user, 'monetum')

    def param_converter(self, params):
        raw_params = []
        for param in params:
            temp_raw = param+'='+str(params[param])
            raw_params.append(temp_raw)
        return '&'.join(raw_params)

    def get_price(self, pair_eid):
        response = self.api('orderbook/ticker', params={'pair_id': pair_eid}, method='GET', jsoned=True)
        d = response['response']['entities'][0]
        r = Temp()
        r.sell = float(d['bid']['price'])
        r.buy = float(d['ask']['price'])
        r.price = (r.sell+r.buy)/2.0
        return r

    def api(self, endpoint, params={}, method='POST', jsoned=True):
        url = "https://monetum.exchange/api/v1/"+endpoint
        h = hmac.new(self._api_private_key.encode(), self.param_converter(params).encode(), hashlib.sha512)
        sign = h.hexdigest()
        payload = params
        headers = {
            'Sign': sign,
            'Key': self._api_public_key,
            'Authorization': 'Basic bW9uZXR1bTptb25ldHVtYXV0aDE=',
            'Cookie': 'session=eyJpdiI6ImtWS3dpM0thTlFValppaHcrYjdjRFE9PSIsInZhbHVlIjoiNU0vSVFLZUJmZ2o0cGFnOUk0RVJvNjVHRXRTZC9KR0Qya1R2Q1NRYUxHaDkvNHNnR2JnejBCZUNCcGdRNFdnL01VSldkQzhGWDJiT0lZRWdIQ1JxTG9hcWUxV3JJcnNvRHNublVBSzVoMDhGU3hHTkhVQ25ZaHFvSjBNaFRkTTgiLCJtYWMiOiJhMWU5N2E4ZmM2MDlhZjQyZjZhYjlkZDM1ODQ5YzVhNDJiZjA0NDg2ZWRiYjdiZTMyOWM1MzQwMDQ1ZDk0YWI3In0%3D'
        }

        response = requests.request(method, url, headers=headers, data=payload)
        APILog(endpoint=endpoint, params=json.dumps(params), response=response.text).save()
        if jsoned:
            return json.loads(response.text)
            
        else:
            return response.text

    def create_order(self, pair_eid, amount, price, side):
        r_amount = round(amount, 7)
        if r_amount > amount:
            r_amount -= 0.0000001
        params = {
            'pair_id': pair_eid,
            'amount': r_amount,
            'price': price,
            'type': side
        }
        response = self.api('order/new', params)
        if response['errors'] is False:
            print('\u001B[32m'+'<<< ORDER CREATED >>>'+'\u001B[0m')
            try:
                Log(type='info', message='Order Created: '+json.dumps(response)).save()
            except:
                Log(type='error', message='Could not saved log!').save()
            return response['response']['entity']['order_id']
        else:
            print('ERROR')
            Log(type='error', message='CRITICAL: During creating error.').save()
            print(response)
            return 0

    def get_dynamic_price(self, pair_eid, min_spread, implementation_counter=0):
        response = self.api('orderbook/info?pair_id='+str(pair_eid), method='GET')
        min_spread = min_spread / 100
        if min_spread > 0.9:
            min_spread = 0.9

        # SELL = GREATEST ASK
        max_sell = 0
        for ask in response['response']['entities']['asks']:
            if float(ask['price']) > max_sell:
                max_sell = float(ask['price'])

        # BUY = LOWEST BID
        min_buy = 9999999999.0
        for bid in response['response']['entities']['bids']:
            if float(bid['price']) < min_buy:
                min_buy = float(bid['price'])

        buy_price = min_buy * (1.0 - float(min_spread))
        sell_price = max_sell * (1.0 + float(min_spread))

        if buy_price > sell_price:
            Log(type='error', message='Critical Error: Buy Price is greater than sell price! IMPLEMENTATION COUNTER: '+str(implementation_counter)).save()
            new_implementation_counter = implementation_counter + 1
            if new_implementation_counter < 10:
                return self.get_dynamic_price(pair_eid, min_spread, new_implementation_counter)
            else:
                Log(type='error', message='Critical Error: Too much implementation!').save()
                return 0, 9999999999
        else:
            if buy_price == 0 or sell_price == 0:
                return self.get_dynamic_price(pair_eid, min_spread)
            else:
                return buy_price, sell_price

    def get_order_status(self, order):
        response = self.api('order/info', {'order_id': order.eid})
        #try:
        if not response['errors']:
            if 'entity' in response['response']:
                order.temp = 'FILLED'  # Backup Declaration
                print('ORDER STATUS: FILLED')
                return 'FILLED'
            else:
                order.temp = 'NOT_FILLED'  # Backup Declaration
                print('ORDER STATUS: NOT_FILLED')
                return 'NOT_FILLED'
        else:
            if 'errors' in response.keys():
                if 'The selected order id is invalid.' in response['errors']['order_id']:
                    order.temp = 'FILLED'  # Backup Declaration
                    print('ORDER STATUS: FILLED')
                    return 'FILLED'
        #except:
        Log(type='error', message='CRITICAL: During get_order_STATUS.'+str(order.eid)).save()
        print(response)
        print('\u001B[31m' + '>>> STATUS ERROR <<<' + '\u001B[0m')
        print('ORDER STATUS: NOTHING')

    def cancel_order(self, order):
        response = self.api('order/cancel', {'order_id': order.eid})
        if 'response' not in response.keys():
            Log(type='error', message='API ERROR').save()
            return False
        else:
            if response['response'] == 'ok':
                order.set_status('CANCELLED')
                print('\u001B[31m' + '>>> ORDER CANCELLED <<<' + '\u001B[0m')
            else:
                order.set_status('FILLED')
                print('\u001B[31m' + '>>> ORDER FILLED <<<' + '\u001B[0m')
            return True

    def get_user_balance(self):
        result = {}
        try:
            response = self.api('balance/list', jsoned=True)
            if not response['errors']:
                for d in response['response']['entities']:
                    result[d['currency_id']] = float(d['balance'])
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
        return result

    def get_currencies(self):
        response = self.api('currency/list', jsoned=True, method='GET')
        result = {}
        if response['errors']:
            result['error'] = 'Error occurred during API request of currency/list!'
        else:
            result['currencies'] = response['response']['entities']
        return result

    def get_pairs(self):
        response = self.api('pair/list', jsoned=True, method='GET')
        result = {}
        if response['errors']:
            result['error'] = 'Error occurred during API request of pair/list!'
        else:
            result['pairs'] = response['response']['entities']
        return result

    @staticmethod
    def check_credentials(private_key, public_key):
        return False
        url = "https://monetum.exchange/api/v1/balance/list"
        h = hmac.new(private_key.encode(), ''.encode(), hashlib.sha512)
        sign = h.hexdigest()
        payload = {}
        headers = {
            'Sign': sign,
            'Key': public_key,
            'Authorization': 'Basic bW9uZXR1bTptb25ldHVtYXV0aDE=',
            'Cookie': 'session=eyJpdiI6ImtWS3dpM0thTlFValppaHcrYjdjRFE9PSIsInZhbHVlIjoiNU0vSVFLZUJmZ2o0cGFnOUk0RVJvNjVHRXRTZC9KR0Qya1R2Q1NRYUxHaDkvNHNnR2JnejBCZUNCcGdRNFdnL01VSldkQzhGWDJiT0lZRWdIQ1JxTG9hcWUxV3JJcnNvRHNublVBSzVoMDhGU3hHTkhVQ25ZaHFvSjBNaFRkTTgiLCJtYWMiOiJhMWU5N2E4ZmM2MDlhZjQyZjZhYjlkZDM1ODQ5YzVhNDJiZjA0NDg2ZWRiYjdiZTMyOWM1MzQwMDQ1ZDk0YWI3In0%3D'
        }

        response = requests.request('POST', url, headers=headers, data=payload)
        res = json.loads(response.text)
        if 'errors' in res.keys():
            return not res['errors']
        else:
            return False


class Temp:
    pass

