# -*- coding: utf-8 -*-

from django.db import models
from entity.models import Workflow, WorkflowMethod, SerializableSimpleEntity, Attribute

class AttributeInAMethod(SerializableSimpleEntity):
    '''
    '''
    attribute = models.ForeignKey(Attribute)
    # ASSERT: exactly one out of workflow and implementation_method is not null
    # workflow not null means we have a sub-workflow for the attribute; ASSERT: in this case
    # the attribute must point to an instance of a SimpleEntity of the same class of the SimpleEntity
    # that is in the entry_point of workflow.entity
    workflow = models.ForeignKey(Workflow, blank=True, null=True)
    # method (inline)
    implementation_method = models.ForeignKey("Method", blank=True, null=True)
    #forse andra' aggiunta qualche informazione per indicare come implementare (e.g. inline)
    
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

class Widget(SerializableSimpleEntity):
    '''
    It is a django widget; TBC
    '''
    widgetname = models.CharField(max_length=255L, blank=True)

class Application(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    description = models.TextField(blank=True)
    workflows = models.ManyToManyField(Workflow)

    def __str__(self):
        return self.name

