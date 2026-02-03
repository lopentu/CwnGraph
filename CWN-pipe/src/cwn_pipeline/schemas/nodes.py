"""Node schema definitions for CWN data."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LemmaRecord(BaseModel):
    """Schema for lemma records.

    Lemma ID format: 6 digits (e.g., '006136')
    """

    lemma_id: str = Field(..., description="Unique lemma identifier (6 digits)")
    lemma: str = Field(..., description="The word/term")
    zhuyin: str = Field(default="", description="Zhuyin (Bopomofo) pronunciation")
    lemma_sno: int = Field(default=1, description="Lemma serial number for homographs")

    @field_validator("lemma_id")
    @classmethod
    def validate_lemma_id(cls, v: str) -> str:
        """Validate lemma ID format."""
        v = str(v).strip()
        if not v.isdigit():
            raise ValueError(f"lemma_id must be numeric, got: {v}")
        if len(v) < 6:
            v = v.zfill(6)
        if len(v) != 6:
            raise ValueError(f"lemma_id must be 6 digits, got: {v}")
        return v

    @field_validator("lemma")
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        """Validate lemma is not empty."""
        v = str(v).strip()
        if not v:
            raise ValueError("lemma cannot be empty")
        return v

    def to_node_data(self) -> dict:
        """Convert to CwnGraph node data format."""
        return {
            "node_type": "lemma",
            "lemma": self.lemma,
            "zhuyin": self.zhuyin,
            "lemma_sno": self.lemma_sno,
        }


class SenseRecord(BaseModel):
    """Schema for sense records.

    Sense ID format: 8 digits (e.g., '06613601')
    The first 6 digits correspond to the lemma ID.
    """

    sense_id: str = Field(..., description="Unique sense identifier (8 digits)")
    lemma_id: str = Field(..., description="Parent lemma ID (6 digits)")
    pos: str = Field(..., description="Part-of-speech tag")
    definition: str = Field(..., description="Sense definition")
    examples: list[str] = Field(default_factory=list, description="Example sentences")
    domain: str = Field(default="", description="Semantic domain")
    supplementary: str = Field(default="", description="Supplementary notes")

    @field_validator("sense_id")
    @classmethod
    def validate_sense_id(cls, v: str) -> str:
        """Validate sense ID format."""
        v = str(v).strip()
        if not v.isdigit():
            raise ValueError(f"sense_id must be numeric, got: {v}")
        if len(v) < 8:
            v = v.zfill(8)
        if len(v) != 8:
            raise ValueError(f"sense_id must be 8 digits, got: {v}")
        return v

    @field_validator("lemma_id")
    @classmethod
    def validate_lemma_id(cls, v: str) -> str:
        """Validate lemma ID format."""
        v = str(v).strip()
        if not v.isdigit():
            raise ValueError(f"lemma_id must be numeric, got: {v}")
        if len(v) < 6:
            v = v.zfill(6)
        return v

    @field_validator("definition")
    @classmethod
    def validate_definition(cls, v: str) -> str:
        """Validate definition is not empty."""
        v = str(v).strip()
        if not v:
            raise ValueError("definition cannot be empty")
        return v

    @field_validator("examples", mode="before")
    @classmethod
    def parse_examples(cls, v) -> list[str]:
        """Parse examples from string or list."""
        if isinstance(v, str):
            if not v.strip():
                return []
            # Support both | and ; as delimiters
            return [ex.strip() for ex in v.replace(";", "|").split("|") if ex.strip()]
        if isinstance(v, list):
            return [str(ex).strip() for ex in v if str(ex).strip()]
        return []

    def to_node_data(self) -> dict:
        """Convert to CwnGraph node data format."""
        return {
            "node_type": "sense",
            "pos": self.pos,
            "def": self.definition,
            "examples": self.examples,
            "domain": self.domain,
            "supplementary": self.supplementary,
        }


class FacetRecord(BaseModel):
    """Schema for facet records.

    Facet ID format: 10 digits (e.g., '0661360101')
    The first 8 digits correspond to the sense ID.
    """

    facet_id: str = Field(..., description="Unique facet identifier (10 digits)")
    sense_id: str = Field(..., description="Parent sense ID (8 digits)")
    pos: str = Field(default="", description="Part-of-speech tag (optional)")
    definition: str = Field(..., description="Facet definition")
    examples: list[str] = Field(default_factory=list, description="Example sentences")

    @field_validator("facet_id")
    @classmethod
    def validate_facet_id(cls, v: str) -> str:
        """Validate facet ID format."""
        v = str(v).strip()
        if not v.isdigit():
            raise ValueError(f"facet_id must be numeric, got: {v}")
        if len(v) < 10:
            v = v.zfill(10)
        if len(v) != 10:
            raise ValueError(f"facet_id must be 10 digits, got: {v}")
        return v

    @field_validator("sense_id")
    @classmethod
    def validate_sense_id(cls, v: str) -> str:
        """Validate sense ID format."""
        v = str(v).strip()
        if not v.isdigit():
            raise ValueError(f"sense_id must be numeric, got: {v}")
        if len(v) < 8:
            v = v.zfill(8)
        return v

    @field_validator("examples", mode="before")
    @classmethod
    def parse_examples(cls, v) -> list[str]:
        """Parse examples from string or list."""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [ex.strip() for ex in v.replace(";", "|").split("|") if ex.strip()]
        if isinstance(v, list):
            return [str(ex).strip() for ex in v if str(ex).strip()]
        return []

    def to_node_data(self) -> dict:
        """Convert to CwnGraph node data format."""
        return {
            "node_type": "facet",
            "pos": self.pos,
            "def": self.definition,
            "examples": self.examples,
        }


class SynsetRecord(BaseModel):
    """Schema for synset records.

    Synset ID format: syn_XXXXXX (e.g., 'syn_004128')
    """

    synset_id: str = Field(..., description="Unique synset identifier")
    gloss: str = Field(..., description="Synset gloss/definition")
    pos: str = Field(default="", description="Part-of-speech tag")
    examples: list[str] = Field(default_factory=list, description="Example sentences")
    pwn_word: str = Field(default="", description="Princeton WordNet word mapping")
    pwn_id: str = Field(default="", description="Princeton WordNet synset ID")

    @field_validator("synset_id")
    @classmethod
    def validate_synset_id(cls, v: str) -> str:
        """Validate synset ID format."""
        v = str(v).strip()
        if not v.startswith("syn_"):
            v = f"syn_{v.zfill(6)}"
        return v

    @field_validator("gloss")
    @classmethod
    def validate_gloss(cls, v: str) -> str:
        """Validate gloss is not empty."""
        v = str(v).strip()
        if not v:
            raise ValueError("gloss cannot be empty")
        return v

    @field_validator("examples", mode="before")
    @classmethod
    def parse_examples(cls, v) -> list[str]:
        """Parse examples from string or list."""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [ex.strip() for ex in v.replace(";", "|").split("|") if ex.strip()]
        if isinstance(v, list):
            return [str(ex).strip() for ex in v if str(ex).strip()]
        return []

    def to_node_data(self) -> dict:
        """Convert to CwnGraph node data format."""
        return {
            "node_type": "synset",
            "gloss": self.gloss,
            "pos": self.pos,
            "examples": self.examples,
            "pwn_word": self.pwn_word,
            "pwn_id": self.pwn_id,
        }
