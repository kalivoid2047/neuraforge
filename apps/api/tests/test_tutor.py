import json

API = "/api/v1"

# No LLM endpoint runs in CI/dev — every chat exercises the fallback path,
# which is itself a required behavior (P-6). Provider streaming is covered
# by the OpenAI-compatible contract; a live-model smoke test is a Phase 12 gate.


def _events(sse_text: str) -> list[dict]:
    return [
        json.loads(line.removeprefix("data:").strip())
        for line in sse_text.splitlines()
        if line.startswith("data:")
    ]


async def _make_thread(client, context=None) -> str:
    r = await client.post(f"{API}/tutor/threads", json={"context": context or {}})
    assert r.status_code == 201
    return r.json()["id"]


async def test_chat_falls_back_with_citations(client):
    thread_id = await _make_thread(client, {"lesson_slug": "multi-head-attention"})
    r = await client.post(
        f"{API}/tutor/threads/{thread_id}/messages",
        json={"text": "Why do we scale attention scores by sqrt d_k?"},
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    events = _events(r.text)

    metas = [e for e in events if e["type"] == "meta"]
    assert metas and metas[-1]["fallback"] is True          # no provider → degrade
    assert any(c["lesson_slug"] == "multi-head-attention" for c in metas[0]["citations"])

    tokens = "".join(e["text"] for e in events if e["type"] == "token")
    assert "retrieved, not generated" in tokens             # honest fallback labeling
    assert "sqrt" in tokens.lower() or "√" in tokens or "scale" in tokens.lower()
    assert events[-1]["type"] == "done"


async def test_history_persists_and_thread_titled(client):
    thread_id = await _make_thread(client)
    await client.post(f"{API}/tutor/threads/{thread_id}/messages",
                      json={"text": "What is softmax?"})
    r = await client.get(f"{API}/tutor/threads")
    threads = r.json()
    assert threads[0]["title"] == "What is softmax?"


async def test_budget_exhaustion_blocks_with_429(client, monkeypatch):
    from neuraforge.core.config import get_settings
    monkeypatch.setattr(get_settings(), "ember_daily_token_budget", 5)

    thread_id = await _make_thread(client)
    r1 = await client.post(f"{API}/tutor/threads/{thread_id}/messages",
                           json={"text": "What is attention?"})
    assert r1.status_code == 200          # first message: budget not yet consumed

    r2 = await client.post(f"{API}/tutor/threads/{thread_id}/messages",
                           json={"text": "And multi-head?"})
    assert r2.status_code == 429
    assert "budget" in r2.json()["detail"].lower()


async def test_disabled_returns_503(client, monkeypatch):
    from neuraforge.core.config import get_settings
    monkeypatch.setattr(get_settings(), "ember_enabled", False)
    thread_id = await _make_thread(client)
    r = await client.post(f"{API}/tutor/threads/{thread_id}/messages",
                          json={"text": "hello"})
    assert r.status_code == 503


async def test_thread_isolation_and_delete(client):
    thread_id = await _make_thread(client)
    # another user's thread must 404 — simulate by random id
    r = await client.post(
        f"{API}/tutor/threads/00000000-0000-7000-8000-000000000000/messages",
        json={"text": "hi"},
    )
    assert r.status_code == 404

    r = await client.delete(f"{API}/tutor/threads/{thread_id}")
    assert r.status_code == 204
    r = await client.get(f"{API}/tutor/threads")
    assert all(t["id"] != thread_id for t in r.json())
