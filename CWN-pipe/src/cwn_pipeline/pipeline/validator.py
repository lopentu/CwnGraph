"""Data validator for CWN pipeline."""

from dataclasses import dataclass, field
from cwn_pipeline.pipeline.loader import LoadResult
from cwn_pipeline.schemas.enums import RelationType


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool = True
    errors: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)

    def add_error(self, category: str, message: str, details: dict | None = None):
        """Add a validation error."""
        self.is_valid = False
        self.errors.append(
            {"category": category, "message": message, "details": details or {}}
        )

    def add_warning(self, category: str, message: str, details: dict | None = None):
        """Add a validation warning."""
        self.warnings.append(
            {"category": category, "message": message, "details": details or {}}
        )

    def summary(self) -> dict:
        """Return summary statistics."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


class CwnValidator:
    """Validate CWN data for consistency and integrity."""

    def __init__(self, existing_data: tuple[dict, dict, dict] | None = None):
        """Initialize validator.

        Args:
            existing_data: Optional (V, E, meta) tuple of existing CWN data
                          for referential integrity checks.
        """
        self.existing_V = existing_data[0] if existing_data else {}
        self.existing_E = existing_data[1] if existing_data else {}
        self.existing_meta = existing_data[2] if existing_data else {}

    def validate(self, data: LoadResult) -> ValidationResult:
        """Run all validation checks on loaded data.

        Args:
            data: LoadResult from CsvLoader.

        Returns:
            ValidationResult with errors and warnings.
        """
        result = ValidationResult()

        # Run validation checks
        self._check_unique_ids(data, result)
        self._check_referential_integrity(data, result)
        self._check_sense_lemma_consistency(data, result)
        self._check_facet_sense_consistency(data, result)
        self._check_relation_nodes_exist(data, result)
        self._check_bidirectional_relations(data, result)

        return result

    def _check_unique_ids(self, data: LoadResult, result: ValidationResult):
        """Check that all IDs are unique within their type."""
        # Check lemma IDs
        lemma_ids = [r.lemma_id for r in data.lemmas]
        duplicates = self._find_duplicates(lemma_ids)
        for dup in duplicates:
            result.add_error(
                "unique_id",
                f"Duplicate lemma_id: {dup}",
                {"lemma_id": dup},
            )

        # Check sense IDs
        sense_ids = [r.sense_id for r in data.senses]
        duplicates = self._find_duplicates(sense_ids)
        for dup in duplicates:
            result.add_error(
                "unique_id",
                f"Duplicate sense_id: {dup}",
                {"sense_id": dup},
            )

        # Check facet IDs
        facet_ids = [r.facet_id for r in data.facets]
        duplicates = self._find_duplicates(facet_ids)
        for dup in duplicates:
            result.add_error(
                "unique_id",
                f"Duplicate facet_id: {dup}",
                {"facet_id": dup},
            )

        # Check synset IDs
        synset_ids = [r.synset_id for r in data.synsets]
        duplicates = self._find_duplicates(synset_ids)
        for dup in duplicates:
            result.add_error(
                "unique_id",
                f"Duplicate synset_id: {dup}",
                {"synset_id": dup},
            )

    def _find_duplicates(self, items: list) -> list:
        """Find duplicate items in a list."""
        seen = set()
        duplicates = []
        for item in items:
            if item in seen:
                if item not in duplicates:
                    duplicates.append(item)
            seen.add(item)
        return duplicates

    def _check_referential_integrity(self, data: LoadResult, result: ValidationResult):
        """Check that referenced IDs exist."""
        # Build set of all node IDs (new + existing)
        all_lemma_ids = {r.lemma_id for r in data.lemmas}
        all_sense_ids = {r.sense_id for r in data.senses}
        all_facet_ids = {r.facet_id for r in data.facets}
        all_synset_ids = {r.synset_id for r in data.synsets}

        # Add existing IDs
        for node_id, node_data in self.existing_V.items():
            node_type = node_data.get("node_type")
            if node_type == "lemma":
                all_lemma_ids.add(node_id)
            elif node_type == "sense":
                all_sense_ids.add(node_id)
            elif node_type == "facet":
                all_facet_ids.add(node_id)
            elif node_type == "synset":
                all_synset_ids.add(node_id)

        all_node_ids = all_lemma_ids | all_sense_ids | all_facet_ids | all_synset_ids

        # Check sense references to lemma
        for sense in data.senses:
            if sense.lemma_id not in all_lemma_ids:
                result.add_error(
                    "referential_integrity",
                    f"Sense {sense.sense_id} references non-existent lemma {sense.lemma_id}",
                    {"sense_id": sense.sense_id, "lemma_id": sense.lemma_id},
                )

        # Check facet references to sense
        for facet in data.facets:
            if facet.sense_id not in all_sense_ids:
                result.add_error(
                    "referential_integrity",
                    f"Facet {facet.facet_id} references non-existent sense {facet.sense_id}",
                    {"facet_id": facet.facet_id, "sense_id": facet.sense_id},
                )

        # Check relation references
        for relation in data.relations:
            if relation.src_id not in all_node_ids:
                result.add_error(
                    "referential_integrity",
                    f"Relation source {relation.src_id} does not exist",
                    {"src_id": relation.src_id, "tgt_id": relation.tgt_id},
                )
            if relation.tgt_id not in all_node_ids:
                result.add_error(
                    "referential_integrity",
                    f"Relation target {relation.tgt_id} does not exist",
                    {"src_id": relation.src_id, "tgt_id": relation.tgt_id},
                )

    def _check_sense_lemma_consistency(self, data: LoadResult, result: ValidationResult):
        """Check that sense IDs start with their lemma ID."""
        for sense in data.senses:
            if not sense.sense_id.startswith(sense.lemma_id):
                result.add_warning(
                    "id_consistency",
                    f"Sense ID {sense.sense_id} does not start with lemma ID {sense.lemma_id}",
                    {"sense_id": sense.sense_id, "lemma_id": sense.lemma_id},
                )

    def _check_facet_sense_consistency(self, data: LoadResult, result: ValidationResult):
        """Check that facet IDs start with their sense ID."""
        for facet in data.facets:
            if not facet.facet_id.startswith(facet.sense_id):
                result.add_warning(
                    "id_consistency",
                    f"Facet ID {facet.facet_id} does not start with sense ID {facet.sense_id}",
                    {"facet_id": facet.facet_id, "sense_id": facet.sense_id},
                )

    def _check_relation_nodes_exist(self, data: LoadResult, result: ValidationResult):
        """Check that relation endpoints exist in the data."""
        # Build set of all node IDs
        all_ids = set()
        all_ids.update(r.lemma_id for r in data.lemmas)
        all_ids.update(r.sense_id for r in data.senses)
        all_ids.update(r.facet_id for r in data.facets)
        all_ids.update(r.synset_id for r in data.synsets)
        all_ids.update(self.existing_V.keys())

        for relation in data.relations:
            if relation.src_id not in all_ids:
                result.add_error(
                    "missing_node",
                    f"Relation source node not found: {relation.src_id}",
                    {"relation": relation.model_dump()},
                )
            if relation.tgt_id not in all_ids:
                result.add_error(
                    "missing_node",
                    f"Relation target node not found: {relation.tgt_id}",
                    {"relation": relation.model_dump()},
                )

    def _check_bidirectional_relations(self, data: LoadResult, result: ValidationResult):
        """Check consistency of bidirectional relations (hypernym/hyponym, etc.)."""
        # Build relation lookup
        relation_pairs = {(r.src_id, r.tgt_id): r.edge_type for r in data.relations}

        # Define inverse relation pairs
        inverse_pairs = {
            RelationType.HYPERNYM: RelationType.HYPONYM,
            RelationType.HYPONYM: RelationType.HYPERNYM,
            RelationType.HOLONYM: RelationType.MERONYM,
            RelationType.MERONYM: RelationType.HOLONYM,
            RelationType.HAS_INSTANCE: RelationType.INSTANCE_OF,
            RelationType.INSTANCE_OF: RelationType.HAS_INSTANCE,
        }

        # Check for missing inverse relations (warning only)
        for (src_id, tgt_id), edge_type in relation_pairs.items():
            if edge_type in inverse_pairs:
                expected_inverse = inverse_pairs[edge_type]
                reverse_key = (tgt_id, src_id)
                if reverse_key in relation_pairs:
                    actual_inverse = relation_pairs[reverse_key]
                    if actual_inverse != expected_inverse:
                        result.add_warning(
                            "relation_consistency",
                            f"Inconsistent inverse relation: {src_id}->{tgt_id} is {edge_type.value}, "
                            f"but {tgt_id}->{src_id} is {actual_inverse.value} (expected {expected_inverse.value})",
                            {
                                "src_id": src_id,
                                "tgt_id": tgt_id,
                                "edge_type": edge_type.value,
                                "expected_inverse": expected_inverse.value,
                            },
                        )
