from enum import Enum, auto
from .cwn_annot_types import CwnAnnotationInfo
from .cwn_relation_types import CwnRelationType
from collections import namedtuple

class CwnNode:
    def __init__(self):
        self.id = None
        self.node_type = None

    def data(self):
        raise NotImplementedError("abstract method: CwnNode.data")

    def __eq__(self, other):
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()

class CwnGlyph(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.glyph = ndata.get("glyph", "")
        self.annot = ndata.get("annot", {})

    def __repr__(self):
        return "<CwnLemma: {lemma}_{lemma_sno}>".format(
            **self.__dict__
        )

    def __eq__(self, other):
        if isinstance(other, CwnGlyph):
            return self.glyph == other.glyph
        else:
            return False

    def __hash__(self):
        return hash(self.glyph)

    def data(self):
        data_fields = ["node_type", "glyph"]
        return {
            k: self.__dict__[k] for k in data_fields
        }

class CwnLemma(CwnAnnotationInfo):
    """Class representing a lemma.

    Attributes
    ----------
    senses: list
        a list of senses (:class:`CwnSense <.CwnSense>`) having this
        lemma
    """
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.node_type = "lemma"
        self.lemma = ndata.get("lemma", "")
        self.lemma_sno = ndata.get("lemma_sno", 1)
        self.zhuyin = ndata.get("zhuyin", "")
        self.annot = ndata.get("annot", {})
        self._senses = None

    def __repr__(self):
        return "<CwnLemma: {lemma}_{lemma_sno}>".format(
            **self.__dict__
        )

    def __eq__(self, other):
        if isinstance(other, CwnLemma):
            return self.lemma == other.lemma and \
                self.zhuyin == other.zhuyin
        else:
            return False

    def __hash__(self):
        return hash((self.lemma, self.zhuyin))

    def data(self):
        """Retrieve all data of this lemma.
        
        Returns
        -------
        dict
            data stored in a dictionary, including the following
            keys: ``node_type``, ``lemma``, ``lemma_sno``, ``zhuyin``,
            ``annot``
        """
        data_fields = ["node_type", "lemma", "lemma_sno", "zhuyin", "annot"]
        return {
            k: self.__dict__[k] for k in data_fields
        }

    @staticmethod
    def from_word(word, cgu):
        """Find lemmas matching search pattern.
        
        Parameters
        ----------
        word : str
            RegEx pattern to search for.
        cgu : CwnBase
            See :class:`CwnBase <CwnGraph.cwn_base.CwnBase>`.
        
        Returns
        -------
        list
            A list of :class:`CwnLemma <.CwnLemma>`.
        """
        return cgu.find_lemma(word)

    @property
    def senses(self):
        if self._senses is None:
            cgu = self.cgu
            sense_nodes = []
            edges = cgu.find_edges(self.id)
            for edge_x in edges:
                if edge_x.edge_type == "has_sense":
                    sense_nodes.append(CwnSense(edge_x.tgt_id, cgu))
            self._senses = sense_nodes
        return self._senses


class CwnSense(CwnAnnotationInfo):
    """Class representing a sense.
    
    Attributes
    ----------
    lemmas: list
        a list of :class:`CwnLemma <.CwnLemma>` belonging to this sense.
    relations: list
        a list of tuples ``(edge_type, end_node, edge_direction)`` 
        giving the information of the edges linked to this sense
    semantic_relations: list
        a list of senses or facets (:class:`CwnSense <.CwnSense>` or 
        :class:`CwnSynset <.CwnSynset>`) related to this sense
    hypernym: list
        a list of hypernyms (:class:`CwnSense <.CwnSense>`) of this
        sense.
    hyponym: list
        a list of hyponym (:class:`CwnSense <.CwnSense>`) of this
        sense.
    synset: list
        a synset (:class:`CwnSynset <.CwnSynset>`) containing this 
        sense.
    synonym: list
        a list of synonyms (:class:`CwnSense <.CwnSense>`) of this
        sense.
    facets: list
        a list of sense facets (:class:`CwnFacet <.CwnFacet>`) 
        belonging to this sense.
    """

    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.pos = ndata.get("pos", "")
        self.node_type = "sense"
        self.definition = ndata.get("def", "")
        self.src = ndata.get("src", None)
        self.examples = ndata.get("examples", [])
        self.domain = ndata.get("domain", "")
        self.annot = ndata.get("annot", {})
        self._relations = None
        self._lemmas = None

    def __repr__(self):
        try:
            head_word = self.lemmas[0].lemma
        except (IndexError, AttributeError):
            head_word = "----"
        return "<CwnSense[{id}]({head}): {definition}>".format(
            head=head_word, **self.__dict__
        )

    def __eq__(self, other):
        if isinstance(other, CwnSense):
            return self.definition == other.definition and \
                self.pos == other.pos and \
                (self.src and other.src and self.src == other.src)
        else:
            return False

    def __hash__(self):
        return hash((self.definition, self.pos, self.src))

    def data(self):
        """Retrieve all data of this sense.
        
        Returns
        -------
        dict
            data stored in a dictionary, including the following
            keys: ``node_type``, ``pos``, ``examples``, ``domain``,
            ``annot``, ``def``
        """
        data_fields = ["node_type", "pos", "examples", "domain", "annot"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }
        data_dict["def"] = self.definition
        return data_dict

    def all_examples(self):
        """Retrieve all example sentences of this sense, 
        including examples inside each sense facet.
        
        Returns
        -------
        list
            a list of example sentences (``str``)
        """
        examples = self.examples
        if not examples:
            examples = []
        if isinstance(examples,str) and\
            examples != '':
            examples = [examples]
        
        
        for facet_x in self.facets:
            examples.extend(facet_x.examples)
        return examples

    @property
    def lemmas(self):
        if self._lemmas is None:
            cgu = self.cgu
            lemma_nodes = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if edge_x.edge_type == "has_sense":
                    lemma_nodes.append(CwnLemma(edge_x.src_id, cgu))
            self._lemmas = lemma_nodes
        return self._lemmas

    @property
    def relations(self):
        if self._relations is None:
            cgu = self.cgu
            relation_infos = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if edge_x.edge_type.startswith("has_sense"):
                    continue                
                
                if not edge_x.reversed:
                    edge_type = edge_x.edge_type
                    end_node_id = edge_x.tgt_id
                    edge_direction = "forward"
                else:
                    edge_type = edge_x.edge_type
                    end_node_id = edge_x.src_id
                    edge_direction = "reversed"
                
                node_data = cgu.get_node_data(end_node_id) 
                if node_data.get("node_type") == "facet":
                    end_node = CwnFacet(end_node_id, cgu) 
                elif node_data.get("node_type") == "synset":
                    end_node = CwnSynset(end_node_id, cgu)
                else:
                    end_node = CwnSense(end_node_id, cgu)

                relation_infos.append((edge_type, end_node, edge_direction))

            self._relations = relation_infos
        return self._relations

    @property
    def semantic_relations(self):
        relation_infos = self.relations
        sem_relations = []
        for rel_x in relation_infos:
            rel_type = CwnRelationType[rel_x[0]]
            if rel_type.is_semantic_relation():
                sem_relations.append(rel_x)
        return sem_relations

    @property
    def hypernym(self):
        relation_infos = self.relations
        hypernym = [x[1] for x in relation_infos if x[0] == "hypernym"]
        return hypernym
    
    @property
    def hyponym(self):
        relation_infos = self.relations
        hypernym = [x[1] for x in relation_infos if x[0] == "hyponym"]
        return hypernym

    @property
    def synset(self):
        relation_infos = self.relations
        synsets = [x[1] for x in relation_infos if x[0] == "is_synset"]
        if not synsets:
            synset = None
        elif len(synsets) == 1:
            synset = synsets[0]
        elif len(synsets) > 1:
            print("WARNING: more than one synset, returning the first")
            synset = synsets[0]
        return synset

    @property
    def synonym(self):
        relation_infos = self.relations
        synonyms = [x[1] for x in relation_infos if x[0] == "synonym"]
        return synonyms

    @property
    def facets(self):
        relation_infos = self.relations
        facets = [x[1] for x in relation_infos if x[0] == "has_facet"]
        return facets

class CwnFacet(CwnSense):
    """Class representing a sense facet.

    Attributes
    ----------
    sense: CwnSense
        the sense (:class:`CwnSense <.CwnSense>`) of this 
        sense facet
    """
    def __init__(self, nid, cgu):
        super(CwnFacet, self).__init__(nid, cgu)
        self.node_type = "facet"
        self._sense = None

    def __repr__(self):
        try:
            head_word = self.sense.lemmas[0].lemma
        except (IndexError, AttributeError):
            head_word = "----"
        return "<CwnFacet[{id}]({head}): {definition}>".format(
            head=head_word, **self.__dict__
        )

    @property
    def sense(self):
        if self._sense is None:
            cgu = self.cgu            
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if edge_x.edge_type == "has_facet":
                    self._sense = CwnSense(edge_x.src_id, cgu)
                    break
        return self._sense
        

class CwnSynset(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.node_type = "synset"
        self.gloss = ndata.get("gloss", "")
        self.pwn_word = ndata.get("pwn_word", "")
        self.pwn_id = ndata.get("pwn_id", "")
        self._relations = None

    def __repr__(self):
        return "<CwnSynset[{id}]: {gloss}>".format(
            **self.__dict__
        )

    def data(self):
        data_fields = ["node_type", "gloss", "pwn_word", "pwn_id"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }
        return data_dict

    def __eq__(self, other):
        if isinstance(other, CwnSynset):
            return self.gloss == other.gloss
        else:
            return False

    def __hash__(self):
        return hash(self.gloss)
    
    @property
    def definition(self):
        return self.gloss

    @property
    def relations(self):
        if self._relations is None:
            cgu = self.cgu
            relation_infos = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if edge_x.edge_type.startswith("has_sense"):
                    continue                
                
                if not edge_x.reversed:
                    edge_type = edge_x.edge_type
                    end_node_id = edge_x.tgt_id  
                    edge_direction = "forward"                  
                else:
                    edge_type = edge_x.edge_type
                    end_node_id = edge_x.src_id
                    edge_direction = "reversed"
                
                node_data = cgu.get_node_data(end_node_id) 
                ntype = node_data.get("node_type")
                if ntype == "facet":
                    end_node = CwnFacet(end_node_id, cgu) 
                elif ntype == "sense":
                    end_node = CwnSense(end_node_id, cgu)
                elif ntype == "synset":
                    end_node = CwnSynset(end_node_id, cgu)
                else:
                    end_node = None

                relation_infos.append((edge_type, end_node, edge_direction))

            self._relations = relation_infos
        return self._relations

    @property
    def semantic_relations(self):
        relation_infos = self.relations
        sem_relations = []
        for rel_x in relation_infos:
            rel_type = CwnRelationType[rel_x[0]]
            if rel_type.is_semantic_relation():
                sem_relations.append(rel_x)
        return sem_relations

    @property
    def senses(self):
        relation_infos = self.relations
        senses = [x[1] for x in relation_infos if x[0].startswith("is_synset")]
        return senses