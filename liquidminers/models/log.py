import datetime

from django.db import models

from liquidminers.models.user import User


class Log(models.Model):
    # Log
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    type = models.CharField(max_length=16, default='INFO', null=True)
    message = models.TextField()

    @staticmethod
    def test():
        print('OK')

    @staticmethod
    def on(message, kind='INFO', user=None):
        try:
            Log(user=user, type=kind, message=message).save()
        except Exception as e:
            print("\033[0;31m" + "<<< LOG SAVING ERROR >>>" + "\033[0m")
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
            return False
        return True

    @staticmethod
    def cleaner():
        APILog.objects.filter(timestamp__lte=datetime.datetime.now() - datetime.timedelta(days=1)).delete()
        Log.objects.filter(timestamp__lte=datetime.datetime.now() - datetime.timedelta(days=5)).delete()


class APILog(models.Model):
    # Log
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    endpoint = models.CharField(max_length=128, null=True)
    method = models.CharField(max_length=32, null=True, default='GET')
    params = models.TextField()
    response = models.TextField()
