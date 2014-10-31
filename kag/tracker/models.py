from django.db import models
from entity.models import WorkflowEntityInstance, SerializableEntity

class ResolutionType(SerializableEntity):
    name = models.CharField(max_length=100L)

class Issue(WorkflowEntityInstance):
    title = models.CharField(max_length=100L)
    description = models.TextField()
    resolution_type = models.ForeignKey(ResolutionType)

class Note(SerializableEntity):
    issue = models.ForeignKey(Issue, related_name='notes')
    text = models.TextField()




