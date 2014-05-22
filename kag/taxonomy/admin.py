from django.contrib import admin
from taxonomy.models import TaxonomyLevel, TaxonomyLevelGraph, Taxonomy

admin.site.register(Taxonomy)
admin.site.register(TaxonomyLevel)
admin.site.register(TaxonomyLevelGraph)


