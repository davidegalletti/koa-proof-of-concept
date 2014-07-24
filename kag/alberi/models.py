from django.db import models
from entity.models import SerializableEntity
    

class Albero(SerializableEntity):
    name = models.CharField(max_length=100L)

class Frutto(SerializableEntity):
    name = models.CharField(max_length=100L)
    albero = models.ForeignKey(Albero)

class Frutteto(SerializableEntity):
    name = models.CharField(max_length=100L)
    alberi = models.ManyToManyField(Albero, related_name="frutteti", blank=True)
