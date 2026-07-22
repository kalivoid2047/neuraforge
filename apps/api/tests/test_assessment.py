from neuraforge.assessment import grading
from neuraforge.assessment.models import Question

API = "/api/v1"

SOFTMAX_CODE = """
import math

def softmax(xs):
    m = max(xs)
    es = [math.exp(x - m) for x in xs]
    total = sum(es)
    return [e / total for e in es]
"""

BROKEN_CODE = """
def softmax(xs):
    return xs  # wrong: not normalized, not exponentiated
"""


# ── pure grading unit tests ─────────────────────────────────────────────


def _q(qtype: str, answer_key: dict) -> Question:
    return Question(
        qtype=qtype, bank="practice", body={}, answer_key=answer_key,
        explanation={}, topic_tags=[], difficulty=1,
    )


def test_grade_mcq_single():
    q = _q("mcq_single", {"correct": "a"})
    assert grading.grade_objective(q, {"selected": "a"})[0] is True
    assert grading.grade_objective(q, {"selected": "b"})[0] is False


def test_grade_mcq_multi_order_independent():
    q = _q("mcq_multi", {"correct": ["a", "c"]})
    assert grading.grade_objective(q, {"selected": ["c", "a"]})[0] is True
    assert grading.grade_objective(q, {"selected": ["a"]})[0] is False


def test_grade_numeric_within_tolerance():
    q = _q("numeric", {"value": 3.14, "tolerance": 0.01})
    assert grading.grade_objective(q, {"value": 3.145})[0] is True
    assert grading.grade_objective(q, {"value": 3.2})[0] is False
    assert grading.grade_objective(q, {"value": "not a number"})[0] is False


def test_grade_fill_blank_case_insensitive():
    q = _q("fill_blank", {"text": "future"})
    assert grading.grade_objective(q, {"text": "  FUTURE  "})[0] is True
    assert grading.grade_objective(q, {"text": "past"})[0] is False


def test_grade_free_text_is_ungraded():
    q = _q("free_text", {})
    correct, message = grading.grade_objective(q, {"text": "anything"})
    assert correct is None and message == "pending review"


# ── API integration: quiz flow ──────────────────────────────────────────

# Answers matching the seeded questions, in seed insertion order (mcq_single,
# mcq_multi, numeric, fill_blank) — see seed._seed_assessment.
CORRECT_ANSWERS = {
    "mcq_single": {"selected": "a"},
    "mcq_multi": {"selected": ["a", "b", "c"]},
    "numeric": {"value": 64},
    "fill_blank": {"text": "future"},
}


async def test_quiz_attempt_scores_and_awards_xp_once(client):
    quiz = (await client.get(f"{API}/quizzes/lessons/multi-head-attention")).json()
    assert quiz["question_count"] == 4

    start = await client.post(f"{API}/quizzes/{quiz['id']}/attempts")
    assert start.status_code == 201
    attempt = start.json()
    assert len(attempt["questions"]) == 4

    xp_before = (await client.get(f"{API}/xp")).json()["total"]

    for q in attempt["questions"]:
        answer = CORRECT_ANSWERS[q["qtype"]]
        r = await client.patch(
            f"{API}/attempts/{attempt['attempt_id']}/answers/{q['id']}", json={"answer": answer}
        )
        assert r.json()["correct"] is True

    finish = await client.post(f"{API}/attempts/{attempt['attempt_id']}/finish")
    body = finish.json()
    assert body["score"] == 100.0
    assert body["passed"] is True
    assert body["xp_awarded"] is True

    # idempotent: re-finishing the same attempt must not double-award (uq_xp_once)
    finish2 = await client.post(f"{API}/attempts/{attempt['attempt_id']}/finish")
    assert finish2.json()["xp_awarded"] is False

    xp_after = (await client.get(f"{API}/xp")).json()["total"]
    assert xp_after == xp_before + 30


async def test_answering_unknown_question_404s(client):
    quiz = (await client.get(f"{API}/quizzes/lessons/multi-head-attention")).json()
    attempt = (await client.post(f"{API}/quizzes/{quiz['id']}/attempts")).json()
    r = await client.patch(
        f"{API}/attempts/{attempt['attempt_id']}/answers/00000000-0000-0000-0000-000000000000",
        json={"answer": {"selected": "a"}},
    )
    assert r.status_code == 404


# ── API integration: server-side exercise grading ──────────────────────


async def test_exercise_submission_pass_then_fail(client):
    exercise = (await client.get(f"{API}/exercises/lessons/multi-head-attention")).json()
    assert "softmax" in exercise["starter_code"]

    xp_before = (await client.get(f"{API}/xp")).json()["total"]

    r = await client.post(
        f"{API}/exercises/{exercise['id']}/submissions", json={"code": SOFTMAX_CODE}
    )
    body = r.json()
    assert body["status"] == "passed"
    assert body["xp_awarded"] is True
    assert all(t["passed"] for t in body["tests"])

    xp_after = (await client.get(f"{API}/xp")).json()["total"]
    assert xp_after == xp_before + 20

    # resubmitting a passing solution must not double-award (uq_xp_once)
    r2 = await client.post(
        f"{API}/exercises/{exercise['id']}/submissions", json={"code": SOFTMAX_CODE}
    )
    assert r2.json()["xp_awarded"] is False

    r3 = await client.post(
        f"{API}/exercises/{exercise['id']}/submissions", json={"code": BROKEN_CODE}
    )
    body3 = r3.json()
    assert body3["status"] == "failed"
    assert any(not t["passed"] for t in body3["tests"])


async def test_exercise_submission_syntax_error_reports_error(client):
    exercise = (await client.get(f"{API}/exercises/lessons/multi-head-attention")).json()
    r = await client.post(
        f"{API}/exercises/{exercise['id']}/submissions", json={"code": "def broken(:\n"}
    )
    body = r.json()
    assert body["status"] == "error"
    assert body["error"] is not None


# ── API integration: project submission ─────────────────────────────────


async def test_project_submission_valid_url_awards_xp(client):
    projects = (await client.get(f"{API}/projects?kind=forge")).json()
    assert len(projects) == 1
    project = projects[0]

    self_assessment = {c: True for c in project["rubric"]}
    r = await client.post(
        f"{API}/projects/{project['id']}/submissions",
        json={"artifact_url": "https://github.com/amina/transformer-from-scratch", "self_assessment": self_assessment},
    )
    body = r.json()
    assert body["status"] == "submitted"
    assert body["check_results"]["artifact_url_valid"] is True

    xp = (await client.get(f"{API}/xp")).json()
    project_events = [e for e in xp["recent"] if e["reason"] == "project_submitted"]
    assert len(project_events) == 1


async def test_project_submission_invalid_url_needs_work(client):
    projects = (await client.get(f"{API}/projects?kind=forge")).json()
    project = projects[0]
    r = await client.post(
        f"{API}/projects/{project['id']}/submissions",
        json={"artifact_url": "not-a-url", "self_assessment": {}},
    )
    assert r.json()["status"] == "needs_work"
