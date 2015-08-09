from django.db import models
from entity.models import SerializableSimpleEntity

class License(SerializableSimpleEntity):
    '''
    Licenses from the list on http://opendefinition.org/licenses/
    JUST THOSE WITH DOMAIN DATA
    '''
    name = models.CharField(max_length=200L)
    short_name = models.CharField(max_length=50L)
    # human_readable is a summary of the legal code;
    human_readable = models.TextField(null = True, blank=True)
    legalcode = models.TextField(default = "")
    adaptation_shared = models.NullBooleanField(blank=True, null=True)
    # requires to be shared with the attribution
    attribution = models.NullBooleanField(blank=True, null=True)
    # requires to be shared with the same license
    share_alike = models.NullBooleanField(blank=True, null=True)
    commercial_use = models.NullBooleanField(blank=True, null=True)
    url_info = models.CharField(max_length=160L, null = True, blank=True)
    reccomended_by_opendefinition = models.NullBooleanField(blank=True, null=True)
    conformant_for_opendefinition = models.NullBooleanField(blank=True, null=True)
    image = models.CharField(max_length=160L, null=True, blank=True)
    image_small = models.CharField(max_length=160L, null=True, blank=True)
