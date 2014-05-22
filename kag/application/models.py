from django.db import models


class Method(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    attributes = models.ManyToManyField('entity.Attribute', blank=True)
    def __unicode__(self):
        return self.name

class Application(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    methods = models.ManyToManyField(Method)
    def __unicode__(self):
        return self.name

