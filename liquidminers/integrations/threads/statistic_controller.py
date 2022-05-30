import datetime
from datetime import timedelta

from django.db.models import Sum

from liquidminers.models import Order
from liquidminers.models.log import Log
from liquidminers.models.pool import Pool
from liquidminers.models.statistic import Statistic
from liquidminers.utils import singleton


@singleton
class StatisticControllerAbstract:

    def __init__(self):
        pass

    def main(self):
        pass

    def daily_pool_volume_statistic(self):
        pools = Pool.objects.filter(status__name='ACTIVE')
        today = datetime.date.today()
        for pool in pools:
            last_processed_day = self.get_last_processed_day('archive_daily_pool_volume', pool.id)
            if last_processed_day is None:
                start_day = pool.start_date
            else:
                start_day = last_processed_day.datetime.date() + timedelta(days=1)
                # replace(hours=0, minutes=0, seconds=0, microseconds=0)
            days = (today - start_day).days
            for d in range(days):
                pd = start_day + timedelta(days=d)
                midnight = pd + timedelta(days=1)
                orders = Order.objects.filter(created_at__gte=pd, created_at__lte=midnight, pool_id=pool.id).aggregate(Sum('worth'))
                if orders['worth__sum'] is None:
                    orders['worth__sum'] = 0
                day_volume = round(orders['worth__sum'], 2)
                save_datetime = datetime.datetime(pd.year, pd.month, pd.day, 0, 0, 0)
                Statistic.save_statistic('archive_daily_pool_volume', day_volume, pool.id, save_datetime)

    def get_last_processed_day(self, name, lookup_id):
        return Statistic.objects.filter(name=name, lookup_id=lookup_id, datetime__lt=datetime.datetime.today()).order_by('updated_at').last()


class StatisticController:

    @staticmethod
    def daily():
        try:
            x = StatisticControllerAbstract()
            x.daily_pool_volume_statistic()
        except Exception as e:
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            Log.on(f"AUTO CANCEL -> {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}", "AC_ERROR")
