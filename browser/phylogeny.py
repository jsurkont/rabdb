from __future__ import print_function

import sys
import json

import networkx
from networkx.readwrite import json_graph
import ete2


class TaxonomicTree(object):

    def __init__(self, newick_file):
        """Loads a taxonomic tree from an extended Newick file.
        """

        self.tree = ete2.Tree(newick_file, format=1)
        self.tree.name = 'root'
        self.tree.add_features(taxid=1, rank='no rank', sci_name='root')

    def tree2graph(self):
        g = networkx.DiGraph()
        for leaf in self.tree.iter_leaves():
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

        #for node in g.nodes_iter(data=True):
        #    print(node)
        #for edge in g.edges_iter():
        #    print(edge)

        g_dict = [json_graph.tree_data(g, 1)]
        #print(g_dict[0].keys())
        return g_dict


def main(nwk_file, graph_file):
    t = TaxonomicTree(nwk_file)
    with open(graph_file, 'w') as fout:
        json.dump(t.tree2graph(), fout, indent=2)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
