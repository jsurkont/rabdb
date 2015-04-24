from django.db import models
from treebeard.mp_tree import MP_Node


class TaxonomyManager(models.Manager):

    def get_by_natural_key(self, taxon):
        return self.get(taxon=taxon)


class Taxonomy(models.Model):
    objects = TaxonomyManager()

    taxon = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, unique=True)
    name_common = models.CharField(max_length=128, blank=True)
    group = models.CharField(max_length=32)

    def __unicode__(self):
        return str(self.taxon)


class ProteinManager(models.Manager):

    def get_by_natural_key(self, protein_id):
        return self.get(protein=protein_id)


class Protein(models.Model):
    objects = ProteinManager()

    protein = models.CharField(max_length=32, unique=True)
    transcript = models.CharField(max_length=32, unique=True)
    gene = models.CharField(max_length=64)
    uniprot = models.CharField(max_length=32, blank=True)
    description = models.TextField()
    seq = models.TextField()
    comment = models.TextField(blank=True)

    def __unicode__(self):
        return str(self.protein)


class Annotation(models.Model):
    protein = models.ForeignKey(Protein)
    taxonomy = models.ForeignKey(Taxonomy)

    gprotein = models.CharField(max_length=32)
    log10_evalue_rab = models.FloatField()
    log10_evalue_nonrab = models.FloatField(blank=True, null=True)
    rabf = models.CharField(max_length=256)
    israb = models.BooleanField()
    rab_subfamily = models.CharField(max_length=16)
    rab_subfamily_score = models.FloatField()
    rab_subfamily_top5 = models.CharField(max_length=256)


class NcbiTaxonomy(MP_Node):
    taxon_id = models.IntegerField(unique=True)
    node_rank = models.CharField(max_length=64)
    taxon_name = models.CharField(max_length=128)

    node_order_by = ['taxon_id']

    def __unicode__(self):
        return 'NcbiTaxonomy: {}'.format(self.taxon_id)
