"""Tests for data validator."""

import pytest
from cwn_pipeline.pipeline.loader import CsvLoader, LoadResult
from cwn_pipeline.pipeline.validator import CwnValidator
from cwn_pipeline.schemas.nodes import LemmaRecord, SenseRecord
from cwn_pipeline.schemas.relations import RelationRecord
from cwn_pipeline.schemas.enums import RelationType


class TestCwnValidator:
    """Test CwnValidator functionality."""

    @pytest.fixture
    def validator(self):
        return CwnValidator()

    def test_validate_unique_ids(self, validator):
        """Test detection of duplicate IDs."""
        data = LoadResult()
        data.lemmas = [
            LemmaRecord(lemma_id="000001", lemma="測試"),
            LemmaRecord(lemma_id="000001", lemma="重複"),  # Duplicate
        ]

        result = validator.validate(data)

        assert not result.is_valid
        assert any("Duplicate lemma_id" in e["message"] for e in result.errors)

    def test_validate_referential_integrity(self, validator):
        """Test detection of missing references."""
        data = LoadResult()
        data.lemmas = [
            LemmaRecord(lemma_id="000001", lemma="測試"),
        ]
        data.senses = [
            SenseRecord(
                sense_id="00000101",
                lemma_id="000002",  # Non-existent lemma
                pos="Na",
                definition="測試定義",
            ),
        ]

        result = validator.validate(data)

        assert not result.is_valid
        assert any("non-existent lemma" in e["message"] for e in result.errors)

    def test_validate_relation_nodes(self, validator):
        """Test detection of missing relation endpoints."""
        data = LoadResult()
        data.lemmas = [
            LemmaRecord(lemma_id="000001", lemma="測試"),
        ]
        data.senses = [
            SenseRecord(
                sense_id="00000101",
                lemma_id="000001",
                pos="Na",
                definition="測試定義",
            ),
        ]
        data.relations = [
            RelationRecord(
                src_id="00000101",
                tgt_id="99999999",  # Non-existent target
                edge_type=RelationType.HYPERNYM,
            ),
        ]

        result = validator.validate(data)

        assert not result.is_valid
        assert any("not found" in e["message"] for e in result.errors)

    def test_valid_data(self, validator):
        """Test validation of correct data."""
        data = LoadResult()
        data.lemmas = [
            LemmaRecord(lemma_id="000001", lemma="測試"),
        ]
        data.senses = [
            SenseRecord(
                sense_id="00000101",
                lemma_id="000001",
                pos="Na",
                definition="測試定義",
            ),
        ]

        result = validator.validate(data)

        assert result.is_valid
        assert len(result.errors) == 0
