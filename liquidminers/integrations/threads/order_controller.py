import datetime
from datetime import timedelta
from timeit import default_timer as timer

from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.auto_cancel_order import AutoCancelOrder
from liquidminers.models.investment import Investment
from liquidminers.models.investment_log import InvestmentLog
from liquidminers.models.log import Log
from liquidminers.models.mixins import Status
from liquidminers.models.order import Order
from liquidminers.models.order_config import OrderConfig


class OrderController:

    def __init__(self, thread_id):
        self.thread_id = thread_id
        self.lock_duration = 5  # in seconds
        self.item_limit = 6
        self.min_renew_time = 10  # in seconds
        self.status_active = Status.objects.get(name='ACTIVE')
        self.release_all_investments()

    def main(self):
        #start = timer()
        self.investment_controller(self.get_unprocessed_investments())
        #end = timer()
        #Log.on(f"Order Controller Completed at {timedelta(seconds=end - start)}s. Thread ID: {self.thread_id}", 'INFO')

    def get_unprocessed_investments(self):
        try:
            lock_diff = datetime.datetime.now() + datetime.timedelta(seconds=self.lock_duration)
            pre_unprocessed_investments = Investment.objects.filter(
                status__name='ACTIVE',
                pool__end_date__gte=datetime.datetime.now(),
                lock_at__lte=datetime.datetime.now(),
                trigger_at__lte=datetime.datetime.now(),
                thread_id='RELEASED'
            ).order_by('updated_at')[:self.item_limit]

            for pui in pre_unprocessed_investments:
                pui.lock_at = lock_diff
                pui.thread_id = self.thread_id
                pui.save()

            unprocessed_investments = Investment.objects.filter(
                status__name='ACTIVE',
                pool__end_date__gte=datetime.datetime.now(),
                thread_id=self.thread_id,
                trigger_at__lte=datetime.datetime.now()
            ).order_by('updated_at')[:self.item_limit]

            print(f"\033[0;35m          | Investments ({len(unprocessed_investments)})\033[0m")
            return unprocessed_investments
        except Exception as e:
            Log.on(f"UNPROCESSED INVESTMENTS ERROR: ---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'OC_ERROR')

    def investment_controller(self, investments):
        try:
            for investment in investments:
                user = investment.user
                pair = investment.pool.pair
                exchange = ExchangeFactory.get(user, investment.pool.exchange)

                # GET PRICE and WALLET DATA
                buy_price, sell_price, mid_price = exchange.get_dynamic_price(pair.eid, 0, 0)
                if buy_price == 0.0 or sell_price == 0.0:
                    Log(type='error', message='price is 0.0 -> STOPPED').save()
                    investment.release()
                    continue

                if investment.renew_time == 0 or investment.renew_unfilled_orders is False:
                    if investment.param_update_check is False:
                        continue


                order_configurations = OrderConfig.objects.filter(investment=investment)
                for order_configuration in order_configurations:

                    new_buy_order, new_sell_order = self.get_renew_status(investment, order_configuration, exchange)
                    order_coin_amount = float(investment.coin_amount) * order_configuration.balance_allocation

                    balances = exchange.get_user_balance()
                    wallet_coin = balances[pair.buy_side.eid] if pair.buy_side.eid in balances.keys() else 0.0
                    wallet_fiat = balances[pair.sell_side.eid] if pair.sell_side.eid in balances.keys() else 0.0
                    coin_available = wallet_coin
                    fiat_available = wallet_fiat

                    # Zero and Negative Check
                    if order_coin_amount <= 0:
                        Log.on(f'Order amount is 0 on investment #{investment.id} and order queue #{order_configuration.queue}', 'ERROR', investment.user.id)
                        investment.release()
                        continue

                    price_to_buy = mid_price * (1 - order_configuration.ask_spread)
                    price_to_sell = mid_price * (1 + order_configuration.bid_spread)

                    fiat_to_buy = order_coin_amount * price_to_buy
                    fiat_to_sell = order_coin_amount * price_to_sell

                    try:
                        if new_buy_order:
                            if fiat_available < (fiat_to_buy * 0.90):
                                print(f"User ({user.id}) does not have enough balance for buy order.")
                                InvestmentLog.log(investment.id, f'Insufficient Balance for Order', 'Your balance is not enough for creating order pair #{order_configuration.queue}.')
                                continue
                            elif fiat_to_buy > fiat_available > (fiat_to_buy * 0.90):
                                fiat_to_buy = fiat_available * 0.999
                                order_coin_amount = fiat_to_buy / price_to_buy

                            buy_order_result = exchange.create_order(pair.eid, order_coin_amount, price_to_buy, 'buy')
                            # Save Buy Order
                            if buy_order_result is False:
                                Log.on(f'Buy Order creation error. Should not be. Investment: #{investment.id}, Order Queue #{order_configuration.queue} ', 'ERROR', investment.user.id)
                            else:
                                try:
                                    Order(
                                        eid=buy_order_result,
                                        side='buy',
                                        investment=investment,
                                        config=order_configuration,
                                        pool=investment.pool,
                                        status=self.status_active,
                                        amount=order_coin_amount,
                                        price=price_to_buy,
                                        worth=fiat_to_buy,
                                        thread_id=self.thread_id
                                    ).save()
                                except Exception as e:
                                    Log.on(f'Buy Order Save Error!', 'ERROR')
                                    Log.on(f"ORDER SAVE ERROR: Buy IID: {investment.id}---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'OC_ERROR')

                        if new_sell_order:
                            if coin_available < (order_coin_amount * 0.90):
                                print(f"User ({user.id}) does not have enough balance for sell order.")
                                InvestmentLog.log(investment.id, f'Insufficient Balance for Order', 'Your balance is not enough for creating order pair #{order_configuration.queue}.')
                                continue
                            elif order_coin_amount > coin_available > (order_coin_amount * 0.90):
                                order_coin_amount = coin_available * 0.999

                            sell_order_result = exchange.create_order(pair.eid, order_coin_amount, price_to_sell, 'sell')
                            # Save Sell Order
                            if sell_order_result is False:
                                Log.on(f'Sell Order creation error. Should not be. Investment: #{investment.id}, Order Queue #{order_configuration.queue} ', 'ERROR')
                            else:
                                try:
                                    Order(
                                        eid=sell_order_result,
                                        side='sell',
                                        investment=investment,
                                        config=order_configuration,
                                        pool=investment.pool,
                                        status=self.status_active,
                                        amount=order_coin_amount,
                                        price=price_to_sell,
                                        worth=fiat_to_sell,
                                        thread_id=self.thread_id
                                    ).save()
                                except Exception as e:
                                    Log.on(f'SELL Order Save Error!', 'ERROR')
                                    Log.on(f"ORDER SAVE ERROR: Sell IID: {investment.id} ---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'OC_ERROR')

                    except Exception as e:
                        Log.on(f"ORDER CREATION ERROR: ---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'OC_ERROR')

                    fiat_available -= fiat_to_buy
                    coin_available -= order_coin_amount

                    # Auto Cancel Orders
                    auto_cancel_order = AutoCancelOrder.get(investment, order_configuration.queue)
                    auto_cancel_order.ask_price = mid_price * (1 + order_configuration.auto_cancel_ask_deviation)
                    auto_cancel_order.bid_price = mid_price * (1 - order_configuration.auto_cancel_bid_deviation)
                    auto_cancel_order.save()

                investment.updated_at = datetime.datetime.now()  # @todo maybe not needed. #check #performance
                if investment.renew_time > 0:
                    investment.trigger_at = datetime.datetime.now() + datetime.timedelta(seconds=investment.renew_time)
                if investment.renew_time == 0 or investment.renew_unfilled_orders is False:
                    investment.param_update_check = False
                investment.thread_id = 'RELEASED'
                investment.save()

            for investment in investments:
                investment.release()
        except Exception as e:
            Log.on(f"INVESTMENT CONTROLLER: ---> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", 'OC_ERROR')

    def get_renew_status(self, investment, config, exchange):
        new_buy_order = new_sell_order = False
        buy_filled = sell_filled = False
        buy_backup_check = sell_backup_check = 0

        # ---------- BUY ----------
        if config.buy_filled is False:
            orders = Order.objects.filter(
                investment=investment,
                status__name='ACTIVE',
                config=config,
                side='buy'
            )

            if len(orders) > 1:
                log_order_text = ""
                for order in orders:
                    status = exchange.get_order_status(order)
                    log_order_text = log_order_text + str(order.id) + " "
                    if status == 'FILLED':
                        buy_backup_check += 1
                    exchange.cancel_order(order)
                Log.on(f"MultipleBuyOrders OIDs: {log_order_text} IID: {investment.id} - {len(orders)} found.", 'INFO', investment.user)
            elif len(orders) == 1:
                buy_order = orders[0]
                status = exchange.get_order_status(buy_order)
                if status == 'FILLED':
                    buy_filled = True
                else:
                    exchange.cancel_order(buy_order)
                    backup_cancel_check = exchange.get_order_status(buy_order)
                    if backup_cancel_check != 'CANCELLED':
                        Log.on(f"BUY Order Have Not Cancelled! Order OID: {buy_order.id}", "ERROR")
        else:
            buy_filled = True

        # ---------- SELL ----------
        if config.sell_filled is False:
            orders = Order.objects.filter(
                investment=investment,
                status__name='ACTIVE',
                config=config,
                side='sell'
            )

            if len(orders) > 1:
                log_order_text = ""
                for order in orders:
                    status = exchange.get_order_status(order)
                    log_order_text = log_order_text + str(order.id) + " "
                    if status == 'FILLED':
                        sell_backup_check += 1
                    exchange.cancel_order(order)
                Log.on(f"MultipleSellOrders OIDs: {log_order_text} IID: {investment.id} - {len(orders)} found.", 'INFO', investment.user)
            elif len(orders) == 1:
                sell_order = orders[0]
                status = exchange.get_order_status(sell_order)
                if status == 'FILLED':
                    sell_filled = True
                else:
                    exchange.cancel_order(sell_order)
                    backup_cancel_check = exchange.get_order_status(sell_order)
                    if backup_cancel_check != 'CANCELLED':
                        Log.on(f"SELL Order Have Not Cancelled! Order OID: {sell_order.id}", "ERROR")
        else:
            sell_filled = True

        diff = buy_backup_check - sell_backup_check
        if diff != 0:
            Log.on(f"Inconsistency on investment: {investment.id}.", 'INFO', investment.user)
            if diff > 0:
                buy_filled = True
                sell_filled = False
            else:
                sell_filled = True
                buy_filled = False

        if (buy_filled and sell_filled) or (buy_filled is False and sell_filled is False):
            new_buy_order = new_sell_order = True
            config.buy_filled = False
            config.sell_filled = False
        elif buy_filled is True and sell_filled is False:
            new_buy_order = False
            new_sell_order = True
            config.buy_filled = buy_filled
            config.sell_filled = sell_filled
        elif buy_filled is False and sell_filled is True:
            new_buy_order = True
            new_sell_order = False
            config.buy_filled = buy_filled
            config.sell_filled = sell_filled

        config.save()
        return new_buy_order, new_sell_order

    def release_all_investments(self):
        investments = Investment.objects.filter(status=self.status_active)
        for investment in investments:
            investment.release()
