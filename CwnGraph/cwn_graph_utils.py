import pdb
import re
from .cwn_types import *

class CwnGraphUtils(GraphStructure):
    """cwn data as graph (vertices and edges)
    """

    def __init__(self, V, E, meta={}):
        super(CwnGraphUtils, self).__init__()
        self.V = V
        self.E = E
        self.meta = meta
        self.edge_src_index = self.build_index(E.keys(), lambda x: x[0])
        self.edge_tgt_index = self.build_index(E.keys(), lambda x: x[1])

    def build_index(self, data, keyfunc):
        idx = {}        
        for k in data:                   
            idx_key = keyfunc(k)
            idx.setdefault(idx_key, []).append(k)
        return idx

    def find_glyph(self, instr):
        for v, vdata in self.V.items():
            if vdata["node_type"] == "glyph":
                if vdata["glyph"] == instr:               
                   return v
        return None
    
    def find_lemma(self, instr_regex):
        """Find lemmas matching search pattern.
        
        Parameters
        ----------
        instr_regex : str
            RegEx pattern to search for.
        
        Returns
        -------
        list
            A list of :class:`CwnLemma <CwnGraph.cwn_types.CwnLemma>`.
        """
        ret = []
        pat = re.compile(instr_regex)
        for v, vdata in self.V.items():
            if vdata["node_type"] == "lemma":
                if pat.search(vdata["lemma"]) is not None:               
                   ret.append(CwnLemma(v, self))
        return ret

    def find_senses(self, lemma="", definition="", examples=""):
        """Find senses with lemmas, definitions, or examples matching 
        search patterns.
        
        Parameters
        ----------
        lemma : str, optional
            RegEx pattern for searching the lemma of a sense, by default ""
        definition : str, optional
            RegEx pattern for searching the definition of a sense, by default ""
        examples : str, optional
            RegEx pattern for searching the examples of a sense, by default ""
        
        Returns
        -------
        list
            A list of :class:`CwnSense <CwnGraph.cwn_types.CwnSense>` matching 
        """

        lemma_re = re.compile(lemma)
        def_re = re.compile(definition)
        ex_re = re.compile(examples)

        sense_list = []
        for node_id, node_x in self.V.items():
            if not node_x["node_type"] == "sense":
                continue
            sense_x = CwnSense(node_id, self)            
            if lemma:
                lemma_matched = any(lemma_re.search(lemma_x.lemma) 
                    for lemma_x in sense_x.lemmas)
            else:
                lemma_matched = False
            
            if definition:
                def_matched = def_re.search(sense_x.definition)
            else:
                def_matched = False
            
            if examples:
                ex_san_re = re.compile(r"[\<\>]")
                example_matched = any([ex_re.search(ex_san_re.sub("", ex_x))
                    for ex_x in sense_x.examples])
            else:
                example_matched = False

            if lemma_matched or def_matched or \
                example_matched:
                sense_list.append(sense_x)                
        return sense_list            
            
    def find_edges(self, node_id, is_directed = True):
        ret = []
        
        for e in self.edge_src_index.get(node_id, []):  
            ret.append(CwnRelation(e, self))            
        if not is_directed:
            for e in self.edge_tgt_index.get(node_id, []):
                ret.append(CwnRelation(e, self, reversed=True))   

        return ret
    
    def connected(self, node_id, is_directed = True, maxConn=100, sense_only=True):
        ret = []
        visited = set()
        buf = [node_id]
        while buf:
            node_x = buf.pop()
            visited.add(node_x)
            conn_edges = self.find_edges(node_x, is_directed)            
            for conn_edge_x in conn_edges:
                conn_node_x = conn_edge_x[0]
                conn_rel = conn_edge_x[1]
                if sense_only and "has_sense" in conn_rel:
                    continue

                if conn_node_x in visited or conn_node_x in buf:
                    continue
                else:
                    buf.append(conn_node_x)
                ret.append((node_x, conn_rel, conn_node_x))
            if maxConn and len(ret) > maxConn:
                break                        
        return ret       

    def has_id(self, node_id):
        return node_id in self.V or node_id in self.E
        
    def get_node_data(self, node_id, field_name = None):
        return self.V.get(node_id, {})

    def get_edge_data(self, edge_id, field_name = None):
        return self.E.get(edge_id, {})
        
    def from_sense_id(self, sense_id):
        return CwnSense(sense_id, self)


