# import base64
# import re
#
# from Crypto import Random
# from Crypto.Cipher import AES
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
#         cipher = AESCipher(self.user.salt)
#         return cipher.decrypt(self.public_key)
#
#     @lazy_property
#     def private_key_decrypted(self):
#         cipher = AESCipher(self.user.salt)
#         return cipher.decrypt(self.private_key)
#
#     @staticmethod
#     def set_credential(user, exchange, public_key, private_key):
#         cipher = AESCipher(user.salt)
#         Credential.objects.filter(user=user, exchange=exchange).delete()
#         Credential.objects.create(
#             user=user,
#             exchange=exchange,
#             public_key=cipher.encrypt(public_key),
#             private_key=cipher.encrypt(private_key)
#         )
#
#
#
# class AESCipher:
#
#     def __init__(self, salt):
#         self.salt = salt
#         self.block_size = 32
#
#     def encrypt(self, raw):
#         if raw is None or len(raw) == 0:
#             raise NameError("No value given to encrypt!")
#         raw = raw + ('\0' * (self.block_size - len(raw) % self.block_size))
#         raw = raw.encode('utf8')
#         iv = Random.new().read(AES.block_size)
#         cipher = AES.new(self.salt.encode('utf8'), AES.MODE_CFB, iv)
#         return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf8')
#
#     def decrypt(self, enc):
#         if enc is None or len(enc) == 0:
#             raise NameError("No value given to decrypt!")
#         enc = base64.b64decode(enc)
#         iv = enc[:16]
#         cipher = AES.new(self.salt.encode('utf8'), AES.MODE_CFB, iv)
#         return re.sub(b'\x00*$', b'', cipher.decrypt( enc[16:])).decode('utf8')
