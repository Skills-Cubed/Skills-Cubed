"""Deterministic unit tests for hybrid score merging logic.

These test _merge_scores directly — no Neo4j required.
"""

import pytest

from src.db.queries import _merge_scores
from src.skills.models import Skill
from src.utils.config import EMBEDDING_DIM

_EMBED = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
_EMBED_ALT = [0.0, 1.0] + [0.0] * (EMBEDDING_DIM - 2)


def _props(skill_id: str, **overrides) -> dict:
    """Build a minimal valid Skill props dict for testing."""
    base = dict(
        skill_id=skill_id,
        title=f"Skill {skill_id}",
        version=1,
        problem="test problem",
        resolution_md="test resolution",
        conditions=[],
        keywords=[],
        embedding=_EMBED,
        product_area="",
        issue_type="",
        confidence=0.5,
        times_used=0,
        times_confirmed=0,
        created_at="2025-01-01T00:00:00+00:00",
        updated_at="2025-01-01T00:00:00+00:00",
    )
    base.update(overrides)
    return base


class TestMergeScoresWeighting:
    def test_vector_only_no_keyword_results(self):
        """Without keyword results, score equals vector score (no 0.7 penalty)."""
        vec = [(_props("a"), 0.9)]
        result = _merge_scores(vec, [], min_score=0.0, top_k=5)
        assert len(result) == 1
        assert result[0]["score"] == pytest.approx(0.9)

    def test_combined_weighting(self):
        """With keyword results, score = 0.7*vec + 0.3*kw."""
        props = _props("a")
        vec = [(props, 0.8)]
        kw = [(props, 5.0)]  # single result → normalizes to 1.0
        result = _merge_scores(vec, kw, min_score=0.0, top_k=5)
        assert len(result) == 1
        # 0.7 * 0.8 + 0.3 * 1.0 = 0.56 + 0.30 = 0.86
        assert result[0]["score"] == pytest.approx(0.86)

    def test_vector_in_both_keyword_missing(self):
        """Skill only in vector results gets kw_score=0.0."""
        vec = [(_props("a"), 0.8)]
        kw = [(_props("b"), 3.0)]  # different skill
        result = _merge_scores(vec, kw, min_score=0.0, top_k=5)
        scores = {r["skill"].skill_id: r["score"] for r in result}
        # a: 0.7*0.8 + 0.3*0.0 = 0.56
        assert scores["a"] == pytest.approx(0.56)
        # b: 0.7*0.0 + 0.3*1.0 = 0.30
        assert scores["b"] == pytest.approx(0.30)

    def test_keyword_only_missing_vector(self):
        """Skill only in keyword results gets vec_score=0.0."""
        kw = [(_props("a"), 5.0)]
        result = _merge_scores([], kw, min_score=0.0, top_k=5)
        assert len(result) == 1
        # 0.7*0.0 + 0.3*1.0 = 0.30
        assert result[0]["score"] == pytest.approx(0.30)


class TestKeywordEmptyFallback:
    def test_no_keyword_results_uses_full_vector_score(self):
        """When kw_records is empty, vector scores are NOT penalized to 0.7 max.

        This is the bug fix: weighting is based on whether keyword results
        actually exist, not on whether query_text was non-empty.
        """
        vec = [(_props("a"), 0.95)]
        # Empty kw_records — even though a keyword query may have been attempted
        result = _merge_scores(vec, [], min_score=0.0, top_k=5)
        assert result[0]["score"] == pytest.approx(0.95)

    def test_no_keyword_results_no_false_min_score_drop(self):
        """Vector-only results with min_score=0.8 should not be dropped when
        keyword search returned nothing."""
        vec = [(_props("a"), 0.85)]
        result = _merge_scores(vec, [], min_score=0.8, top_k=5)
        # Without the fix, 0.7*0.85 = 0.595 < 0.8 → wrongly filtered
        assert len(result) == 1
        assert result[0]["score"] == pytest.approx(0.85)


