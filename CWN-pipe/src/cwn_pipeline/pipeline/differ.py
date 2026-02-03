"""Diff calculator for CWN data updates."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cwn_pipeline.pipeline.loader import LoadResult


class ChangeType(str, Enum):
    """Type of change detected."""

    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"


@dataclass
class Change:
    """Represents a single change to the data."""

    change_type: ChangeType
    entity_type: str  # lemma, sense, facet, synset, relation
    entity_id: str
    old_data: dict | None = None
    new_data: dict | None = None

    def describe(self) -> str:
        """Return human-readable description of the change."""
        if self.change_type == ChangeType.ADD:
            return f"[ADD] {self.entity_type} {self.entity_id}"
        elif self.change_type == ChangeType.MODIFY:
            return f"[MODIFY] {self.entity_type} {self.entity_id}"
        elif self.change_type == ChangeType.DELETE:
            return f"[DELETE] {self.entity_type} {self.entity_id}"
        return f"[{self.change_type}] {self.entity_type} {self.entity_id}"


@dataclass
class DiffResult:
    """Result of comparing existing and new data."""

    changes: list[Change] = field(default_factory=list)

    @property
    def additions(self) -> list[Change]:
        return [c for c in self.changes if c.change_type == ChangeType.ADD]

    @property
    def modifications(self) -> list[Change]:
        return [c for c in self.changes if c.change_type == ChangeType.MODIFY]

    @property
    def deletions(self) -> list[Change]:
        return [c for c in self.changes if c.change_type == ChangeType.DELETE]

    def summary(self) -> dict:
        """Return summary of changes."""
        by_entity = {}
        for change in self.changes:
            key = f"{change.entity_type}_{change.change_type.value}"
            by_entity[key] = by_entity.get(key, 0) + 1

        return {
            "total_changes": len(self.changes),
            "additions": len(self.additions),
            "modifications": len(self.modifications),
            "deletions": len(self.deletions),
            "by_entity_type": by_entity,
        }

    def has_changes(self) -> bool:
        return len(self.changes) > 0


class CwnDiffer:
    """Calculate differences between existing and new CWN data."""

    def __init__(self, existing_data: tuple[dict, dict, dict]):
        """Initialize differ with existing data.

        Args:
            existing_data: (V, E, meta) tuple from existing CwnGraph image.
        """
        self.existing_V = existing_data[0]
        self.existing_E = existing_data[1]
        self.existing_meta = existing_data[2]

    def diff(self, new_data: LoadResult, detect_deletions: bool = False) -> DiffResult:
        """Calculate differences between existing and new data.

        Args:
            new_data: LoadResult from CsvLoader.
            detect_deletions: If True, detect nodes in existing but not in new data.
                             Use with caution for incremental updates.

        Returns:
            DiffResult containing all detected changes.
        """
        result = DiffResult()

        # Diff lemmas
        self._diff_lemmas(new_data, result, detect_deletions)

        # Diff senses
        self._diff_senses(new_data, result, detect_deletions)

        # Diff facets
        self._diff_facets(new_data, result, detect_deletions)

        # Diff synsets
        self._diff_synsets(new_data, result, detect_deletions)

        # Diff relations
        self._diff_relations(new_data, result, detect_deletions)

        return result

    def _diff_lemmas(
        self, new_data: LoadResult, result: DiffResult, detect_deletions: bool
    ):
        """Calculate lemma differences."""
        new_lemma_ids = {r.lemma_id for r in new_data.lemmas}
        existing_lemma_ids = {
            nid
            for nid, ndata in self.existing_V.items()
            if ndata.get("node_type") == "lemma"
        }

        for lemma in new_data.lemmas:
            if lemma.lemma_id in existing_lemma_ids:
                # Check for modifications
                old_data = self.existing_V[lemma.lemma_id]
                new_node_data = lemma.to_node_data()
                if self._has_changes(old_data, new_node_data):
                    result.changes.append(
                        Change(
                            change_type=ChangeType.MODIFY,
                            entity_type="lemma",
                            entity_id=lemma.lemma_id,
                            old_data=old_data,
                            new_data=new_node_data,
                        )
                    )
            else:
                # New lemma
                result.changes.append(
                    Change(
                        change_type=ChangeType.ADD,
                        entity_type="lemma",
                        entity_id=lemma.lemma_id,
                        new_data=lemma.to_node_data(),
                    )
                )

        if detect_deletions:
            for lemma_id in existing_lemma_ids - new_lemma_ids:
                result.changes.append(
                    Change(
                        change_type=ChangeType.DELETE,
                        entity_type="lemma",
                        entity_id=lemma_id,
                        old_data=self.existing_V[lemma_id],
                    )
                )

    def _diff_senses(
        self, new_data: LoadResult, result: DiffResult, detect_deletions: bool
    ):
        """Calculate sense differences."""
        new_sense_ids = {r.sense_id for r in new_data.senses}
        existing_sense_ids = {
            nid
            for nid, ndata in self.existing_V.items()
            if ndata.get("node_type") == "sense"
        }

        for sense in new_data.senses:
            if sense.sense_id in existing_sense_ids:
                old_data = self.existing_V[sense.sense_id]
                new_node_data = sense.to_node_data()
                if self._has_changes(old_data, new_node_data):
                    result.changes.append(
                        Change(
                            change_type=ChangeType.MODIFY,
                            entity_type="sense",
                            entity_id=sense.sense_id,
                            old_data=old_data,
                            new_data=new_node_data,
                        )
                    )
            else:
                result.changes.append(
                    Change(
                        change_type=ChangeType.ADD,
                        entity_type="sense",
                        entity_id=sense.sense_id,
                        new_data=sense.to_node_data(),
                    )
                )

        if detect_deletions:
            for sense_id in existing_sense_ids - new_sense_ids:
                result.changes.append(
                    Change(
                        change_type=ChangeType.DELETE,
                        entity_type="sense",
                        entity_id=sense_id,
                        old_data=self.existing_V[sense_id],
                    )
                )

    def _diff_facets(
        self, new_data: LoadResult, result: DiffResult, detect_deletions: bool
    ):
        """Calculate facet differences."""
        new_facet_ids = {r.facet_id for r in new_data.facets}
        existing_facet_ids = {
            nid
            for nid, ndata in self.existing_V.items()
            if ndata.get("node_type") == "facet"
        }

        for facet in new_data.facets:
            if facet.facet_id in existing_facet_ids:
                old_data = self.existing_V[facet.facet_id]
                new_node_data = facet.to_node_data()
                if self._has_changes(old_data, new_node_data):
                    result.changes.append(
                        Change(
                            change_type=ChangeType.MODIFY,
                            entity_type="facet",
                            entity_id=facet.facet_id,
                            old_data=old_data,
                            new_data=new_node_data,
                        )
                    )
            else:
                result.changes.append(
                    Change(
                        change_type=ChangeType.ADD,
                        entity_type="facet",
                        entity_id=facet.facet_id,
                        new_data=facet.to_node_data(),
                    )
                )

        if detect_deletions:
            for facet_id in existing_facet_ids - new_facet_ids:
                result.changes.append(
                    Change(
                        change_type=ChangeType.DELETE,
                        entity_type="facet",
                        entity_id=facet_id,
                        old_data=self.existing_V[facet_id],
                    )
                )

    def _diff_synsets(
        self, new_data: LoadResult, result: DiffResult, detect_deletions: bool
    ):
        """Calculate synset differences."""
        new_synset_ids = {r.synset_id for r in new_data.synsets}
        existing_synset_ids = {
            nid
            for nid, ndata in self.existing_V.items()
            if ndata.get("node_type") == "synset"
        }

        for synset in new_data.synsets:
            if synset.synset_id in existing_synset_ids:
                old_data = self.existing_V[synset.synset_id]
                new_node_data = synset.to_node_data()
                if self._has_changes(old_data, new_node_data):
                    result.changes.append(
                        Change(
                            change_type=ChangeType.MODIFY,
                            entity_type="synset",
                            entity_id=synset.synset_id,
                            old_data=old_data,
                            new_data=new_node_data,
                        )
                    )
            else:
                result.changes.append(
                    Change(
                        change_type=ChangeType.ADD,
                        entity_type="synset",
                        entity_id=synset.synset_id,
                        new_data=synset.to_node_data(),
                    )
                )

        if detect_deletions:
            for synset_id in existing_synset_ids - new_synset_ids:
                result.changes.append(
                    Change(
                        change_type=ChangeType.DELETE,
                        entity_type="synset",
                        entity_id=synset_id,
                        old_data=self.existing_V[synset_id],
                    )
                )

    def _diff_relations(
        self, new_data: LoadResult, result: DiffResult, detect_deletions: bool
    ):
        """Calculate relation differences."""
        new_edge_keys = {r.edge_key for r in new_data.relations}
        existing_edge_keys = set(self.existing_E.keys())

        for relation in new_data.relations:
            edge_key = relation.edge_key
            if edge_key in existing_edge_keys:
                old_data = self.existing_E[edge_key]
                new_edge_data = relation.to_edge_data()
                if self._has_changes(old_data, new_edge_data):
                    result.changes.append(
                        Change(
                            change_type=ChangeType.MODIFY,
                            entity_type="relation",
                            entity_id=f"{edge_key[0]}->{edge_key[1]}",
                            old_data=old_data,
                            new_data=new_edge_data,
                        )
                    )
            else:
                result.changes.append(
                    Change(
                        change_type=ChangeType.ADD,
                        entity_type="relation",
                        entity_id=f"{edge_key[0]}->{edge_key[1]}",
                        new_data=relation.to_edge_data(),
                    )
                )

        if detect_deletions:
            for edge_key in existing_edge_keys - new_edge_keys:
                result.changes.append(
                    Change(
                        change_type=ChangeType.DELETE,
                        entity_type="relation",
                        entity_id=f"{edge_key[0]}->{edge_key[1]}",
                        old_data=self.existing_E[edge_key],
                    )
                )

    def _has_changes(self, old_data: dict, new_data: dict) -> bool:
        """Check if there are meaningful changes between old and new data."""
        # Compare relevant fields (ignore internal fields)
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                return True
        return False
