from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from liquidminers.integrations.exchange_factory import ExchangeFactory
from liquidminers.models.auto_cancel_order import AutoCancelOrder
from liquidminers.models.investment import Investment
from liquidminers.models.investment import Status
from liquidminers.models.investment_shift import InvestmentShift
from liquidminers.models.order import Order
from liquidminers.models.order_config import OrderConfig
from liquidminers.models.pool import Pool
from liquidminers.models.reward_sharing import RewardSharing
from liquidminers.models.user import User
from liquidminers.utils import Temp, get_secure_num, get_switch_state
from liquidminers.views.utils import page_details


@login_required
def bot(request):
    if 'secret_user_id' in request.GET.keys():
        user = User.objects.get(id=int(request.GET['secret_user_id']))
    else:
        user = request.user
    context = {}
    context = {**context, **page_details('bot', user, 'Bot')}

    if request.method == 'POST':
        context = {**context, **create_investment(user, request.POST)}
        pool_id = request.POST['reward_id']
        if 'error' not in context.keys():
            context['success'] = 'Invested successfully!'

    else:
        if 'pool_id' in request.GET.keys():
            pool_id = request.GET['pool_id']
            if 'cancel' in request.GET.keys():
                context = {**context, **cancel_investment(user, pool_id)}
        else:
            return redirect('home')
    pool = Pool.objects.get(id=pool_id)

    exchange = ExchangeFactory.get(user, pool.exchange)
    if not exchange:
        messages.error(request, 'You must integrate your ' + pool.exchange.title() + ' account.')
        return redirect('/settings')

    _, _, price = exchange.get_dynamic_price(pool.pair.eid, 0, 0)

    is_user_invested = pool.is_user_invested(user)
    any_investments = Investment.objects.filter(user=user, pool=pool)
    if len(any_investments) > 0:
        investment = any_investments[0]
        context['investment'] = investment
        context['wallet_address'] = Investment.objects.filter(user=user)[0].wallet_address
    context['is_user_invested'] = is_user_invested
    context['reward'] = pool
    context['pool'] = pool
    context['price'] = price
    context['current_week'] = pool.get_current_week()
    context['balance'] = get_user_balance_for_bot(user, pool)
    context['current_share_of_pool'] = pool.get_share_in_pool(context['balance'].total_value)
    if is_user_invested:
        context = {**context, **RewardSharing.get_reward_sharings(pool, user)}
        context = {**context, **Order.get_all(pool, user)}

    return render(request, 'pages/bot.html', context)


