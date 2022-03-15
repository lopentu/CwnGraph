from enum import Enum, auto
from .cwn_relation_types import CwnRelationType
from collections import namedtuple
from typing import List
#pylint: disable=import-error
from nltk.corpus import wordnet as wn

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

class CwnGlyph(CwnNode):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.glyph = ndata.get("glyph", "")        

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

class CwnLemma(CwnNode):
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
        self._senses = None
        self._synsets = None
        

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
        data_fields = ["node_type", "lemma", "lemma_sno", "zhuyin"]
        return {
            k: self.__dict__[k] for k in data_fields
        }

    @classmethod
    def create(cls, cgu, 
            lemma_id, lemma: str, zhuyin: str, 
            lemma_sno: int=1,
            auto_pad_id=True):
        
        if isinstance(lemma_id, int):
            lemma_id = str(lemma_id)

        if len(lemma_id) < 6 and auto_pad_id:
            lemma_id = lemma_id.zfill(6)
            print("WARNING: lemma_id should have 6 digits. autopad zero as auto_pad_id=True")

        inst = CwnLemma(lemma_id, cgu)
        inst.lemma = lemma
        inst.zhuyin = zhuyin
        inst.lemma_sno = lemma_sno
        return inst

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

    @property
    def synsets(self):
        if self._synsets is None:
            cgu = self.cgu
            synset_nodes = []
            edges = cgu.find_edges(self.id)
            for edge_x in edges:
                if edge_x.edge_type == "has_synset":
                    synset_nodes.append(CwnSynset(edge_x.tgt_id, cgu))
            self._senses = synset_nodes
        return self._synsets


class CwnSense(CwnNode):
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
        self._relations = None
        self._lemmas = None

    def __repr__(self):
        try:
            head_word = self.lemmas[0].lemma            
        except (IndexError, AttributeError):
            head_word = "----"
        return "<CwnSense[{id}]({head}，{pos}): {definition}>".format(
            head=head_word, **self.__dict__            
        )

    def __eq__(self, other):
        if isinstance(other, CwnSense):
            return self.id == other.id and \
                self.definition == other.definition and \
                self.pos == other.pos and \
                self.src == other.src
        else:
            return False

    def __hash__(self):
        return hash((self.id, self.definition, self.pos, self.src))

    @classmethod
    def create(cls, cgu, 
            sense_id: str, pos: str, definition: str, 
            examples: List[str]=[], domain: str="", 
            auto_pad_id=True):
        
        if isinstance(sense_id, int):
            sense_id = str(sense_id)

        if len(sense_id) < 8 and auto_pad_id:
            sense_id = sense_id.zfill(8)
            print("WARNING: sense_id should have 8 digits. autopad zero as auto_pad_id=True")

        inst = CwnSense(sense_id, cgu)
        inst.pos = pos
        inst.definition = definition
        inst.examples = examples
        inst.domain = domain
        return inst

    def data(self):
        """Retrieve all data of this sense.
        
        Returns
        -------
        dict
            data stored in a dictionary, including the following
            keys: ``node_type``, ``pos``, ``examples``, ``domain``,
            ``annot``, ``def``
        """
        data_fields = ["node_type", "pos", "examples", "domain"]
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
        examples = [x for x in self.examples if x]
        
        
        for facet_x in self.facets:
            examples.extend(facet_x.examples)
        return examples

    def all_relations(self):
        """Retrieve all relations in this sense, 
        including relations links of sense facets.
        
        Returns
        -------
        list
            a list of relation tuples (``Tuple[str, CwnSense, str]``)
        """
        relations = self.relations
        if not relations:
            relations = []        
        
        for facet_x in self.facets:
            relations.extend(facet_x.relations)
        return relations

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
    def head_word(self):
        lemmas = self.lemmas
        if lemmas:
            return lemmas[0].lemma
        else:
            return ""

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
                elif ntype == "synset":
                    end_node = CwnSynset(end_node_id, cgu)
                elif ntype == "pwn_synset":
                    end_node = PwnSynset(end_node_id, cgu)
                else:
                    end_node = CwnSense(end_node_id, cgu)

                relation_infos.append((edge_type, end_node, edge_direction))

            self._relations = relation_infos
        return self._relations

    @property
    def semantic_relations(self):
        relation_infos = [rel_x 
            for rel_x in self.relations
            if rel_x[2] == 'forward']
            
        sem_relations = []
        for rel_x in relation_infos:
            rel_type = CwnRelationType[rel_x[0]]
            if rel_type.is_semantic_relation():
                sem_relations.append(rel_x)
        return sem_relations

    @property
    def hypernym(self):
        relation_infos = self.relations
        hypernym = [x[1] for x in relation_infos if x[0] == "hypernym" and x[2] == "forward"]
        return hypernym
    
    @property
    def hyponym(self):
        relation_infos = self.relations
        hypernym = [x[1] for x in relation_infos if x[0] == "hyponym" and x[2] == "forward"]
        return hypernym

    @property
    def pwn_synsets(self):
        relation_infos = self.relations
        pwn_synsets = [(x[0], x[1]) for x in relation_infos if x[1].node_type=="pwn_synset"]
        return pwn_synsets

    @property
    def synset(self):
        relation_infos = self.relations
        synsets = [x[1] for x in relation_infos if x[0] == "is_synset" and x[2] == "forward"]
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
        synonyms = [x[1] for x in relation_infos 
                    if x[0] == "synonym" and x[2]=="forward"]
        return synonyms

    @property
    def facets(self):
        relation_infos = self.relations
        facets = [x[1] for x in relation_infos if x[0] == "has_facet" and x[2] == "forward"]
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
    def lemmas(self):        
        return self.sense.lemmas

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
        

