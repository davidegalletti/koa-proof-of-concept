from django.db import models


class DBConnection(models.Model):
    connection_string = models.CharField(max_length=255L)


class Entity(models.Model):
    version = models.IntegerField(blank=True)
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    table_name = models.CharField(max_length=255L, db_column='tableName', blank=True) 
    id_field = models.CharField(max_length=255L, db_column='idField', blank=True)
    name_field = models.CharField(max_length=255L, db_column='nameField', blank=True)
    description_field = models.CharField(max_length=255L, db_column='descriptionField', blank=True)
    version_released = models.IntegerField(null=True, db_column='versionReleased', blank=True)
    connection = models.ForeignKey(DBConnection, null=True, blank=True)
    def __unicode__(self):
        return self.name + " (" + self.version + ")" 

class Attribute(models.Model):
    name = models.CharField(max_length=255L, blank=True)
    entity = models.ForeignKey('Entity', null=True, blank=True)
    def __unicode__(self):
        return self.entity.name + "." + self.name 

