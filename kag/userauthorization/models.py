from django.db import models

class PermissionHolder(models.Model):
    methods = models.ManyToManyField('application.Method')

class User(models.Model):
    login = models.CharField(max_length=255L, blank=True)
    password = models.CharField(max_length=255L, blank=True)
    name = models.CharField(max_length=255L, blank=True)
    surname = models.CharField(max_length=255L, blank=True)
    permission_holder = models.ForeignKey(PermissionHolder)

class Role(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    permission_holder = models.ForeignKey(PermissionHolder)
    users = models.ManyToManyField(User)

class Group(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    permission_holder = models.ForeignKey(PermissionHolder)
    users = models.ManyToManyField(User)