class TestBM25Normalization:
    def test_all_same_score_normalizes_to_one(self):
        """When all BM25 scores are identical, they all normalize to 1.0."""
        props_a, props_b = _props("a"), _props("b")
        vec = [(props_a, 0.5), (props_b, 0.5)]
        kw = [(props_a, 3.0), (props_b, 3.0)]  # identical BM25 scores
        result = _merge_scores(vec, kw, min_score=0.0, top_k=5)
        for r in result:
            # 0.7*0.5 + 0.3*1.0 = 0.65
            assert r["score"] == pytest.approx(0.65)

    def test_min_max_spread(self):
        """BM25 scores are min-max normalized within the result set."""
        props_a, props_b = _props("a"), _props("b")
        vec = [(props_a, 0.5), (props_b, 0.5)]
        kw = [(props_a, 10.0), (props_b, 2.0)]  # a=max, b=min
        result = _merge_scores(vec, kw, min_score=0.0, top_k=5)
        scores = {r["skill"].skill_id: r["score"] for r in result}
        # a: kw normalized = (10-2)/(10-2) = 1.0 → 0.7*0.5 + 0.3*1.0 = 0.65
        assert scores["a"] == pytest.approx(0.65)
        # b: kw normalized = (2-2)/(10-2) = 0.0 → 0.7*0.5 + 0.3*0.0 = 0.35
        assert scores["b"] == pytest.approx(0.35)

    def test_single_keyword_result_normalizes_to_one(self):
        """A single keyword result normalizes to 1.0 (range=0 → all 1.0)."""
        props = _props("a")
        vec = [(props, 0.6)]
        kw = [(props, 7.5)]
        result = _merge_scores(vec, kw, min_score=0.0, top_k=5)
        # 0.7*0.6 + 0.3*1.0 = 0.72
        assert result[0]["score"] == pytest.approx(0.72)


class TestClampingAndFiltering:
    def test_clamp_above_one(self):
        """Scores above 1.0 from vector are clamped."""
        vec = [(_props("a"), 1.5)]
        result = _merge_scores(vec, [], min_score=0.0, top_k=5)
        assert result[0]["score"] == pytest.approx(1.0)

    def test_clamp_below_zero(self):
        """Negative vector scores are clamped to 0.0."""
        vec = [(_props("a"), -0.3)]
        result = _merge_scores(vec, [], min_score=0.0, top_k=5)
        assert result[0]["score"] == pytest.approx(0.0)

    def test_min_score_filters(self):
        """Results below min_score are excluded."""
        vec = [(_props("a"), 0.9), (_props("b"), 0.3)]
        result = _merge_scores(vec, [], min_score=0.5, top_k=5)
        assert len(result) == 1
        assert result[0]["skill"].skill_id == "a"

    def test_top_k_limits_results(self):
        """Only top_k results are returned."""
        vec = [(_props(f"s{i}"), 0.9 - i * 0.1) for i in range(5)]
        result = _merge_scores(vec, [], min_score=0.0, top_k=2)
        assert len(result) == 2
        assert result[0]["score"] > result[1]["score"]


class TestEdgeCases:
    def test_empty_inputs(self):
        """No results from either search returns empty list."""
        result = _merge_scores([], [], min_score=0.0, top_k=5)
        assert result == []

    def test_empty_with_keyword_records(self):
        """Empty kw_records means vector-only scoring, not combined."""
        result = _merge_scores([], [], min_score=0.0, top_k=5)
        assert result == []

    def test_sorted_descending(self):
        """Results are sorted by score descending."""
        vec = [(_props("a"), 0.3), (_props("b"), 0.9), (_props("c"), 0.6)]
        result = _merge_scores(vec, [], min_score=0.0, top_k=5)
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_returns_skill_objects(self):
        """Each result contains a proper Skill instance."""
        vec = [(_props("a"), 0.8)]
        result = _merge_scores(vec, [], min_score=0.0, top_k=5)
        assert isinstance(result[0]["skill"], Skill)
        assert result[0]["skill"].skill_id == "a"
