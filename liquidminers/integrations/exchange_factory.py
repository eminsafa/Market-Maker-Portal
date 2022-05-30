from liquidminers.integrations.exchanges.gateio import Gateio
from liquidminers.integrations.exchanges.monetum import Monetum
from liquidminers.utils import singleton
from liquidminers.models.user import User


@singleton
class ExchangeController:
    _exchanges = {"monetum": {}, "gateio": {}}  # "monetum": {<User>: <Exchange>}, "gateio": {} ...
    _admin_user_id = 1

    def __init__(self):
        pass

    def get(self, user, exchange_name):
        if exchange_name not in self._exchanges.keys():
            return False

        if user in self._exchanges[exchange_name]:
            return self._exchanges[exchange_name][user]
        else:
            if exchange_name == 'monetum':
                user_exchange = Monetum(user)
            elif exchange_name == 'gateio':
                user_exchange = Gateio(user)
            else:
                return False
            if user_exchange._valid:
                self._exchanges[exchange_name][user] = user_exchange
                return user_exchange
            else:
                return False

    def delete(self, user, exchange_name):
        if user in self._exchanges[exchange_name].keys():
            self._exchanges[exchange_name].pop(user)
        return True

    def get_exchange_list(self):
        return self._exchanges.keys()

    def check_credentials(self, exchange_name, private_key, public_key):
        if exchange_name == 'monetum':
            return Monetum.check_credentials(private_key, public_key)
        elif exchange_name == 'gateio':
            return Gateio.check_credentials(private_key, public_key)
        else:
            return False

    def is_user_valid(self, user, exchange_name=None):
        if exchange_name is None:
            for exchange in self.get_exchange_list():
                if self.get(user, exchange):
                    return True
        else:
            if self.get(user, exchange_name):
                return True
        return False

    def get_admin_exchange(self, exchange_name):
        try:
            users = User.objects.filter(id=self._admin_user_id)
            if len(users) == 1:
                return self.get(users[0], exchange_name)
            else:
                return None
        except:
            print('CRITICAL ERROR!')
            # @todo log


class ExchangeFactory:

    @staticmethod
    def get(user, exchange_name):
        exchange_controller = ExchangeController()
        return exchange_controller.get(user, exchange_name)

    @staticmethod
    def delete(user, exchange_name):
        exchange_controller = ExchangeController()
        return exchange_controller.delete(user, exchange_name)

    @staticmethod
    def get_exchange_list():
        exchange_controller = ExchangeController()
        return exchange_controller.get_exchange_list()

    @staticmethod
    def check_credentials(exchange_name, private_key, public_key):
        exchange_controller = ExchangeController()
        return exchange_controller.check_credentials(exchange_name, private_key, public_key)

    @staticmethod
    def get_admin_exchange(exchange_name):
        exchange_controller = ExchangeController()
        return exchange_controller.get_admin_exchange(exchange_name)