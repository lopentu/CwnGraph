"""Transform loaded data to CwnGraph format."""

from dataclasses import dataclass, field
from datetime import datetime

from cwn_pipeline.pipeline.loader import LoadResult
from cwn_pipeline.schemas.enums import RelationType


@dataclass
class TransformResult:
    """Result of transforming data to CwnGraph format."""

    V: dict = field(default_factory=dict)  # Vertices (nodes)
    E: dict = field(default_factory=dict)  # Edges (relations)
    meta: dict = field(default_factory=dict)  # Metadata

    def summary(self) -> dict:
        """Return summary statistics."""
        node_types = {}
        for ndata in self.V.values():
            ntype = ndata.get("node_type", "unknown")
            node_types[ntype] = node_types.get(ntype, 0) + 1

        edge_types = {}
        for edata in self.E.values():
            etype = edata.get("edge_type", "unknown")
            edge_types[etype] = edge_types.get(etype, 0) + 1

        return {
            "total_nodes": len(self.V),
            "total_edges": len(self.E),
            "node_types": node_types,
            "edge_types": edge_types,
            "version": self.meta.get("version", "unknown"),
        }


class CwnTransformer:
    """Transform loaded data to CwnGraph (V, E, meta) format."""

    def __init__(self, base_data: tuple[dict, dict, dict] | None = None):
        """Initialize transformer.

        Args:
            base_data: Optional (V, E, meta) tuple to merge updates into.
                      If None, creates a new dataset from scratch.
        """
        if base_data:
            self.base_V = dict(base_data[0])
            self.base_E = dict(base_data[1])
            self.base_meta = dict(base_data[2])
        else:
            self.base_V = {}
            self.base_E = {}
            self.base_meta = {}

    def transform(
        self,
        data: LoadResult,
        version: str | None = None,
        label: str | None = None,
    ) -> TransformResult:
        """Transform loaded data to CwnGraph format.

        Args:
            data: LoadResult from CsvLoader.
            version: Version string for the new dataset.
            label: Label for the new dataset.

        Returns:
            TransformResult containing V, E, and meta.
        """
        result = TransformResult()

        # Start with base data if available
        result.V = dict(self.base_V)
        result.E = dict(self.base_E)
        result.meta = dict(self.base_meta)

        # Transform nodes
        self._transform_lemmas(data, result)
        self._transform_senses(data, result)
        self._transform_facets(data, result)
        self._transform_synsets(data, result)

        # Transform relations
        self._transform_semantic_relations(data, result)

        # Generate structural relations
        self._generate_structural_relations(data, result)

        # Update metadata
        self._update_meta(result, version, label)

        return result

    def _transform_lemmas(self, data: LoadResult, result: TransformResult):
        """Add lemma nodes to result."""
        for lemma in data.lemmas:
            result.V[lemma.lemma_id] = lemma.to_node_data()

    def _transform_senses(self, data: LoadResult, result: TransformResult):
        """Add sense nodes to result."""
        for sense in data.senses:
            result.V[sense.sense_id] = sense.to_node_data()

    def _transform_facets(self, data: LoadResult, result: TransformResult):
        """Add facet nodes to result."""
        for facet in data.facets:
            result.V[facet.facet_id] = facet.to_node_data()

    def _transform_synsets(self, data: LoadResult, result: TransformResult):
        """Add synset nodes to result."""
        for synset in data.synsets:
            result.V[synset.synset_id] = synset.to_node_data()

    def _transform_semantic_relations(self, data: LoadResult, result: TransformResult):
        """Add semantic relations to result."""
        for relation in data.relations:
            edge_key = relation.edge_key
            result.E[edge_key] = relation.to_edge_data()

    def _generate_structural_relations(self, data: LoadResult, result: TransformResult):
        """Generate structural relations (has_sense, has_facet, etc.)."""
        # Generate lemma -> sense relations
        for sense in data.senses:
            edge_key = (sense.lemma_id, sense.sense_id)
            result.E[edge_key] = {"edge_type": RelationType.HAS_SENSE.value}

        # Generate sense -> facet relations
        for facet in data.facets:
            edge_key = (facet.sense_id, facet.facet_id)
            result.E[edge_key] = {"edge_type": RelationType.HAS_FACET.value}

    def _update_meta(
        self,
        result: TransformResult,
        version: str | None,
        label: str | None,
    ):
        """Update metadata."""
        now = datetime.now()

        if version is None:
            version = f"v.{now.strftime('%Y.%m.%d')}"

        if label is None:
            label = f"cwn-graph-{version}"

        result.meta.update(
            {
                "version": version,
                "label": label,
                "updated_at": now.isoformat(),
                "node_count": len(result.V),
                "edge_count": len(result.E),
            }
        )


class IncrementalTransformer(CwnTransformer):
    """Transform data for incremental updates.

    Only applies changes (additions, modifications) without full rebuild.
    """

    def apply_changes(
        self,
        data: LoadResult,
        version: str | None = None,
        label: str | None = None,
    ) -> TransformResult:
        """Apply incremental changes to base data.

        This is more efficient for small updates as it only modifies
        changed entries rather than rebuilding the entire dataset.

        Args:
            data: LoadResult containing only new/modified records.
            version: Version string for the updated dataset.
            label: Label for the updated dataset.

        Returns:
            TransformResult containing updated V, E, and meta.
        """
        result = TransformResult()
        result.V = dict(self.base_V)
        result.E = dict(self.base_E)
        result.meta = dict(self.base_meta)

        # Track changes for metadata
        changes = {
            "added_nodes": 0,
            "modified_nodes": 0,
            "added_edges": 0,
            "modified_edges": 0,
        }

        # Apply node updates
        for lemma in data.lemmas:
            is_new = lemma.lemma_id not in result.V
            result.V[lemma.lemma_id] = lemma.to_node_data()
            if is_new:
                changes["added_nodes"] += 1
            else:
                changes["modified_nodes"] += 1

        for sense in data.senses:
            is_new = sense.sense_id not in result.V
            result.V[sense.sense_id] = sense.to_node_data()
            if is_new:
                changes["added_nodes"] += 1
            else:
                changes["modified_nodes"] += 1

        for facet in data.facets:
            is_new = facet.facet_id not in result.V
            result.V[facet.facet_id] = facet.to_node_data()
            if is_new:
                changes["added_nodes"] += 1
            else:
                changes["modified_nodes"] += 1

        for synset in data.synsets:
            is_new = synset.synset_id not in result.V
            result.V[synset.synset_id] = synset.to_node_data()
            if is_new:
                changes["added_nodes"] += 1
            else:
                changes["modified_nodes"] += 1

        # Apply relation updates
        for relation in data.relations:
            edge_key = relation.edge_key
            is_new = edge_key not in result.E
            result.E[edge_key] = relation.to_edge_data()
            if is_new:
                changes["added_edges"] += 1
            else:
                changes["modified_edges"] += 1

        # Generate structural relations for new nodes
        for sense in data.senses:
            edge_key = (sense.lemma_id, sense.sense_id)
            if edge_key not in result.E:
                result.E[edge_key] = {"edge_type": RelationType.HAS_SENSE.value}
                changes["added_edges"] += 1

        for facet in data.facets:
            edge_key = (facet.sense_id, facet.facet_id)
            if edge_key not in result.E:
                result.E[edge_key] = {"edge_type": RelationType.HAS_FACET.value}
                changes["added_edges"] += 1

        # Update metadata
        self._update_meta(result, version, label)
        result.meta["changes"] = changes

        return result
