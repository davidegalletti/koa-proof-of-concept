from django.db import models

class PermissionHolder(models.Model):
    methods = models.ManyToManyField('application.Method', blank=True)

class KUser(models.Model):
    login = models.CharField(max_length=255L, blank=True)
    password = models.CharField(max_length=255L, blank=True)
    name = models.CharField(max_length=255L, blank=True)
    surname = models.CharField(max_length=255L, blank=True)
    permission_holder = models.OneToOneField(PermissionHolder)
    def __unicode__(self):
        return self.name + " " + self.surname + " (" + self.login + ")"

class Role(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    permission_holder = models.OneToOneField(PermissionHolder)
    users = models.ManyToManyField(KUser)
    def __unicode__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    permission_holder = models.OneToOneField(PermissionHolder)
    users = models.ManyToManyField(KUser)
    def __unicode__(self):
        return self.name

