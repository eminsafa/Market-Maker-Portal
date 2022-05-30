from liquidminers.models.statistic import Statistic

class MiddleStatistics:

    def __init__(self):
        pass

    @staticmethod
    def get_liquidity_of_pool(pool_id):
        return Statistic.get_liquidity_of_pool(pool_id)