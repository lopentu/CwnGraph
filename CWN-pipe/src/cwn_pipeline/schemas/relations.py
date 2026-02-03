"""Relation schema definitions for CWN data."""

from pydantic import BaseModel, Field, field_validator, model_validator
from cwn_pipeline.schemas.enums import RelationType


class RelationRecord(BaseModel):
    """Schema for relation records.

    Represents an edge between two nodes in the CWN graph.
    """

    src_id: str = Field(..., description="Source node ID")
    tgt_id: str = Field(..., description="Target node ID")
    edge_type: RelationType = Field(..., description="Type of relation")

    @field_validator("src_id", "tgt_id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate node ID is not empty."""
        v = str(v).strip()
        if not v:
            raise ValueError("Node ID cannot be empty")
        return v

    @field_validator("edge_type", mode="before")
    @classmethod
    def parse_edge_type(cls, v) -> RelationType:
        """Parse edge type from string or enum."""
        if isinstance(v, RelationType):
            return v
        if isinstance(v, str):
            v = v.strip().lower()
            # Try direct enum lookup
            try:
                return RelationType(v)
            except ValueError:
                pass
            # Try Chinese label conversion
            try:
                return RelationType.from_chinese(v)
            except ValueError:
                pass
            raise ValueError(f"Unknown relation type: {v}")
        raise ValueError(f"Invalid edge_type value: {v}")

    @model_validator(mode="after")
    def validate_no_self_loop(self) -> "RelationRecord":
        """Ensure source and target are different."""
        if self.src_id == self.tgt_id:
            raise ValueError(f"Self-loop detected: {self.src_id} -> {self.tgt_id}")
        return self

    def to_edge_data(self) -> dict:
        """Convert to CwnGraph edge data format."""
        return {
            "edge_type": self.edge_type.value,
        }

    @property
    def edge_key(self) -> tuple[str, str]:
        """Return edge key as (src_id, tgt_id) tuple."""
        return (self.src_id, self.tgt_id)


class LemmaSenseRelation(BaseModel):
    """Schema for lemma-sense structural relations.

    Automatically generated from SenseRecord.
    """

    lemma_id: str
    sense_id: str

    @property
    def edge_type(self) -> RelationType:
        return RelationType.HAS_SENSE

    def to_edge_data(self) -> dict:
        return {"edge_type": self.edge_type.value}

    @property
    def edge_key(self) -> tuple[str, str]:
        return (self.lemma_id, self.sense_id)


class SenseFacetRelation(BaseModel):
    """Schema for sense-facet structural relations.

    Automatically generated from FacetRecord.
    """

    sense_id: str
    facet_id: str

    @property
    def edge_type(self) -> RelationType:
        return RelationType.HAS_FACET

    def to_edge_data(self) -> dict:
        return {"edge_type": self.edge_type.value}

    @property
    def edge_key(self) -> tuple[str, str]:
        return (self.sense_id, self.facet_id)


class SenseSynsetRelation(BaseModel):
    """Schema for sense-synset relations."""

    sense_id: str
    synset_id: str

    @property
    def edge_type(self) -> RelationType:
        return RelationType.IS_SYNSET

    def to_edge_data(self) -> dict:
        return {"edge_type": self.edge_type.value}

    @property
    def edge_key(self) -> tuple[str, str]:
        return (self.sense_id, self.synset_id)
