import datetime

from liquidminers.models.log import Log
from liquidminers.models.mixins import Week
from liquidminers.models.order import Order
from liquidminers.models.pool import Pool
from liquidminers.models.reward_calculation import RewardCalculation
from liquidminers.models.reward_sharing import RewardSharing
from liquidminers.utils import singleton


@singleton
class RewardControllerAbstract:

    def main(self):
        print("\033[0;32m<<<<< ----+  SharingsCalculation  +---- >>>>>\033[0m")
        try:
            pools = Pool.objects.filter(status__name='ACTIVE')
            dt = datetime.datetime.now()

            current_week = Week.get(dt).id
            for pool in pools:
                pool_week_configs = pool.weekly_amount.all()
                for week_config in pool_week_configs:
                    processing_week = week_config.week
                    if processing_week.id <= current_week:
                        self.calculate_reward_sharing(pool, week_config)
            print("\033[0;32m          | Done.\033[0m")
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            Log.on("Error occurred during RewardSharing calculation! Check Data", "ERROR")

    def calculate_reward_sharing(self, pool, week_config):
        shared_reward = 0.0
        last_calculation = RewardCalculation.objects.filter(pool=pool).order_by('-end')
        if len(last_calculation) == 0:
            start_dt = week_config.week.start
        else:
            start_dt = last_calculation[0].end

        now = datetime.datetime.now()
        pool_end_dt = datetime.datetime(pool.end_date.year, pool.end_date.month, pool.end_date.day, 23, 59, 59, 999)
        if now > pool_end_dt:
            end_dt = pool_end_dt
        else:
            end_dt = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)

        time_delta = end_dt - start_dt
        total_minutes = time_delta.total_seconds() / 60
        if total_minutes < 1.0:
            print("\033[0;32m          | Passed. Need More Time\033[0m")
            return False

        orders = Order.objects.filter(pool=pool, created_at__gt=start_dt, created_at__lte=end_dt)
        ask_reward = bid_reward = week_config.amount / 10080 / 2 * total_minutes

        orders_list = {}
        total_ask_point = 0.0
        total_bid_point = 0.0
        for order in orders:
            if order.side == 'buy':
                point = order.amount * self.spread_weight(pool.max_spread, order.config.ask_spread)
                total_ask_point += point
            elif order.side == 'sell':
                point = order.amount * self.spread_weight(pool.max_spread, order.config.bid_spread)
                total_bid_point += point
            else:
                Log.on(f"Error on order size. Reward ID: {pool.id} Week ID: {week_config.week.id}", "ERROR")
                continue

            if order.investment not in orders_list:
                orders_list[order.investment] = []

            orders_list[order.investment].append({
                'order': order,
                'point': point
            })

        if total_ask_point <= 0.0 and total_bid_point <= 0.0:
            print("\033[0;32m          | No Reward Point to Share\033[0m")
            return False
        # @todo CRUCIAL WEEK NUMBER IS NOT LOGICAL
        calculation = RewardCalculation(
            pool=pool,
            week=week_config.week,
            start=start_dt,
            end=end_dt,
            duration=total_minutes
        )
        calculation.save()

        for investment in orders_list:
            print(f"\033[0;32m          | Saving Reward of Investment #{investment.id}\033[0m")
            total_investment_reward = 0.0
            for order_dict in orders_list[investment]:
                if order_dict['order'].side == 'buy':
                    if total_ask_point > 0.0:
                        reward = ask_reward * order_dict['point'] / total_ask_point
                    else:
                        reward = 0
                else:
                    if total_bid_point > 0.0:
                        reward = bid_reward * order_dict['point'] / total_bid_point
                    else:
                        reward = 0
                total_investment_reward += reward

            if total_investment_reward > 0.0:
                RewardSharing(
                    investment=investment,
                    week=week_config.week,
                    amount=total_investment_reward,
                    calculation=calculation
                ).save()

            shared_reward += total_investment_reward

        calculation.amount = shared_reward
        calculation.save()
        print(f"Reward calculated! for reward: {pool.id} week: {week_config.week.id}")

    def spread_weight(self, max_spread, spread) -> float:
        coef = spread / max_spread
        if coef == 0:
            return 1
        elif coef <= 0.2:
            return 0.95
        elif coef <= 0.3:
            return 0.9
        elif coef <= 0.6:
            return 1.5 - (2 * coef)
        elif coef <= 1:
            return 0.6 - (0.5 * coef)
        else:
            return 0


class RewardController:

    @staticmethod
    def main():
        reward_controller = RewardControllerAbstract()
        reward_controller.main()
