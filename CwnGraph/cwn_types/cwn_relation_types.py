from enum import Enum, auto


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
    holonym_generic = 21
    holonym_member = 22
    holonym_substance = 23
    meronym_generic = 24
    meronym_member = 25
    meronym_substance = 26
    generic = -1
    has_sense = 91
    has_lemma = 92
    has_facet = 93
    is_synset = 94
    has_synset = 95  # pre-declare for lemma-synset relations

    def __repr__(self):
        return f"<CwnRelationType: {str(self.name)}>"

    def __eq__(self, other):
        if isinstance(other, CwnRelationType):
            return other.value == self.value
        else:
            return False

    def is_semantic_relation(self):
        return 0 < self.value <= 20

    def is_upper_relation(self):
        return self.name in (
            "holonym", "hypernym", "holonym_generic", "holonym_member", "holonym_substance"
        )

    def is_lower_relation(self):
        return self.name in (
            "meronym", "hyponym", "meronym_generic", "meronym_member", "meronym_substance"
        )

    def is_synonym_relation(self):
        return self.name in (
            "synonym", "is_synset", "has_synset"
        )

    def inverse(self):
        cls = self.__class__
        inverse_pairs = [
            (cls.has_instance, cls.instance_of),
            (cls.hypernym, cls.hyponym),
            (cls.holonym, cls.meronym),
            (cls.holonym_generic, cls.meronym_generic),
            (cls.holonym_member, cls.meronym_member),
            (cls.holonym_substance, cls.meronym_substance)
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
            "整體詞": CwnRelationType.holonym,
            "部分詞": CwnRelationType.meronym,
            "整體詞_一般性": CwnRelationType.holonym_generic,
            "整體詞_成員": CwnRelationType.holonym_member,
            "整體詞_成份": CwnRelationType.holonym_substance,
            "部分詞_一般性": CwnRelationType.meronym_generic,
            "部分詞_成員": CwnRelationType.meronym_member,
            "部分詞_成份": CwnRelationType.meronym_substance,
            "反義詞": CwnRelationType.antonym,
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


class CwnRelation:
    def __init__(self, eid, cgu, reversed=False):
        edata = cgu.get_edge_data(eid)
        self.cgu = cgu
        self.id = eid
        self.edge_type = edata.get("edge_type", "generic")
        self.reversed = reversed

    @classmethod
    def create(cls, cgu, src_id, tgt_id, edge_type: CwnRelationType):
        eid = (src_id, tgt_id)
        inst = CwnRelation(eid, cgu)
        inst.edge_type = edge_type.name
        return inst

    def __repr__(self):
        src_id = self.id[0]
        tgt_id = self.id[1]
        if not self.reversed:
            return f"<CwnRelation> {self.edge_type}: {src_id} -> {tgt_id}"
        else:
            return f"<CwnRelation> {self.edge_type}(rev): {tgt_id} <- {src_id}"

    def data(self):
        data_fields = ["edge_type"]
        data_dict = {
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
