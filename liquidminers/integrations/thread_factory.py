import random
import threading
import time

from liquidminers.integrations.threads.auto_cancel_controller import AutoCancelController
from liquidminers.integrations.threads.order_controller import OrderController
from liquidminers.integrations.threads.reward_controller import RewardController
from liquidminers.integrations.threads.statistic_controller import StatisticController
from liquidminers.models.configuration import Configuration
from liquidminers.models.log import Log
from liquidminers.utils import singleton


@singleton
class ThreadController:
    _threads = {}
    _max_thread_count = 1
    _loop_delay = 2
    _configuration_status = False

    _delays = {
        'log_cleaner': 1000,
        'sharing_calculation': 5,
        'check_conf_status': 2,
    }

    def __init__(self):
        pass

    def check_conf_status(self):
        # self._configuration_status = True
        self._configuration_status = Configuration.is_trade_engine_active()

    def parent_controller(self):
        thread_count = len(self._threads)
        self.check_conf_status()
        if thread_count < 1:
            reward_sharing_thread_initialized = True
        else:
            reward_sharing_thread_initialized = False
        if self._configuration_status:
            if thread_count < self._max_thread_count:
                thread_id = self.generate_id()
                new_thread = threading.Thread(target=self.thread_body, args=(thread_id, reward_sharing_thread_initialized,))
                reward_sharing_thread_initialized = False
                self._threads[thread_id] = new_thread
                new_thread.start()
                time.sleep(2)

    def generate_id(self):
        thread_id = ''.join(random.choice([chr(i) for i in range(ord('a'), ord('z'))]) for _ in range(8)).upper()
        if thread_id in self._threads.keys():
            return self.get_thread_id()
        else:
            return thread_id

    def thread_body(self, thread_id, reward_sharing):
        print("\033[0;34m" + "THREAD INITIALIZED" + "\033[0m")
        print("\033[0;34m" + "ID: " + thread_id + "\033[0m")
        print("\033[0;34m" + "RS: " + str(reward_sharing) + "\033[0m")
        print("\033[0;34m" + "RS: " + str(self._threads) + "\033[0m")
        self.check_conf_status()
        order_controller = OrderController(thread_id)
        i = 0
        while True:
            if self._configuration_status:
                try:
                    order_controller.main()
                    AutoCancelController.main()
                except Exception as e:
                    print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
                    Log.on(f"THREAD=ORDER_CONT OR AUTOCANCEL ---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'API_ERROR')

                if i % self._delays['check_conf_status'] == 0:
                    self.check_conf_status()
                    self.parent_controller()
                if i % self._delays['sharing_calculation'] == 0:
                    if reward_sharing:
                        RewardController.main()
                if i % self._delays['log_cleaner'] == 0:
                    Log.cleaner()
                    StatisticController.daily()
                if i > 10000:
                    i = 0
                time.sleep(self._loop_delay)
                i += 1
            else:
                # THREAD ENGINE STOP
                del self._threads[thread_id]
                break


class ThreadFactory:

    @staticmethod
    def run():
        thread_controller = ThreadController()
        thread_controller.parent_controller()
