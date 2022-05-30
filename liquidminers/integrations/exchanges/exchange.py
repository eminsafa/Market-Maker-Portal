from liquidminers.models.credential import Credential


class Exchange:

    _currencies = {1: 'BTC', 2: 'BCH', 3: 'USDT', 4: 'ETH', 5: 'EUR'}

    def __init__(self, user, exchange_name):
        self.user = user

        try:
            credential = Credential.objects.get(user=user, exchange=exchange_name)
            self._api_private_key = credential.private_key_decrypted
            self._api_public_key = credential.public_key_decrypted
            self._valid = True
        except:
            # @todo add logger
            self._api_private_key = 'ERROR'
            self._api_public_key = 'ERROR'
            self._valid = False

    def get_dynamic_price(self, pair_id, bid_spread, ask_spread, implementation_counter=0):
        pass

    def get_price(self, pair_id):
        pass

    def get_real_price(self):
        pass

    def create_order(self, pair_eid, amount, price, side):
        pass

    def get_order_status(self, order):
        # Monetum Exchange does not support!
        pass

    def get_user_balance(self):
        pass

    def get_currencies(self):
        pass

    def get_pairs(self):
        pass

    @staticmethod
    def credential_check(private_key, public_key):
        return False

class Temp:
    pass

