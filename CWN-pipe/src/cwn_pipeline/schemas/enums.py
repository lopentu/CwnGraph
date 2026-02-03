"""Enum definitions for CWN data types."""

from enum import Enum


class NodeType(str, Enum):
    """CWN node types."""

    LEMMA = "lemma"
    SENSE = "sense"
    FACET = "facet"
    SYNSET = "synset"
    PWN_SYNSET = "pwn_synset"


class RelationType(str, Enum):
    """CWN relation types."""

    # Structural relations
    HAS_SENSE = "has_sense"
    HAS_LEMMA = "has_lemma"
    HAS_FACET = "has_facet"
    IS_SYNSET = "is_synset"
    HAS_SYNSET = "has_synset"

    # Semantic relations - hierarchical
    HYPERNYM = "hypernym"  # 上位詞
    HYPONYM = "hyponym"  # 下位詞
    HOLONYM = "holonym"  # 整體詞
    MERONYM = "meronym"  # 部分詞
    INSTANCE_OF = "instance_of"  # 是...的事例
    HAS_INSTANCE = "has_instance"  # 有事例

    # Semantic relations - similarity
    SYNONYM = "synonym"  # 同義詞
    NEARSYNONYM = "nearsynonym"  # 近義詞
    ANTONYM = "antonym"  # 反義詞
    PARANYM = "paranym"  # 類義詞
    VARIANT = "variant"  # 異體
    VARWORD = "varword"  # 異體詞

    @classmethod
    def semantic_relations(cls) -> list["RelationType"]:
        """Return list of semantic relation types."""
        return [
            cls.HYPERNYM,
            cls.HYPONYM,
            cls.HOLONYM,
            cls.MERONYM,
            cls.INSTANCE_OF,
            cls.HAS_INSTANCE,
            cls.SYNONYM,
            cls.NEARSYNONYM,
            cls.ANTONYM,
            cls.PARANYM,
            cls.VARIANT,
            cls.VARWORD,
        ]

    @classmethod
    def structural_relations(cls) -> list["RelationType"]:
        """Return list of structural relation types."""
        return [
            cls.HAS_SENSE,
            cls.HAS_LEMMA,
            cls.HAS_FACET,
            cls.IS_SYNSET,
            cls.HAS_SYNSET,
        ]

    @classmethod
    def from_chinese(cls, label: str) -> "RelationType":
        """Convert Chinese label to RelationType."""
        mapping = {
            "上位詞": cls.HYPERNYM,
            "下位詞": cls.HYPONYM,
            "整體詞": cls.HOLONYM,
            "全體詞": cls.HOLONYM,
            "部分詞": cls.MERONYM,
            "同義詞": cls.SYNONYM,
            "近義詞": cls.NEARSYNONYM,
            "反義詞": cls.ANTONYM,
            "類義詞": cls.PARANYM,
            "異體": cls.VARIANT,
            "異體詞": cls.VARWORD,
            "事例": cls.HAS_INSTANCE,
            "之事例": cls.INSTANCE_OF,
        }
        if label not in mapping:
            raise ValueError(f"Unknown Chinese relation label: {label}")
        return mapping[label]


class PosTag(str, Enum):
    """CWN part-of-speech tags (based on CKIP POS)."""

    # Nouns
    Na = "Na"  # 普通名詞
    Nb = "Nb"  # 專有名詞
    Nc = "Nc"  # 地方名詞
    Ncd = "Ncd"  # 位置名詞
    Nd = "Nd"  # 時間名詞
    Nf = "Nf"  # 量詞
    Ng = "Ng"  # 後置詞
    Nh = "Nh"  # 代名詞

    # Verbs
    VA = "VA"  # 動作不及物動詞
    VAC = "VAC"  # 動作使動動詞
    VB = "VB"  # 動作類及物動詞
    VC = "VC"  # 動作及物動詞
    VCL = "VCL"  # 動作接地方賓語動詞
    VD = "VD"  # 雙賓動詞
    VE = "VE"  # 動作句賓動詞
    VF = "VF"  # 動作謂賓動詞
    VG = "VG"  # 分類動詞
    VH = "VH"  # 狀態不及物動詞
    VHC = "VHC"  # 狀態使動動詞
    VI = "VI"  # 狀態類及物動詞
    VJ = "VJ"  # 狀態及物動詞
    VK = "VK"  # 狀態句賓動詞
    VL = "VL"  # 狀態謂賓動詞
    V_2 = "V_2"  # 有

    # Adjectives
    A = "A"  # 非謂形容詞

    # Adverbs
    D = "D"  # 副詞

    # Determiners
    Neqa = "Neqa"  # 數詞定詞
    Neqb = "Neqb"  # 數詞後置定詞
    Nes = "Nes"  # 特指定詞
    Neu = "Neu"  # 數詞

    # Conjunctions
    Caa = "Caa"  # 對等連接詞
    Cab = "Cab"  # 連接詞
    Cba = "Cba"  # 連接詞
    Cbb = "Cbb"  # 關聯連接詞

    # Prepositions
    P = "P"  # 介詞

    # Particles
    T = "T"  # 語助詞

    # Interjections
    I = "I"  # 感嘆詞

    # Others
    DE = "DE"  # 的之得地
    SHI = "SHI"  # 是
    FW = "FW"  # 外文

    @classmethod
    def noun_tags(cls) -> list["PosTag"]:
        """Return all noun POS tags."""
        return [cls.Na, cls.Nb, cls.Nc, cls.Ncd, cls.Nd, cls.Nf, cls.Ng, cls.Nh]

    @classmethod
    def verb_tags(cls) -> list["PosTag"]:
        """Return all verb POS tags."""
        return [
            cls.VA,
            cls.VAC,
            cls.VB,
            cls.VC,
            cls.VCL,
            cls.VD,
            cls.VE,
            cls.VF,
            cls.VG,
            cls.VH,
            cls.VHC,
            cls.VI,
            cls.VJ,
            cls.VK,
            cls.VL,
            cls.V_2,
        ]
