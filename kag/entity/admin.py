from django.contrib import admin
from entity.models import DBConnection, Entity, Attribute

admin.site.register(Attribute)
admin.site.register(DBConnection)
admin.site.register(Entity)

