from django.db import models
# from entity.models import EntityInstance
from entity.models import SerializableEntity
    

class Albero(SerializableEntity):
#     def __init__(self):
#         EntityInstance.__init__(self)
    name = models.CharField(max_length=100L)

class Frutto(SerializableEntity):
#     def __init__(self):
#         EntityInstance.__init__(self)
    name = models.CharField(max_length=100L)
    albero = models.ForeignKey(Albero)

class Frutteto(SerializableEntity):
#     def __init__(self):
#         EntityInstance.__init__(self)
    name = models.CharField(max_length=100L)
    alberi = models.ManyToManyField(Albero, blank=True)
