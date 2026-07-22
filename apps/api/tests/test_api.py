API = "/api/v1"


async def test_health(client):
    r = await client.get(f"{API}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_curriculum_shape_and_progress(client):
    r = await client.get(f"{API}/curriculum")
    assert r.status_code == 200
    data = r.json()
    month = data["months"][0]
    assert month["number"] == 7
    assert month["title"] == "Transformers From Scratch"
    assert len(month["weeks"]) == 4
    assert sum(len(w["lessons"]) for w in month["weeks"]) == 20

    statuses = {l["slug"]: l["status"] for w in month["weeks"] for l in w["lessons"]}
    assert statuses["why-attention"] == "done"
    assert statuses["multi-head-attention"] == "current"
    assert statuses["positional-encoding"] == "todo"
    # 7 of 20 done → 35%
    assert month["progress"] == 35


async def test_lesson_detail(client):
    r = await client.get(f"{API}/lessons/multi-head-attention")
    assert r.status_code == 200
    d = r.json()
    assert d["code"] == "7.2.3"
    assert d["progress_status"] == "in_progress"
    assert d["resume_anchor"] == "math"
    done = {s["anchor"] for s in d["sections"] if s["done"]}
    assert done == {"objectives", "intuition", "history"}


async def test_lesson_404_problem_json(client):
    r = await client.get(f"{API}/lessons/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["title"] == "Not found"


async def test_tick_section_and_complete_lesson(client):
    # tick remaining sections of the in-progress lesson
    for anchor in ["math", "visualizer", "python"]:
        r = await client.put(f"{API}/progress/lessons/multi-head-attention/sections/{anchor}")
        assert r.status_code == 200
        assert r.json()["lesson_status"] == "in_progress"

    r = await client.put(f"{API}/progress/lessons/multi-head-attention/sections/quiz")
    body = r.json()
    assert body["lesson_status"] == "completed"
    assert body["ticked_sections"] == body["total_sections"] == 7

    # idempotent re-tick
    r = await client.put(f"{API}/progress/lessons/multi-head-attention/sections/quiz")
    assert r.json()["lesson_status"] == "completed"

    # summary reflects it: 8 done, next lesson is positional-encoding
    r = await client.get(f"{API}/progress/summary")
    s = r.json()
    assert s["lessons_completed"] == 8
    assert s["current"]["slug"] == "positional-encoding"


async def test_tick_unknown_section_404(client):
    r = await client.put(f"{API}/progress/lessons/multi-head-attention/sections/bogus")
    assert r.status_code == 404