class CwnSynset(CwnNode):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.node_type = "synset"
        self.pos = ndata.get("pos", "")
        self.gloss = ndata.get("gloss", "")
        self.examples = ndata.get("examples", [])
        self.pwn_word = ndata.get("pwn_word", "")
        self.pwn_id = ndata.get("pwn_id", "")
        self._relations = None

    def __repr__(self):
        return "<CwnSynset[{id}]: {gloss}>".format(
            **self.__dict__
        )

    def data(self):
        data_fields = ["node_type", "pos", "gloss", 
                       "examples", "pwn_word", "pwn_id"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }
        return data_dict

    
    @classmethod
    def create(cls, cgu, 
            synset_id, pos: str, gloss: str, 
            examples: List[str]=[],
            pwn_word: str="", pwn_id: str=""):
        inst = CwnSynset(synset_id, cgu)
        inst.pos = pos
        inst.gloss = gloss
        inst.examples = examples
        inst.pwn_word = pwn_word
        inst.pwn_id = pwn_id        
        return inst

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

class PwnSynset(CwnNode):
    WN_RELATIONS = [
        "hypernyms", "hyponyms", "hypernym_paths",
        "member_holonyms", "member_meronyms",
        "part_holonyms", "part_meronyms",
        "substance_holonyms", "substance_meronyms"
    ]

    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.node_type = "pwn_synset"
        self.synset_word1_wn16 = ndata.get("synset_word1", "")
        self.synset_sno_wn16 = ndata.get("synset_sno", "")  
        self.synset_wn30_name = ndata.get("wn30_name", "")
        try:      
            self.synset_wn30 = wn.synset(ndata.get("wn30_name", ""))
        except:
            self.synset_wn30 = None
        self._relations = None

    def __repr__(self):        
        return "<PwnSynset[{id}]: {synset_wn30_name}>".format(
            **self.__dict__
        )

    def __eq__(self, other):
        if isinstance(other, PwnSynset):
            return self.synset_word1_wn16 == other.synset_word1_wn16
        else:
            return False

    def __hash__(self):
        return hash(self.synset_word1_wn16)

    def __getattr__(self, attr):                  
        if attr in PwnSynset.WN_RELATIONS:             
            if not self.synset_wn30:
                raise AttributeError("attribute not found: " + attr)
            else:                
                rel_method = getattr(self.synset_wn30, attr)                
                return rel_method
        else:
            raise AttributeError("attribute not found: " + attr)

    @property
    def has_wn30(self):
        return bool(self.synset_wn30_name)

    def data(self):
        data_fields = ["node_type"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }
        return data_dict
    
    @property
    def wn30_synset(self):
        try:
            return wn.synset(self.synset_wn30_name)
        except Exception:
            raise ValueError("Cannot find synset or no mapping exists")

    @property
    def relations(self):
        if self._relations is None:
            cgu = self.cgu
            relation_infos = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:               
                
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
    def senses(self):
        relation_infos = self.relations
        senses = [x[1] for x in relation_infos if x[1].node_type=="sense"]
        return senses
    
    @property
    def facets(self):
        relation_infos = self.relations
        senses = [x[1] for x in relation_infos if x[1].node_type=="facet"]
        return senses    
    
    @property
    def cwn_synsets(self):
        relation_infos = self.relations
        senses = [x[1] for x in relation_infos if x[1].node_type=="synset"]
        return senses 