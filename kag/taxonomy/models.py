from django.db import models


class TaxonomyLevel(models.Model):
    table_name = models.CharField(max_length=255L, blank=True)
    description_field = models.CharField(max_length=255L, db_column='descriptionField', blank=True) # Field name made lowercase.
    id_field = models.CharField(max_length=255L, db_column='idField', blank=True) # Field name made lowercase.
    name_field = models.CharField(max_length=255L, db_column='nameField', blank=True) # Field name made lowercase.
    label = models.CharField(max_length=255L, blank=True)
    default = models.BooleanField(default=True)
    entity = models.ForeignKey('entity.Entity', blank=True)
#    lower_levels = models.ManyToManyField('self')
    upper_levels = models.ManyToManyField('self', through='TaxonomyLevelGraph', symmetrical=False, related_name='lower_levels')

class TaxonomyLevelGraph(models.Model):
    upper = models.ForeignKey(TaxonomyLevel, related_name='upper')
    lower = models.ForeignKey(TaxonomyLevel, related_name='lower')
    foreign_key_upper = models.CharField(max_length=255L)

class Taxonomy(models.Model):
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    first_level = models.ForeignKey(TaxonomyLevel)
    def __str__(self):
        return self.name

