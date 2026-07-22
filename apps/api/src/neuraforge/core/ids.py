import os
import time
import uuid

_last: tuple[int, int] = (0, 0)


def uuid7() -> uuid.UUID:
    """Time-ordered UUIDv7 (RFC 9562) — index-friendly PKs per DATABASE.md §1."""
    global _last
    ms = time.time_ns() // 1_000_000
    seq = _last[1] + 1 if ms == _last[0] else 0
    _last = (ms, seq)

    rand = int.from_bytes(os.urandom(8))
    value = (
        (ms & 0xFFFFFFFFFFFF) << 80
        | 0x7 << 76
        | (seq & 0xFFF) << 64
        | 0x2 << 62
        | (rand & 0x3FFFFFFFFFFFFFFF)
    )
    return uuid.UUID(int=value)
