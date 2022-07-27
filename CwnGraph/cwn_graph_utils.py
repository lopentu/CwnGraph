import pdb
import re
from itertools import chain, groupby
from .cwn_types import *
from .evaluate_wng import evaluate_wngual

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

    def find_all_senses(self, lemma):
        sense_iter = (x.senses for x in self.find_lemma(f"^{lemma}$"))
        sense_iter = chain.from_iterable(sense_iter)
        return list(sense_iter)

    def find_senses(self, lemma="", pos="", definition="", examples=""):
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
        pos_re = re.compile(pos)
        def_re = re.compile(re.escape(definition))
        ex_re = re.compile(re.escape(examples))

        sense_list = []
        for node_id, node_x in self.V.items():
            if not node_x["node_type"] == "sense":
                continue
            sense_x = CwnSense(node_id, self)
            is_matched = True
            if lemma:
                lemma_matched = any(lemma_re.search(lemma_x.lemma)
                    for lemma_x in sense_x.lemmas)
                is_matched &= lemma_matched

            if pos and is_matched:
                pos_matched = pos_re.search(sense_x.pos)
                is_matched &= pos_matched is not None

            if definition and is_matched:
                def_matched = def_re.search(sense_x.definition)
                is_matched &= def_matched is not None

            if examples and is_matched:
                ex_san_re = re.compile(r"[\<\>]")
                example_matched = any([ex_re.search(ex_san_re.sub("", ex_x))
                    for ex_x in sense_x.examples])
                is_matched &= example_matched

            if is_matched:
                sense_list.append(sense_x)
        return sense_list

    def senses(self):
        sense_iter = filter(lambda x: x[1].get("node_type", "") == "sense",
                        self.V.items())
        for sense_id, sense_data in sense_iter:
            try:
                yield CwnSense(sense_id, self)
            except Exception as ex:
                print(ex)

    def find_edges(self, node_id, is_directed=True):
        ret = []

        for e in self.edge_src_index.get(node_id, []):
            ret.append(CwnRelation(e, self))
        if not is_directed:
            for e in self.edge_tgt_index.get(node_id, []):
                ret.append(CwnRelation(e, self, reversed=True))

        return ret

    def subgraph(self, node_ids, meta={}, include_lemma=True, include_synset=True):
        sV = {nid: self.V[nid] for nid in node_ids}
        sE = {eid: self.E[eid] for eid in self.E
              if eid[0] in node_ids and
                 eid[1] in node_ids}
        
        ## make sure all sense node also has its lemma node
        to_add_nodes = {}
        for nid, ndata in sV.items():
            if ndata["node_type"] != "sense":
                continue
            edges = self.find_edges(nid, is_directed=False)
            
            for edge_x in edges:                
                if include_lemma and edge_x.relation_type=="has_sense":
                    lemma_id = edge_x.src_id
                    to_add_nodes[lemma_id] = self.V[lemma_id]
                    sE[(lemma_id, nid)] = self.E[(lemma_id, nid)]

                if include_synset and edge_x.relation_type=="is_synset":
                    synset_id = edge_x.tgt_id
                    to_add_nodes[synset_id] = self.V[synset_id]
                    sE[(nid, synset_id)] = self.E[(nid, synset_id)]                                             
            
        sV.update(to_add_nodes)

        return (sV, sE, {"label": "subgraph", **meta})

    def connected(self, node_id, is_directed=False,
            max_conn=1000, max_depth=-1, lemma_guard=True, 
            include_upper_relations=True,
            include_lower_relations=True,
            include_synonym=True,
            include_facets=False):
        '''
        connected(self, node_id, is_directed=False,
            max_conn=1000, max_depth=-1, lemma_guard=True)
        
        Parameters
        -----------

        lemma_guard: bool
            the (undirected) exploration of new nodes are stopped when seeing a lemma node
        upper_relations_only: bool
            only explore those relations that has `is_upper_relation` is True. Setting this
            arg to True implies is_directed is True.
        '''

        ret = set([node_id])
        visited = set()
        buf = [(node_id, 0)]
        is_directed = is_directed or include_upper_relations or include_lower_relations

        while buf:
            node_x, depth = buf.pop()
            if node_x in visited:
                continue

            conn_edges = self.find_edges(node_x, is_directed)
            for conn_edge_x in conn_edges:
                if conn_edge_x.reversed:
                    conn_node_x = conn_edge_x.src_id
                else:
                    conn_node_x = conn_edge_x.tgt_id
                
                conn_node_type = self.V.get(conn_node_x, {}).get("node_type")
                if conn_node_type=="facet" and not include_facets:
                    continue                    

                rel_type = CwnRelationType[conn_edge_x.relation_type]
                include_relation = rel_type.is_upper_relation() and \
                                    include_upper_relations                                    
                include_relation |= rel_type.is_lower_relation() and \
                                    include_lower_relations
                include_relation |= rel_type.is_synonym_relation() and \
                                    include_synonym
                                
                if include_relation:
                    ret.add(conn_node_x)
                else:
                    # if this relation is not included, 
                    # it will not be further explored
                    continue
                
                # explore the connected edges
                ntype = self.V.get(conn_node_x, {}).get("node_type", "")
                within_depth_limit = max_depth > 0 and depth < max_depth
                is_lemma_guarded = lemma_guard and ntype=="lemma"


                if (within_depth_limit and
                    not is_lemma_guarded):
                    buf.append((conn_node_x, depth+1))
            visited.add(node_x)
            if max_conn and len(ret) > max_conn:
                break
        return ret

    def find_shortest_path(self, src_id, tgt_id, is_directed=True):
        buf = [(src_id, 0)]
        backtrace = {}
        visited = set()
        is_found = False

        while buf:
            nid, depth = buf.pop(0)
            if nid in visited:
                continue
            
            conn_edges = self.find_edges(nid, is_directed)

            for conn_edge_x in conn_edges:
                if conn_edge_x.reversed:
                    conn_node_x = conn_edge_x.src_id
                else:
                    conn_node_x = conn_edge_x.tgt_id

                prev_depth = backtrace.get(conn_node_x, (None, 999))[1]
                if depth < prev_depth:
                    backtrace[conn_node_x] = (nid, depth)

                if conn_node_x == tgt_id:
                    is_found = True
                    break   
                buf.append((conn_node_x, depth+1))

            visited.add(nid)            
                            
        ## backtracking
        trace = []
        if is_found:
            nid = tgt_id
            trace.append(tgt_id)
            while True:
                if nid==src_id:
                    break
                nid = backtrace[nid][0]
                trace.append(nid)                
            trace = trace[::-1]
        return trace

    def has_id(self, node_id):
        return node_id in self.V or node_id in self.E

    def get_node_data(self, node_id):
        return self.V.get(node_id, {})

    def get_edge_data(self, edge_id):
        return self.E.get(edge_id, {})

    def from_sense_id(self, sense_id):
        if len(str(sense_id))<=8:
            return CwnSense(sense_id, self)
        else:
            return CwnFacet(sense_id, self)

    def get_all_lemmas(self):
        lemmas = [CwnLemma(nid, self) for nid, ndata in self.V.items()
                    if ndata["node_type"] == "lemma"]
        lemmas = sorted(lemmas, key=lambda x: (x.lemma, x.lemma_sno or 0))
        lemma_groups = groupby(lemmas, key=lambda x: x.lemma)
        lemma_groups = {grp_key: list(grp_iter)
            for grp_key, grp_iter in lemma_groups if grp_key}
        return lemma_groups

    def get_all_senses(self):
        senses = [CwnSense(nid, self) for nid, ndata in self.V.items()
                    if ndata["node_type"] == "sense"]
        return senses

    def get_all_synsets(self):
        synsets = [CwnSynset(nid, self) for nid, ndata in self.V.items()
                    if ndata["node_type"] == "synset"]
        return synsets

    def evaluate(self, wng_str: str):        
        return evaluate_wngual(self, wng_str)

