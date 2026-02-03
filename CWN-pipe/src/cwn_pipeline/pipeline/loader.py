"""CSV data loader for CWN pipeline."""

from pathlib import Path
from dataclasses import dataclass, field
import pandas as pd
from pydantic import ValidationError

from cwn_pipeline.schemas.nodes import LemmaRecord, SenseRecord, FacetRecord, SynsetRecord
from cwn_pipeline.schemas.relations import RelationRecord


@dataclass
class LoadResult:
    """Result of loading CSV data."""

    lemmas: list[LemmaRecord] = field(default_factory=list)
    senses: list[SenseRecord] = field(default_factory=list)
    facets: list[FacetRecord] = field(default_factory=list)
    synsets: list[SynsetRecord] = field(default_factory=list)
    relations: list[RelationRecord] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def total_records(self) -> int:
        return (
            len(self.lemmas)
            + len(self.senses)
            + len(self.facets)
            + len(self.synsets)
            + len(self.relations)
        )

    def summary(self) -> dict:
        """Return summary statistics."""
        return {
            "lemmas": len(self.lemmas),
            "senses": len(self.senses),
            "facets": len(self.facets),
            "synsets": len(self.synsets),
            "relations": len(self.relations),
            "errors": len(self.errors),
        }


class CsvLoader:
    """Load CWN data from CSV files."""

    # Expected column mappings for each file type
    LEMMA_COLUMNS = {
        "required": ["lemma_id", "lemma"],
        "optional": ["zhuyin", "lemma_sno"],
    }

    SENSE_COLUMNS = {
        "required": ["sense_id", "lemma_id", "pos", "definition"],
        "optional": ["examples", "domain", "supplementary"],
    }

    FACET_COLUMNS = {
        "required": ["facet_id", "sense_id", "definition"],
        "optional": ["pos", "examples"],
    }

    SYNSET_COLUMNS = {
        "required": ["synset_id", "gloss"],
        "optional": ["pos", "examples", "pwn_word", "pwn_id"],
    }

    RELATION_COLUMNS = {
        "required": ["src_id", "tgt_id", "edge_type"],
        "optional": [],
    }

    def __init__(self, encoding: str = "utf-8"):
        """Initialize the loader.

        Args:
            encoding: File encoding for CSV files.
        """
        self.encoding = encoding

    def load_directory(self, dir_path: str | Path) -> LoadResult:
        """Load all CSV files from a directory.

        Expected files:
        - lemmas.csv
        - senses.csv
        - facets.csv (optional)
        - synsets.csv (optional)
        - relations.csv

        Args:
            dir_path: Path to directory containing CSV files.

        Returns:
            LoadResult containing all loaded data.
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")

        result = LoadResult()

        # Load each file type
        file_loaders = [
            ("lemmas.csv", self.load_lemmas),
            ("senses.csv", self.load_senses),
            ("facets.csv", self.load_facets),
            ("synsets.csv", self.load_synsets),
            ("relations.csv", self.load_relations),
        ]

        for filename, loader in file_loaders:
            filepath = dir_path / filename
            if filepath.exists():
                records, errors = loader(filepath)
                # Store results based on type
                if filename == "lemmas.csv":
                    result.lemmas = records
                elif filename == "senses.csv":
                    result.senses = records
                elif filename == "facets.csv":
                    result.facets = records
                elif filename == "synsets.csv":
                    result.synsets = records
                elif filename == "relations.csv":
                    result.relations = records
                result.errors.extend(errors)

        return result

    def _load_csv(self, filepath: Path) -> pd.DataFrame:
        """Load a CSV file into a DataFrame."""
        return pd.read_csv(
            filepath,
            encoding=self.encoding,
            dtype=str,  # Read all as string to preserve IDs
            keep_default_na=False,  # Don't convert empty strings to NaN
        )

    def _validate_columns(
        self, df: pd.DataFrame, required: list[str], filepath: Path
    ) -> list[str]:
        """Check if required columns are present."""
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in {filepath}: {missing}")
        return list(df.columns)

    def load_lemmas(self, filepath: str | Path) -> tuple[list[LemmaRecord], list[dict]]:
        """Load lemmas from CSV file."""
        filepath = Path(filepath)
        df = self._load_csv(filepath)
        self._validate_columns(df, self.LEMMA_COLUMNS["required"], filepath)

        records = []
        errors = []

        for idx, row in df.iterrows():
            try:
                record = LemmaRecord(
                    lemma_id=row["lemma_id"],
                    lemma=row["lemma"],
                    zhuyin=row.get("zhuyin", ""),
                    lemma_sno=int(row.get("lemma_sno", 1) or 1),
                )
                records.append(record)
            except (ValidationError, ValueError) as e:
                errors.append(
                    {
                        "file": str(filepath),
                        "row": idx + 2,  # +2 for 1-indexed and header
                        "data": row.to_dict(),
                        "error": str(e),
                    }
                )

        return records, errors

    def load_senses(self, filepath: str | Path) -> tuple[list[SenseRecord], list[dict]]:
        """Load senses from CSV file."""
        filepath = Path(filepath)
        df = self._load_csv(filepath)
        self._validate_columns(df, self.SENSE_COLUMNS["required"], filepath)

        records = []
        errors = []

        for idx, row in df.iterrows():
            try:
                record = SenseRecord(
                    sense_id=row["sense_id"],
                    lemma_id=row["lemma_id"],
                    pos=row["pos"],
                    definition=row["definition"],
                    examples=row.get("examples", ""),
                    domain=row.get("domain", ""),
                    supplementary=row.get("supplementary", ""),
                )
                records.append(record)
            except (ValidationError, ValueError) as e:
                errors.append(
                    {
                        "file": str(filepath),
                        "row": idx + 2,
                        "data": row.to_dict(),
                        "error": str(e),
                    }
                )

        return records, errors

    def load_facets(self, filepath: str | Path) -> tuple[list[FacetRecord], list[dict]]:
        """Load facets from CSV file."""
        filepath = Path(filepath)
        df = self._load_csv(filepath)
        self._validate_columns(df, self.FACET_COLUMNS["required"], filepath)

        records = []
        errors = []

        for idx, row in df.iterrows():
            try:
                record = FacetRecord(
                    facet_id=row["facet_id"],
                    sense_id=row["sense_id"],
                    pos=row.get("pos", ""),
                    definition=row["definition"],
                    examples=row.get("examples", ""),
                )
                records.append(record)
            except (ValidationError, ValueError) as e:
                errors.append(
                    {
                        "file": str(filepath),
                        "row": idx + 2,
                        "data": row.to_dict(),
                        "error": str(e),
                    }
                )

        return records, errors

    def load_synsets(self, filepath: str | Path) -> tuple[list[SynsetRecord], list[dict]]:
        """Load synsets from CSV file."""
        filepath = Path(filepath)
        df = self._load_csv(filepath)
        self._validate_columns(df, self.SYNSET_COLUMNS["required"], filepath)

        records = []
        errors = []

        for idx, row in df.iterrows():
            try:
                record = SynsetRecord(
                    synset_id=row["synset_id"],
                    gloss=row["gloss"],
                    pos=row.get("pos", ""),
                    examples=row.get("examples", ""),
                    pwn_word=row.get("pwn_word", ""),
                    pwn_id=row.get("pwn_id", ""),
                )
                records.append(record)
            except (ValidationError, ValueError) as e:
                errors.append(
                    {
                        "file": str(filepath),
                        "row": idx + 2,
                        "data": row.to_dict(),
                        "error": str(e),
                    }
                )

        return records, errors

    def load_relations(
        self, filepath: str | Path
    ) -> tuple[list[RelationRecord], list[dict]]:
        """Load relations from CSV file."""
        filepath = Path(filepath)
        df = self._load_csv(filepath)
        self._validate_columns(df, self.RELATION_COLUMNS["required"], filepath)

        records = []
        errors = []

        for idx, row in df.iterrows():
            try:
                record = RelationRecord(
                    src_id=row["src_id"],
                    tgt_id=row["tgt_id"],
                    edge_type=row["edge_type"],
                )
                records.append(record)
            except (ValidationError, ValueError) as e:
                errors.append(
                    {
                        "file": str(filepath),
                        "row": idx + 2,
                        "data": row.to_dict(),
                        "error": str(e),
                    }
                )

        return records, errors
