from enum import Enum, auto
from .cwn_annot_types import CwnAnnotationInfo

class CwnRelationType(Enum):
    holonym = 1
    antonym = 2
    meronym = 3
    hypernym = 4
    hyponym = 5
    variant = 6
    nearsynonym = 7
    paranym = 8
    synonym = 9
    varword = 11
    instance_of = 12
    has_instance = 13        
    generic = -1    
    has_sense = 91
    has_lemma = 92
    has_facet = 93
    is_synset = 94

    def __repr__(self):
        return f"<CwnRelationType: {str(self.name)}>"

    def __eq__(self, other):
        if isinstance(other, CwnRelationType):
            return other.value == self.value
        else:
            return False

    def is_semantic_relation(self):
        return 0 < self.value <= 20

    def inverse(self):
        cls = self.__class__
        inverse_pairs = [
            (cls.has_instance, cls.instance_of),
            (cls.hypernym, cls.hyponym),
            (cls.holonym, cls.meronym)
        ]

        for rel_x, rel_y in inverse_pairs:
            if self == rel_x:
                return rel_y

            if self == rel_y:
                return rel_x
        
        return None

    @staticmethod
    def from_zhLabel(zhlabel):
        label_map = {
            "全體詞": CwnRelationType.holonym,
            "反義詞": CwnRelationType.antonym,
            "部分詞": CwnRelationType.meronym,
            "上位詞": CwnRelationType.hypernym,
            "下位詞": CwnRelationType.hyponym,
            "異體": CwnRelationType.variant,
            "近義詞": CwnRelationType.nearsynonym,
            "類義詞": CwnRelationType.paranym,
            "同義詞": CwnRelationType.synonym,
            "事例": CwnRelationType.has_instance,
            "之事例": CwnRelationType.instance_of,
            "同義詞集": CwnRelationType.is_synset
        }

        return label_map.get(zhlabel, CwnRelationType.generic)


class CwnRelation(CwnAnnotationInfo):
    def __init__(self, eid, cgu, reversed=False):
        edata = cgu.get_edge_data(eid)
        self.cgu = cgu
        self.id = eid
        self.edge_type = edata.get("edge_type", "generic")
        self.annot = {}
        self.reversed = reversed

    def __repr__(self):
        src_id = self.id[0]
        tgt_id = self.id[1]
        if not self.reversed:
            return f"<CwnRelation> {self.edge_type}: {src_id} -> {tgt_id}"
        else:
            return f"<CwnRelation> {self.edge_type}(rev): {tgt_id} <- {src_id}"

    def data(self):
        data_fields = ["edge_type", "annot"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }
        return data_dict

    @property
    def src_id(self):
        return self.id[0]

    @property
    def tgt_id(self):
        return self.id[1]

    @property
    def relation_type(self):
        return self.edge_type

    @relation_type.setter
    def relation_type(self, x):        
        if not isinstance(x, CwnRelationType):
            raise ValueError(f"{x} is not instance of CwnRelationType")
        else:
            self.edge_type = x.name