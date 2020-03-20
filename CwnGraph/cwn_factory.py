from .cwn_types import *
from .cwn_graph_utils import CwnGraphUtils

class CwnNodeFactory:
    @staticmethod
    def createNode(node_id, cgu: CwnGraphUtils):        
        node_class_map = {
            "glyph": CwnGlyph,            
            "lemma": CwnLemma,
            "sense": CwnSense,
            "synset": CwnSynset,
            "facet": CwnFacet
        }
        node_data = cgu.get_node_data(node_id)
        node_type = node_data.get("node_type", "")
        if node_type not in node_class_map:
            raise ValueError("Unrecognized node_type: " + node_type)
        node_class = node_class_map[node_type]
        node = node_class(node_id, cgu)

        return node

class CwnEdgeFactory:        
    @staticmethod
    def createEdge(edge_id, cgu: CwnGraphUtils):   
        # edge_data = cgu.get_edge_data(edge_id)
        edge = CwnRelation(edge_id, cgu)
        return edge