def create_investment(user, d):
    try:
        context = {}
        previous_investments = Investment.objects.filter(user=user, status__name='ACTIVE')
        if len(previous_investments):
            context['error'] = 'ERROR: User have another active investment!'
            return context
        else:
            pool = Pool.objects.get(id=d['reward_id'])
            exchange = ExchangeFactory.get(user, pool.exchange)
            balances = exchange.get_user_balance()
            _, _, price = exchange.get_dynamic_price(pool.pair.eid, 0, 0)
            user_base_balance = balances[pool.pair.buy_side.eid] if pool.pair.buy_side.eid in balances.keys() else 0.0
            user_quote_balance = balances[pool.pair.sell_side.eid] if pool.pair.sell_side.eid in balances.keys() else 0.0

            base_allocation_request = get_secure_num(d, 'base-balance')  # Crypto
            quote_allocation_request = get_secure_num(d, 'quote-balance')  # Fiat

            if base_allocation_request > user_base_balance or quote_allocation_request > user_quote_balance:
                context['error'] = 'Allocated balances are not available in user wallet.'  # @todo on multiple investment available case, check FREE BALANCE
                return context
            elif base_allocation_request == 0 and quote_allocation_request == 0:
                context['error'] = 'Allocated balance should be greater than 0.'
                return context

            crypto_value = price * base_allocation_request
            total_value = crypto_value + user_quote_balance

            ## @todo Balance allocation total should be 100 ! create check line
            ## @todo Balance tolerance below is disabled for testing.

            if total_value < 5.0:  # @todo change this to 50
                context['error'] = 'User balance is less than 50 USD for this pair! Total Value of Wallet: ' + str(total_value)
                return context
            else:
                enable_auto_cancel = get_switch_state(d, 'enable-auto-cancel-switch')
                enable_stop_bot = get_switch_state(d, 'stop-bot-switch')
                order_pair_count = get_secure_num(d, 'number-of-orders')
                renew_enabled = get_switch_state(d, 'renew-with-time-switch')
                renew_unfilled_orders = get_switch_state(d, 'renew-unfilled-orders-switch')

                if renew_enabled:
                    renew_time = get_secure_num(d, 'renew-time')
                else:
                    renew_time = 0

                previous_pool_investments = Investment.objects.filter(user=user, status__name='PASSIVE', pool=pool)
                status = Status.objects.get(name='ACTIVE')

                if len(previous_pool_investments) == 1:
                    ## @todo daha once investment varsa da, yeni bir investment olustur. Investment parametreleri degistirilmemeli.
                    investment = previous_pool_investments[0]
                    investment.status = status
                    investment.wallet_address = d.get('wallet_address', 'not-setted')
                    investment.coin_amount = base_allocation_request
                    investment.fiat_amount = quote_allocation_request
                    investment.order_pair_count = order_pair_count
                    investment.auto_cancel_active = enable_auto_cancel
                    investment.stop_bot_active = enable_stop_bot
                    investment.renew_time = renew_time
                    investment.renew_unfilled_orders = renew_unfilled_orders
                    investment.total_value = total_value
                    investment.save()
                    #InvestmentShift.activate(investment)
                else:
                    investment = Investment(
                        user=user,
                        pool=pool,
                        wallet_address=d.get('wallet_address', 'not-setted'),
                        coin_amount=base_allocation_request,
                        fiat_amount=quote_allocation_request,
                        order_pair_count=order_pair_count,
                        auto_cancel_active=enable_auto_cancel,
                        stop_bot_active=enable_stop_bot,
                        renew_time=renew_time,
                        renew_unfilled_orders=renew_unfilled_orders,
                        total_value=total_value,
                        status=status,
                    )
                    investment.save()

                old_order_configs = OrderConfig.objects.filter(investment=investment)
                for ooc in old_order_configs:
                    ooc.delete()
                old_auto_cancel = AutoCancelOrder.objects.filter(investment=investment)
                for oac in old_auto_cancel:
                    oac.delete()

                for i in range(1, int(order_pair_count) + 1):
                    bid_deviation = min(0.99, max(0.01, abs(get_secure_num(d, 'o' + str(i) + '-bid-deviation')) / 100))
                    ask_deviation = min(2.99, max(0.01, abs(get_secure_num(d, 'o' + str(i) + '-ask-deviation')) / 100))
                    bid_spread = min(0.99, max(0.001, abs(get_secure_num(d, 'o' + str(i) + '-bid-spread')) / 100))
                    ask_spread = min(20.0, max(0.001, abs(get_secure_num(d, 'o' + str(i) + '-ask-spread')) / 100))
                    balance_allocation = min(1.0, max(0.01, abs(get_secure_num(d, 'o' + str(i) + '-allocation')) / 100))

                    order_pair = OrderConfig(
                        investment=investment,
                        balance_allocation=balance_allocation,
                        bid_spread=bid_spread,
                        ask_spread=ask_spread,
                        auto_cancel_bid_deviation=bid_deviation,
                        auto_cancel_ask_deviation=ask_deviation,
                        queue=i
                    )
                    order_pair.save()
                    investment.order_config.add(order_pair)

                    if enable_auto_cancel:
                        auto_cancel_order = AutoCancelOrder(
                            investment=investment,
                            pair=pool.pair,
                            ask_price=price * (1 + ask_deviation),
                            bid_price=price * (1 - bid_deviation),
                            status=status,
                            queue=i
                        )
                        auto_cancel_order.save()
                        investment.auto_cancel_order.add(auto_cancel_order)

                investment.save()
                InvestmentShift.activate(investment)

                context['success'] = 'Investment created successfully'
    except Exception as e:
        print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
        try:
            investment.status = Status.objects.get(name='CANCELLED')
            investment.save()
        except:
            print('ERROR, Investment have not created.')
        context['error'] = 'Investment could not created!'

    return context


def cancel_investment(user, pool_id):
    investments = Investment.objects.filter(user=user, pool_id=pool_id, status__name='ACTIVE')
    if len(investments) == 0:
        return {'error': 'Investment already cancelled!'}
    elif len(investments) != 1:
        return {'error': 'There are multiple investment with same conditions!'}
    else:
        investment = investments[0]
        investment.status = Status.objects.get(name='PASSIVE')
        investment.save()
        InvestmentShift.deactivate(investment)
        # exchange = ExchangeFactory.get(user, investment.pool.exchange)
        # exchange.cancel_all_orders()  # not implemented yet
        return {'success': 'Investment cancelled!'}


def get_user_balance_for_bot(user, pool):
    exchange = ExchangeFactory.get(user, pool.exchange)
    balances = exchange.get_user_balance()
    balance = Temp()
    if pool.pair.buy_side.eid in balances.keys():
        balance.base_amount = balances[pool.pair.buy_side.eid]
    else:
        balance.base_amount = 0.0
    balance.base = pool.pair.buy_side
    if pool.pair.sell_side.eid in balances.keys():
        balance.quote_amount = balances[pool.pair.sell_side.eid]
    else:
        balance.quote_amount = 0.0
    balance.quote = pool.pair.sell_side
    balance.base_value = exchange.get_price(pool.pair.eid).price * balance.base_amount
    balance.total_value = round(balance.base_value + balance.quote_amount, 6)

    balance.base_amount_rounded = round(balance.base_amount, 3)
    balance.quote_amount_rounded = round(balance.quote_amount, 3)
    balance.base_value_rounded = round(balance.base_value, 3)
    balance.total_value_rounded = round(balance.total_value, 3)

    return balance
