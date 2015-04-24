from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Taxonomy, Protein, Annotation, NcbiTaxonomy


class TaxonomyAdmin(admin.ModelAdmin):
    #fields = ['taxon', 'name', 'group']
    list_display = ('taxon', 'name', 'name_common', 'group')


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('protein', 'taxonomy', 'species_name', 'israb', 'rab_subfamily', 'rab_subfamily_score')

    def species_name(self, instance):
        return instance.taxonomy.name


class NcbiTaxonomyAdmin(TreeAdmin):
    form = movenodeform_factory(NcbiTaxonomy)


admin.site.register(Taxonomy, TaxonomyAdmin)
admin.site.register(Protein)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(NcbiTaxonomy, NcbiTaxonomyAdmin)
