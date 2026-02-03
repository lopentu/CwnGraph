"""CWN data schemas using Pydantic."""

from cwn_pipeline.schemas.nodes import LemmaRecord, SenseRecord, FacetRecord, SynsetRecord
from cwn_pipeline.schemas.relations import RelationRecord
from cwn_pipeline.schemas.enums import NodeType, RelationType, PosTag

__all__ = [
    "LemmaRecord",
    "SenseRecord",
    "FacetRecord",
    "SynsetRecord",
    "RelationRecord",
    "NodeType",
    "RelationType",
    "PosTag",
]
