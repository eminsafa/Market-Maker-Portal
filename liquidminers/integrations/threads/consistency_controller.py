## BU KISIMDA DATABASE MODEL CONSISTENCY SAGLANMASI AMACLANMAKTADIR.
## ORNEGIN, MEVCUT BIR POOLDA MEVCUT BIR INVESTMENT'TA DEGISIKLIK YAPILIR
## VE YENI BIR INVESTMENT OLUSTURULURSA ESKI INVESTMENT'A AIT ORDER_CONFIG
## OBJESI SILINMIS OLMALIDIR. --> bunu investment olusturulurken uyguladim ancak yine de benzer
## consistency check islemleri yapilabilir.


# INVESTMENT STATUS CHECK
# investments = Investment.objects.filter(pool__end_date__lt=datetime.datetime.now(), status__name='ACTIVE')
# # @todo this is maybe available on consistency check part
# reward_objects = Pool.objects.filter(end_date__lt=datetime.datetime.now(), status__name='ACTIVE')
# passive = Status.objects.get(name='PASSIVE')
# for i in investments:
#     i.status = passive
#     i.save()
# for r in reward_objects:
#     r.status = passive
#     r.save()


# @todo main issue: CHECK IF MULTIPLE REWARD SHARED ON SAME TIME INTERVAL!
# @todo configlerde iki taraf da filled oldu ise ikisini de sil.