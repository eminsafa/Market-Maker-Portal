from django.db import models

from liquidminers.models.user import User
from liquidminers.models.utils import lazy_property


import cryptocode


class Credential(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    exchange = models.CharField(max_length=32, null=True)
    public_key = models.TextField()
    private_key = models.TextField()


    @lazy_property
    def public_key_decrypted(self):
        return cryptocode.decrypt(self.public_key, self.user.salt)

    @lazy_property
    def private_key_decrypted(self):
        return cryptocode.decrypt(self.private_key, self.user.salt)

    @staticmethod
    def set_credential(user, exchange, public_key, private_key):
        Credential.objects.filter(user=user, exchange=exchange).delete()
        Credential.objects.create(
            user=user,
            exchange=exchange,
            public_key=cryptocode.encrypt(public_key, user.salt),
            private_key=cryptocode.encrypt(private_key, user.salt)
        )


