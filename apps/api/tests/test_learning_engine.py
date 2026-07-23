from neuraforge.learning.review import schedule
from neuraforge.learning.models import ReviewState
from datetime import UTC, datetime

API = "/api/v1"


# ── pure scheduler unit tests ───────────────────────────────────────────

def _state() -> ReviewState:
    return ReviewState(stability=0.0, difficulty=5.0, reps=0, lapses=0,
                       due_at=datetime.now(UTC))


def test_scheduler_good_grades_grow_interval():
    s = _state()
    intervals = []
    for _ in range(4):
        schedule(s, 3)
        intervals.append(s.stability)
    assert intervals == sorted(intervals)          # monotonic growth
    assert intervals[0] >= 1.0 and intervals[-1] > 4.0


def test_scheduler_again_shrinks_and_counts_lapse():
    s = _state()
    schedule(s, 3)
    schedule(s, 3)
    before = s.stability
    schedule(s, 1)
    assert s.stability < before and s.lapses == 1
    assert s.difficulty > 5.0


def test_scheduler_easy_reduces_difficulty():
    s = _state()
    schedule(s, 4)
    assert s.difficulty < 5.0 and s.stability >= 2.0


# ── API integration ─────────────────────────────────────────────────────

async def test_review_queue_and_grading_awards_daily_xp(client):
    r = await client.get(f"{API}/reviews/queue")
    assert r.status_code == 200
    queue = r.json()
    assert len(queue) == 6  # seeded system deck, all new → all due

    xp_before = (await client.get(f"{API}/xp")).json()["total"]

    r = await client.post(f"{API}/reviews/{queue[0]['card_id']}/grade", json={"grade": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["interval_days"] >= 1.0
    assert body["xp_awarded"] is True

    # graded card leaves today's queue
    r = await client.get(f"{API}/reviews/queue")
    assert len(r.json()) == 5

    # second grade the same day: no double review-session XP (uq_xp_once)
    r = await client.post(f"{API}/reviews/{queue[1]['card_id']}/grade", json={"grade": 2})
    assert r.json()["xp_awarded"] is False

    xp_after = (await client.get(f"{API}/xp")).json()["total"]
    assert xp_after == xp_before + 10


async def test_spark_assignment_stable_and_completable(client):
    r1 = await client.get(f"{API}/sparks/today")
    r2 = await client.get(f"{API}/sparks/today")
    assert r1.json()["title"] == r2.json()["title"]  # deterministic per day
    assert r1.json()["completed"] is False

    r = await client.post(f"{API}/sparks/today/complete")
    assert r.json()["completed"] is True

    # idempotent completion; XP awarded exactly once
    await client.post(f"{API}/sparks/today/complete")
    xp = (await client.get(f"{API}/xp")).json()
    spark_events = [e for e in xp["recent"] if e["reason"] == "daily_spark"]
    assert len(spark_events) == 1 and spark_events[0]["amount"] == 15


async def test_planner_composes_queue_and_spark(client):
    r = await client.get(f"{API}/planner/today")
    assert r.status_code == 200
    p = r.json()
    assert p["cards_due"] == 6
    assert p["spark"]["completed"] is False
    kinds = {i["kind"] for i in p["items"]}
    assert kinds == {"spark", "reviews"}


async def test_lesson_completion_awards_xp_via_events(client):
    # complete the in-progress lesson (4 remaining sections)
    for anchor in ["math", "visualizer", "python", "quiz"]:
        await client.put(f"{API}/progress/lessons/multi-head-attention/sections/{anchor}")

    xp = (await client.get(f"{API}/xp")).json()
    lesson_events = [e for e in xp["recent"] if e["reason"] == "lesson_complete"]
    assert len(lesson_events) == 1
    assert lesson_events[0]["ref_id"] == "multi-head-attention"
    assert lesson_events[0]["amount"] == 50

    # re-ticking a completed lesson must not re-award (event + DB idempotency)
    await client.put(f"{API}/progress/lessons/multi-head-attention/sections/quiz")
    xp2 = (await client.get(f"{API}/xp")).json()
    assert xp2["total"] == xp["total"]


async def test_streak_records_activity(client):
    await client.put(f"{API}/progress/lessons/multi-head-attention/sections/math")
    r = await client.get(f"{API}/streak")
    s = r.json()
    assert s["current"] == 1  # first activity today
    assert s["last_active_date"] is not None
