from django.db import models

from liquidminers.models.mixins import Status


class Transaction(models.Model):

    pool = models.ForeignKey('liquidminers.Pool', on_delete=models.CASCADE, null=True)
    week = models.ForeignKey('liquidminers.Week', on_delete=models.CASCADE, null=True)
    status = models.ForeignKey('liquidminers.Status', on_delete=models.CASCADE, null=True)

    @staticmethod
    def get_status(pool, week):
        transaction_status = Transaction.objects.filter(pool=pool, week=week)
        if len(transaction_status) == 0:
            status = Status.objects.get(name='NOT PROCESSED')
            t = Transaction(pool=pool, week=week, status=status)
            t.save()
            return t.status
        elif len(transaction_status) == 1:
            return transaction_status[0].status
        else:
            # @todo log
            #Log('error', 'There are multiple Transaction! Rew: ' + str(reward.id) + ' Week: ' + str(week.id)).save()
            return transaction_status[0].status
