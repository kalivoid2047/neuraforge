"""Pure grading + quiz-assembly logic (FR-ASSESS-1/3), no DB session required
for grading itself so it's directly unit-testable — mirrors the split in
learning/review.py (pure scheduler) vs learning/service.py (persistence).

Answer/answer_key JSON shapes (this module's contract, per qtype):
  mcq_single  answer_key={"correct": "a"}            answer={"selected": "a"}
  mcq_multi   answer_key={"correct": ["a","c"]}       answer={"selected": ["a","c"]}
  numeric     answer_key={"value": 3.14, "tolerance": 0.01}   answer={"value": 3.15}
  code_output answer_key={"output": "42"}             answer={"output": "42"}
  fill_blank  answer_key={"text": "gradient descent"} answer={"text": "Gradient Descent"}
  free_text   not auto-graded — always returns (None, "pending review")
"""

import random
import uuid

from .models import Question


def grade_objective(question: Question, answer: dict) -> tuple[bool | None, str]:
    """Returns (correct, message). correct is None for ungraded types (free_text)."""
    key = question.answer_key
    qtype = question.qtype

    if qtype == "mcq_single":
        correct = answer.get("selected") == key.get("correct")
        return correct, "correct" if correct else "incorrect"

    if qtype == "mcq_multi":
        got = set(answer.get("selected") or [])
        correct = got == set(key.get("correct") or [])
        return correct, "correct" if correct else "incorrect"

    if qtype == "numeric":
        try:
            got = float(answer.get("value"))
        except (TypeError, ValueError):
            return False, "not a number"
        target = float(key.get("value", 0))
        tolerance = float(key.get("tolerance", 0))
        correct = abs(got - target) <= tolerance
        return correct, "correct" if correct else f"expected {target} ± {tolerance}"

    if qtype == "code_output":
        got = str(answer.get("output", "")).strip()
        correct = got == str(key.get("output", "")).strip()
        return correct, "correct" if correct else "output does not match"

    if qtype == "fill_blank":
        got = str(answer.get("text", "")).strip().casefold()
        correct = got == str(key.get("text", "")).strip().casefold()
        return correct, "correct" if correct else "incorrect"

    if qtype == "free_text":
        return None, "pending review"

    return False, f"unsupported question type: {qtype}"


async def select_questions(session, blueprint: dict) -> list[Question]:
    """Instantiate a quiz's question set from its blueprint (FR-ASSESS-3).

    Explicit `question_ids` (lesson mini-quizzes, hand-authored) are used
    verbatim. Otherwise a random sample is drawn from the bank filtered by
    tags/difficulty — a fresh random selection per attempt (unlike Sparks,
    quiz assembly has no "same question all day" requirement).
    """
    from sqlalchemy import select

    if "question_ids" in blueprint:
        ids = [uuid.UUID(str(i)) for i in blueprint["question_ids"]]
        rows = (await session.scalars(select(Question).where(Question.id.in_(ids)))).all()
        by_id = {q.id: q for q in rows}
        return [by_id[i] for i in ids if i in by_id]

    query = select(Question).where(Question.status == "published")
    if bank := blueprint.get("bank"):
        query = query.where(Question.bank == bank)
    if lo_hi := blueprint.get("difficulty"):
        query = query.where(Question.difficulty.between(lo_hi[0], lo_hi[1]))
    candidates = list(await session.scalars(query))
    tags = set(blueprint.get("topic_tags") or [])
    if tags:
        candidates = [q for q in candidates if tags & set(q.topic_tags)]
    count = int(blueprint.get("count", 10))
    return random.sample(candidates, k=min(count, len(candidates)))
