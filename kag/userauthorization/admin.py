from django.contrib import admin
from userauthorization.models import PermissionHolder, KUser, Role, Group

class KUserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Anagrafica', {'fields' :['name', 'surname']}),
        ('Accesso',    {'fields' :['login', 'password'], 'classes': ['collapse']}),
        (None,         {'fields' :['permission_holder']}),

    ]

admin.site.register(KUser, KUserAdmin)
admin.site.register(PermissionHolder)
admin.site.register(Role)
admin.site.register(Group)


