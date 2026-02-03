"""Export CWN data to various formats."""

import json
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict

from cwn_pipeline.pipeline.transformer import TransformResult


@dataclass
class ExportResult:
    """Result of export operation."""

    files: list[str] = field(default_factory=list)
    success: bool = True
    errors: list[str] = field(default_factory=list)

    def add_file(self, filepath: str):
        """Record an exported file."""
        self.files.append(filepath)

    def add_error(self, error: str):
        """Record an error."""
        self.errors.append(error)
        self.success = False


class CwnExporter:
    """Export CWN data to various formats."""

    def __init__(self, output_dir: str | Path):
        """Initialize exporter.

        Args:
            output_dir: Directory for output files.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_pyobj(
        self,
        data: TransformResult,
        filename: str | None = None,
    ) -> str:
        """Export to CwnGraph pickle format (.pyobj).

        Args:
            data: TransformResult to export.
            filename: Output filename (without extension).

        Returns:
            Path to exported file.
        """
        if filename is None:
            version = data.meta.get("version", "unknown")
            filename = f"cwn-graph-{version}"

        filepath = self.output_dir / f"{filename}.pyobj"

        with open(filepath, "wb") as f:
            pickle.dump((data.V, data.E, data.meta), f)

        return str(filepath)

    def export_json(
        self,
        data: TransformResult,
        filename: str | None = None,
        indent: int = 2,
    ) -> str:
        """Export to JSON format (for debugging/inspection).

        Args:
            data: TransformResult to export.
            filename: Output filename (without extension).
            indent: JSON indentation level.

        Returns:
            Path to exported file.
        """
        if filename is None:
            version = data.meta.get("version", "unknown")
            filename = f"cwn-graph-{version}"

        filepath = self.output_dir / f"{filename}.json"

        export_data = {
            "meta": data.meta,
            "nodes": data.V,
            "edges": {f"{k[0]}->{k[1]}": v for k, v in data.E.items()},
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=indent)

        return str(filepath)

    def export_all(
        self,
        data: TransformResult,
        filename: str | None = None,
    ) -> ExportResult:
        """Export to all supported formats.

        Args:
            data: TransformResult to export.
            filename: Base filename (without extension).

        Returns:
            ExportResult with list of exported files.
        """
        result = ExportResult()

        try:
            pyobj_path = self.export_pyobj(data, filename)
            result.add_file(pyobj_path)
        except Exception as e:
            result.add_error(f"Failed to export pyobj: {e}")

        try:
            json_path = self.export_json(data, filename)
            result.add_file(json_path)
        except Exception as e:
            result.add_error(f"Failed to export JSON: {e}")

        return result


class CwnWebExporter:
    """Export CWN data for CwnWeb (web interface format)."""

    def __init__(self, output_dir: str | Path, num_partitions: int = 50):
        """Initialize web exporter.

        Args:
            output_dir: Directory for output files (cwn_web/).
            num_partitions: Number of data partitions (default 50).
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.num_partitions = num_partitions

    def export(self, data: TransformResult) -> ExportResult:
        """Export data in CwnWeb format.

        Creates:
        - word_map.json: Maps words to partition indices
        - cwn_web_data_N.json: Partitioned word data (N = 0 to num_partitions-1)
        - cwn-pos-label.json: POS tag labels

        Args:
            data: TransformResult to export.

        Returns:
            ExportResult with list of exported files.
        """
        result = ExportResult()

        try:
            # Build word -> senses mapping
            word_data = self._build_word_data(data)

            # Partition data
            partitions, word_map = self._partition_data(word_data)

            # Export word_map.json
            word_map_path = self.output_dir / "word_map.json"
            with open(word_map_path, "w", encoding="utf-8") as f:
                json.dump(word_map, f, ensure_ascii=False)
            result.add_file(str(word_map_path))

            # Export partitioned data files
            for idx, partition in enumerate(partitions):
                filepath = self.output_dir / f"cwn_web_data_{idx}.json"
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(partition, f, ensure_ascii=False, indent=2)
                result.add_file(str(filepath))

            # Export POS labels
            pos_labels_path = self._export_pos_labels()
            result.add_file(pos_labels_path)

        except Exception as e:
            result.add_error(f"Failed to export web format: {e}")

        return result

    def _build_word_data(self, data: TransformResult) -> dict[str, list[dict]]:
        """Build word -> sense data mapping for web format."""
        word_data: dict[str, list[dict]] = defaultdict(list)

        # Get all lemmas
        lemmas = {
            nid: ndata
            for nid, ndata in data.V.items()
            if ndata.get("node_type") == "lemma"
        }

        # Get all senses
        senses = {
            nid: ndata
            for nid, ndata in data.V.items()
            if ndata.get("node_type") == "sense"
        }

        # Build lemma -> senses mapping from edges
        lemma_senses: dict[str, list[str]] = defaultdict(list)
        for (src, tgt), edata in data.E.items():
            if edata.get("edge_type") == "has_sense":
                lemma_senses[src].append(tgt)

        # Build sense relations
        sense_relations: dict[str, dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        for (src, tgt), edata in data.E.items():
            edge_type = edata.get("edge_type", "")
            if edge_type in [
                "hypernym",
                "hyponym",
                "holonym",
                "meronym",
                "synonym",
                "antonym",
                "nearsynonym",
                "paranym",
                "variant",
                "varword",
            ]:
                # Get target word for display
                tgt_lemma = self._get_sense_lemma(tgt, data)
                sense_relations[src][edge_type].append([tgt_lemma, tgt])

        # Build word data structure
        for lemma_id, lemma_data in lemmas.items():
            word = lemma_data.get("lemma", "")
            zhuyin = lemma_data.get("zhuyin", "")

            for sense_id in lemma_senses.get(lemma_id, []):
                sense_data = senses.get(sense_id, {})
                sense_entry = {
                    "lemma": word,
                    "zhuyin": zhuyin,
                    "cwn_id": sense_id,
                    "definition": sense_data.get("def", ""),
                    "pos": sense_data.get("pos", ""),
                    "examples": sense_data.get("examples", []),
                    "relations": dict(sense_relations.get(sense_id, {})),
                }
                word_data[word].append(sense_entry)

        return dict(word_data)

    def _get_sense_lemma(self, sense_id: str, data: TransformResult) -> str:
        """Get the lemma word for a sense ID."""
        for (src, tgt), edata in data.E.items():
            if edata.get("edge_type") == "has_sense" and tgt == sense_id:
                lemma_data = data.V.get(src, {})
                return lemma_data.get("lemma", "")
        return ""

    def _partition_data(
        self, word_data: dict[str, list[dict]]
    ) -> tuple[list[dict], dict[str, int]]:
        """Partition word data into N files.

        Args:
            word_data: Dictionary of word -> sense data.

        Returns:
            Tuple of (list of partition dicts, word -> partition index map).
        """
        words = sorted(word_data.keys())
        partitions: list[dict] = [{} for _ in range(self.num_partitions)]
        word_map: dict[str, int] = {}

        for idx, word in enumerate(words):
            partition_idx = idx % self.num_partitions
            partitions[partition_idx][word] = word_data[word]
            word_map[word] = partition_idx

        return partitions, word_map

    def _export_pos_labels(self) -> str:
        """Export POS tag labels."""
        # Standard CWN POS labels
        pos_labels = {
            "Na": {"pos": "Na", "label": "普通名詞"},
            "Nb": {"pos": "Nb", "label": "專有名詞"},
            "Nc": {"pos": "Nc", "label": "地方名詞"},
            "Ncd": {"pos": "Ncd", "label": "位置名詞"},
            "Nd": {"pos": "Nd", "label": "時間名詞"},
            "Nf": {"pos": "Nf", "label": "量詞"},
            "Ng": {"pos": "Ng", "label": "後置詞"},
            "Nh": {"pos": "Nh", "label": "代名詞"},
            "VA": {"pos": "VA", "label": "動作不及物動詞"},
            "VAC": {"pos": "VAC", "label": "動作使動動詞"},
            "VB": {"pos": "VB", "label": "動作類及物動詞"},
            "VC": {"pos": "VC", "label": "動作及物動詞"},
            "VCL": {"pos": "VCL", "label": "動作接地方賓語動詞"},
            "VD": {"pos": "VD", "label": "雙賓動詞"},
            "VE": {"pos": "VE", "label": "動作句賓動詞"},
            "VF": {"pos": "VF", "label": "動作謂賓動詞"},
            "VG": {"pos": "VG", "label": "分類動詞"},
            "VH": {"pos": "VH", "label": "狀態不及物動詞"},
            "VHC": {"pos": "VHC", "label": "狀態使動動詞"},
            "VI": {"pos": "VI", "label": "狀態類及物動詞"},
            "VJ": {"pos": "VJ", "label": "狀態及物動詞"},
            "VK": {"pos": "VK", "label": "狀態句賓動詞"},
            "VL": {"pos": "VL", "label": "狀態謂賓動詞"},
            "V_2": {"pos": "V_2", "label": "有"},
            "A": {"pos": "A", "label": "非謂形容詞"},
            "D": {"pos": "D", "label": "副詞"},
            "Caa": {"pos": "Caa", "label": "對等連接詞"},
            "Cab": {"pos": "Cab", "label": "連接詞"},
            "Cba": {"pos": "Cba", "label": "連接詞"},
            "Cbb": {"pos": "Cbb", "label": "關聯連接詞"},
            "P": {"pos": "P", "label": "介詞"},
            "T": {"pos": "T", "label": "語助詞"},
            "I": {"pos": "I", "label": "感嘆詞"},
            "DE": {"pos": "DE", "label": "的之得地"},
            "SHI": {"pos": "SHI", "label": "是"},
            "FW": {"pos": "FW", "label": "外文"},
        }

        filepath = self.output_dir / "cwn-pos-label.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(pos_labels, f, ensure_ascii=False, indent=2)

        return str(filepath)
