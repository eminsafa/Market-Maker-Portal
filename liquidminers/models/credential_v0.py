# import base64
# import re
#
# from cryptography.fernet import Fernet
# from django.db import models
#
# from liquidminers.models.user import User
# from liquidminers.models.utils import lazy_property
#
#
# #import codecs
#
# #codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)
#
# class Credential(models.Model):
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     exchange = models.CharField(max_length=32, null=True)
#     public_key = models.TextField()
#     private_key = models.TextField()
#
#
#     @lazy_property
#     def public_key_decrypted(self):
#         cipher = Fernet(self.user.salt.encode()+b'12345678901=')
#         return cipher.decrypt(self.private_key.encode()).decode()
#
#     @lazy_property
#     def private_key_decrypted(self):
#         cipher = Fernet(self.user.salt.encode()+b'12345678901=')
#         return cipher.decrypt(self.private_key.encode()).decode()
#
#     @staticmethod
#     def set_credential(user, exchange, public_key, private_key):
#         cipher = Fernet(user.salt.encode()+b'12345678901=')
#         Credential.objects.filter(user=user, exchange=exchange).delete()
#         Credential.objects.create(
#             user=user,
#             exchange=exchange,
#             public_key=cipher.encrypt(public_key.encode()).decode(),
#             private_key=cipher.encrypt(private_key.encode()).decode()
#         )
#
#
#
#
