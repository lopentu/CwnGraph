"""Tests for CSV loader."""

import pytest
from pathlib import Path
from cwn_pipeline.pipeline.loader import CsvLoader


class TestCsvLoader:
    """Test CsvLoader functionality."""

    @pytest.fixture
    def loader(self):
        return CsvLoader()

    @pytest.fixture
    def template_dir(self):
        return Path(__file__).parent.parent / "data" / "templates"

    def test_load_lemmas(self, loader, template_dir):
        """Test loading lemmas from CSV."""
        records, errors = loader.load_lemmas(template_dir / "lemmas.csv")

        assert len(errors) == 0
        assert len(records) == 2

        # Check first record
        assert records[0].lemma_id == "006136"
        assert records[0].lemma == "電腦"
        assert records[0].zhuyin == "ㄉㄧㄢˋ ㄋㄠˇ"
        assert records[0].lemma_sno == 1

    def test_load_senses(self, loader, template_dir):
        """Test loading senses from CSV."""
        records, errors = loader.load_senses(template_dir / "senses.csv")

        assert len(errors) == 0
        assert len(records) == 4

        # Check first record
        assert records[0].sense_id == "06613601"
        assert records[0].lemma_id == "006136"
        assert records[0].pos == "Na"
        assert "資料處理裝置" in records[0].definition

    def test_load_directory(self, loader, template_dir):
        """Test loading all files from directory."""
        result = loader.load_directory(template_dir)

        assert len(result.lemmas) == 2
        assert len(result.senses) == 4
        assert len(result.facets) == 2
        assert len(result.synsets) == 1
        assert len(result.relations) == 3
        assert not result.has_errors

    def test_examples_parsing(self, loader, template_dir):
        """Test that examples are parsed correctly."""
        records, _ = loader.load_senses(template_dir / "senses.csv")

        # First sense should have 2 examples
        sense1 = records[0]
        assert len(sense1.examples) == 2
        assert "這台<電腦>的效能很好。" in sense1.examples
