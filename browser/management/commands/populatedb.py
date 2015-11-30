import os
import re
import math
import json

import ete2
import networkx
from networkx.readwrite import json_graph
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from browser.models import Annotation, Taxonomy, Protein, NcbiTaxonomy


class Command(BaseCommand):
    help = "Populate tables from Rabifier predictions. " \
           "Rab predictions should be organized as a set of jason files (output of Rabifier), in a single directory. " \
           "Each file contains Rab predictions for a single species, file name should correspond to the species' " \
           "taxon id e.g. for human '9606.json'. Only positive predictions (i.e. putative Rabs) are included in " \
           "the database). " \
           "Taxonomy is build based on the NCBI taxonomy using ete2 module, some files are downloaded to the $HOME, " \
           "check http://pythonhosted.org/ete2/tutorial/tutorial_ncbitaxonomy.html for more details."

    def add_arguments(self, parser):
        parser.add_argument('path', help='path to a directory with Rab predictions')

    def handle(self, *args, **options):
        rr = RabminerReader(options['path'])
        summary = rr.insert_annotations()
        self.stdout.write('Inserted {annotations} annotations for {taxa} taxa'.format(**summary))
        summary = rr.insert_tree()
        self.stdout.write('Inserted tree with {leaves} leaves and {internal_nodes} internal nodes'.format(**summary))


class RabminerReader(object):

    def __init__(self, path):
        self.path = path
        self.taxon2file = {int(os.path.splitext(f)[0]): f for f in os.listdir(path)}  # all taxa names must be integers
        assert self.taxon2file.keys()
        self.ncbi = ete2.NCBITaxa()
        self.taxon2name = self.ncbi.get_taxid_translator(self.taxon2file.keys())

    @atomic
    def insert_annotations(self):
        pattern = re.compile('gene:(\S+) transcript:(\S+)')
        counter_taxa = 0
        counter_annotations = 0
        for taxon in self.taxon2file:
            #print '{},{}'.format(taxon, self.taxon2name[taxon])
            taxonomy_record = Taxonomy(taxon=taxon, name=self.taxon2name[taxon])
            taxonomy_record.save()
            counter_taxa += 1
            with open(os.path.join(self.path, self.taxon2file[taxon])) as handle:
                a = json.load(handle)
                for b in a.itervalues():
                    if b['is_rab']:
                        assert b['evalue_bh_rabs'] is not None and b['evalue_bh_rabs'] != 10
                        assert b['evalue_bh_rabs'] < b['evalue_bh_non_rabs'] or (b['evalue_bh_rabs'] and b['evalue_bh_non_rabs'] is None)
                        gene, transcript = pattern.findall(b['sequence']['header'])[0]
                        protein_record = Protein(protein=b['id'], transcript=transcript, gene=gene,
                                                 description=b['sequence']['header'], seq=b['sequence']['seq'])
                        protein_record.save()
                        annotation_record = Annotation(protein=protein_record, taxonomy=taxonomy_record,
                                                       gprotein=' '.join(b['gdomain_regions']),
                                                       log10_evalue_rab=math.log10(b['evalue_bh_rabs']) if b['evalue_bh_rabs'] > 0 else b['evalue_bh_rabs'],
                                                       log10_evalue_nonrab=None if b['evalue_bh_non_rabs'] is None else 0 if b['evalue_bh_non_rabs'] == 0 else math.log10(b['evalue_bh_non_rabs']),
                                                       rabf='|'.join(' '.join(map(str, x)) for x in b['rabf_motifs']),
                                                       israb=b['is_rab'],
                                                       rab_subfamily=b['rab_subfamily'][0],
                                                       rab_subfamily_score=b['rab_subfamily'][1],
                                                       rab_subfamily_top5='|'.join(' '.join(map(str, x)) for x in b['rab_subfamily_top_5']))
                        annotation_record.save()
                        counter_annotations += 1

        return {'taxa': counter_taxa, 'annotations': counter_annotations}

    def insert_tree(self):
        tree = self.ncbi.get_topology(self.taxon2name.keys())
        tree.name = 'root'
        tree.add_features(taxid=1, rank='no rank', sci_name='root')
        g = networkx.DiGraph()
        for leaf in tree.iter_leaves():
            g.add_node(int(leaf.taxid), data={'taxon_id': int(leaf.taxid), 'node_rank': leaf.rank, 'taxon_name': leaf.sci_name})
            child = leaf
            for parent in leaf.get_ancestors():
                if g.has_node(int(parent.taxid)):
                    g.add_edge(int(parent.taxid), int(child.taxid))
                    break
                else:
                    g.add_node(int(parent.taxid), data={'taxon_id': int(parent.taxid), 'node_rank': parent.rank, 'taxon_name': parent.sci_name})
                    g.add_edge(int(parent.taxid), int(child.taxid))
                child = parent

        g_dict = [json_graph.tree_data(g, 1)]
        NcbiTaxonomy.load_bulk(g_dict)
        counter_nodes = sum(1 for _ in tree.traverse())
        return {'internal_nodes': counter_nodes - len(tree), 'leaves': len(tree)}
