import os

import pytest

from src.skills.models import Skill, SkillUpdate
from src.utils.config import EMBEDDING_DIM

pytestmark = pytest.mark.skipif(
    not all(os.getenv(v) for v in ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")),
    reason="Neo4j credentials not configured (need NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)",
)

# Deterministic test embedding — unit vector along first dimension
_TEST_EMBEDDING = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
_ALT_EMBEDDING = [0.0, 1.0] + [0.0] * (EMBEDDING_DIM - 2)


def _make_skill(**overrides) -> Skill:
    defaults = dict(
        title="Test: password reset",
        problem="Customer cannot reset password",
        resolution_md="## Do\n1. Verify identity\n2. Send reset link",
        embedding=_TEST_EMBEDDING,
        keywords=["password", "reset"],
        product_area="account",
        issue_type="access",
    )
    defaults.update(overrides)
    return Skill.create_new(**defaults)


_indexes_initialized = False


@pytest.fixture(autouse=True)
async def _reset_driver():
    """Reset the global driver before each test so it binds to the current event loop."""
    from src.db import connection

    connection._driver = None

    global _indexes_initialized
    if not _indexes_initialized:
        await connection.initialize_indexes()
        # Clean up stale test nodes from previous runs
        driver = await connection.get_driver()
        async with driver.session() as session:
            await session.run(
                "MATCH (s:Skill) WHERE s.title STARTS WITH 'Test: ' DELETE s"
            )
        _indexes_initialized = True
        # Reset so the test gets a fresh driver on its own loop
        connection._driver = None


@pytest.fixture
async def created_skill():
    """Create a skill, yield it, then clean up."""
    from src.db.connection import get_driver
    from src.db.queries import create_skill

    skill = _make_skill()
    created = await create_skill(skill)
    yield created

    # Cleanup
    driver = await get_driver()
    async with driver.session() as session:
        await session.run(
            "MATCH (s:Skill {skill_id: $sid}) DELETE s",
            sid=created.skill_id,
        )


@pytest.mark.integration
async def test_create_and_get(created_skill):
    from src.db.queries import get_skill

    fetched = await get_skill(created_skill.skill_id)
    assert fetched is not None
    assert fetched.skill_id == created_skill.skill_id
    assert fetched.title == created_skill.title
    assert fetched.resolution_md == created_skill.resolution_md
    assert fetched.version == 1


@pytest.mark.integration
async def test_get_skill_not_found():
    from src.db.queries import get_skill

    result = await get_skill("nonexistent-id")
    assert result is None


@pytest.mark.integration
async def test_update_skill(created_skill):
    from src.db.queries import update_skill

    updates = SkillUpdate(title="Updated: password reset flow", confidence=0.9)
    updated = await update_skill(created_skill.skill_id, updates)

    assert updated.title == "Updated: password reset flow"
    assert updated.confidence == 0.9
    assert updated.version == 2
    assert updated.skill_id == created_skill.skill_id


@pytest.mark.integration
async def test_update_skill_not_found():
    from src.db.queries import update_skill

    with pytest.raises(ValueError, match="not found"):
        await update_skill("nonexistent-id", SkillUpdate(title="nope"))


@pytest.mark.integration
async def test_check_duplicate(created_skill):
    from src.db.queries import check_duplicate

    # Same embedding → should find duplicate
    dup = await check_duplicate(_TEST_EMBEDDING, threshold=0.9)
    assert dup is not None
    assert dup.skill_id == created_skill.skill_id

    # Different embedding → should not match
    no_dup = await check_duplicate(_ALT_EMBEDDING, threshold=0.9)
    assert no_dup is None


@pytest.mark.integration
async def test_hybrid_search(created_skill):
    from src.db.queries import hybrid_search

    results = await hybrid_search(
        query_embedding=_TEST_EMBEDDING,
        query_text="password reset",
        top_k=5,
        min_score=0.0,
    )
    assert len(results) >= 1
    assert results[0]["skill"].skill_id == created_skill.skill_id
    assert 0.0 <= results[0]["score"] <= 1.0


@pytest.mark.integration
async def test_hybrid_search_vector_only(created_skill):
    from src.db.queries import hybrid_search

    results = await hybrid_search(
        query_embedding=_TEST_EMBEDDING,
        query_text="",
        top_k=5,
    )
    assert len(results) >= 1
    # With no keyword boost, score should still be valid
    assert 0.0 <= results[0]["score"] <= 1.0


@pytest.mark.integration
async def test_hybrid_search_min_score_filter(created_skill):
    from src.db.queries import hybrid_search

    results = await hybrid_search(
        query_embedding=_ALT_EMBEDDING,
        query_text="completely unrelated xyz",
        top_k=5,
        min_score=0.99,
    )
    # With an orthogonal embedding and unrelated text, high min_score should filter out
    # (may or may not return results depending on DB state, but scores must be >= 0.99)
    for r in results:
        assert r["score"] >= 0.99
