import random

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField('email', unique=True)
    salt = models.CharField(max_length=32, null=False, default='gknvmnewgyoqeuivcpdpuhfbrqfwctmc')
    verification_code = models.CharField(max_length=32, null=False, default='gknvmnewgyoqeuivcpdpuhfbrqfwctmc')
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=32, null=True)   # owner

    def set_salt(self):
        if self.salt == 'gknvmnewgyoqeuivcpdpuhfbrqfwctmc':
            self.salt = ''.join(random.choice([chr(i) for i in range(ord('a'), ord('z'))]) for _ in range(32))
            self.save()

    @property
    def user_role(self):
        if self.role is None or self.role == '':
            return 'user'
        elif self.role == 'owner':
            return 'owner'




