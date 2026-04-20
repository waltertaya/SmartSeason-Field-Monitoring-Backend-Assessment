from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        AGENT = 'agent', 'Field Agent'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.AGENT)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_agent(self):
        return self.role == self.Role.AGENT