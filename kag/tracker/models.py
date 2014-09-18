from django.db import models
from entity.models import WorkflowEntityInstance

class ResolutionType(models.Model):
    name = models.CharField(max_length=100L)

class Issue(WorkflowEntityInstance):
    title = models.CharField(max_length=100L)
    description = models.TextField()
    resolution_type = models.ForeignKey(ResolutionType)
