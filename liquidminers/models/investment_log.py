import datetime

from django.db import models


class InvestmentLog(models.Model):
    investment = models.ForeignKey('Investment', on_delete=models.CASCADE, null=True)
    user_display = models.BooleanField(null=True, default=True)
    kind = models.CharField(max_length=8, default='INFO', null=True)
    subject = models.CharField(max_length=64, null=True)
    content = models.TextField()
    param = models.CharField(max_length=64, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    @staticmethod
    def log(investment_id: int, subject: str, content: str, user_display: bool = True, kind: str = 'INFO', param: str = None):
        try:
            InvestmentLog(
                investment_id=investment_id,
                subject=subject,
                content=content,
                user_display=user_display,
                kind=kind,
                param=param
            )
            return True
        except Exception as e:
            print("\033[0;31m" + "<<< LOG SAVING ERROR >>>" + "\033[0m")
            print("\033[0;31m" + f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}" + "\033[0m")
        return False
