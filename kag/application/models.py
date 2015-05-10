# -*- coding: utf-8 -*-

from django.db import models
from entity.models import Workflow, WorkflowMethod, SerializableEntity, Attribute

class AttributeInAMethod(SerializableEntity):
    '''
    '''
    attribute = models.ForeignKey(Attribute)
    # workflow is blank unless the attribute is an entity or a set of entities; it can be blank if a method is specified
    # TODO: chiarire il commento di sopra: significa che entità collegate possono avere un sotto workflow?
    workflow = models.ForeignKey(Workflow, blank=True, null=True)
    # method (inline)
    implementation_method = models.ForeignKey("Method", blank=True, null=True)
    #TODO: forse andra' aggiunta qualche informazione per indicare come implementare (e.g. inline)
    
class Method(WorkflowMethod):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    attributes = models.ManyToManyField(AttributeInAMethod, related_name="container_method")
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

class Application(SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    workflows = models.ManyToManyField(Workflow)

    def __str__(self):
        return self.name

