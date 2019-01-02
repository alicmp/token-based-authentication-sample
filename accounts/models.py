# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, phone_number, username=None, password=None, is_active=True, is_staff=False, is_admin=False): # pylint: disable=R0913
        if not phone_number:
            raise ValueError("Users must have a phone number")
        user_obj = self.model(
            phone_number=phone_number,
        )
        if not password:
            user_obj.set_unusable_password()
        else:
            user_obj.set_password(password) # change user password
        user_obj.username = username
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone_number, username=None, password=None):
        user = self.create_user(
            username=username,
            phone_number=phone_number,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, phone_number, password, username=None):
        user = self.create_user(
            username=username,
            phone_number=phone_number,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        return user

class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=17, unique=True)
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'phone_number' #username
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return "{}".format(self.phone_number)

