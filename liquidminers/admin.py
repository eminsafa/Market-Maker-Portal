from django.contrib import admin

# from liquidminers.models.credential import Credential
from liquidminers.models.currency import Currency
from liquidminers.models.exchange import Exchange
from liquidminers.models.investment import Investment
from liquidminers.models.investment_shift import InvestmentShift
from liquidminers.models.mixins import Status, Week
from liquidminers.models.order import Order
from liquidminers.models.pair import Pair
from liquidminers.models.pool import Pool
from liquidminers.models.reward_sharing import RewardSharing
from liquidminers.models.user import User


class CurrencyAdmin(admin.ModelAdmin):
    temp = []
    for i in Currency._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class ExchangeAdmin(admin.ModelAdmin):
    temp = []
    for i in Exchange._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class InvestmentAdmin(admin.ModelAdmin):
    temp = []
    for i in Investment._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class InvestmentShiftAdmin(admin.ModelAdmin):
    temp = []
    for i in InvestmentShift._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class StatusAdmin(admin.ModelAdmin):
    temp = []
    for i in Status._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class WeekAdmin(admin.ModelAdmin):
    temp = []
    for i in Week._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class OrderAdmin(admin.ModelAdmin):
    temp = []
    for i in Order._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class PairAdmin(admin.ModelAdmin):
    temp = []
    for i in Pair._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class PoolAdmin(admin.ModelAdmin):
    temp = []
    for i in Pool._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class RewardSharingAdmin(admin.ModelAdmin):
    temp = []
    for i in RewardSharing._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


class UserAdmin(admin.ModelAdmin):
    temp = []
    for i in User._meta.fields:
        temp.append(i.__str__().split('.')[-1])
    list_display = tuple(temp)


# admin.site.register(Credential, CredentialAdmin)
# Credentials is not allowed to publish on web admin panel.

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(Investment, InvestmentAdmin)
admin.site.register(InvestmentShift, InvestmentShiftAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Pair, PairAdmin)
admin.site.register(Pool, PoolAdmin)
admin.site.register(RewardSharing, RewardSharingAdmin)
admin.site.register(User, UserAdmin)
