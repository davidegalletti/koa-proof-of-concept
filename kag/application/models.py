from django.db import models
from entity.models import WorkflowMethod, WorkflowEntity, VersionableEntityInstance, SerializableEntity

class Method(WorkflowMethod):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    attributes = models.ManyToManyField('entity.Attribute', blank=True)
    create_instance = models.BooleanField(default=False)
    script_precondition = models.TextField(blank=True)
    script_postcondition = models.TextField(blank=True)
    script_premethod = models.TextField(blank=True)
    script_postmethod = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Widget(SerializableEntity):
    '''
    It is a django widget; TBC
    '''
    widgetname = models.CharField(max_length=255L, blank=True)

class Application(WorkflowEntity):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    methods = models.ManyToManyField(Method)

    def __str__(self):
        return self.name

