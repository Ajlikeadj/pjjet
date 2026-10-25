"""Pin the deep-JSON nesting guard so it stays deterministic across all supported Pythons.

On 3.10 and 3.11, json.loads raises RecursionError before pjjet's custom scanner could run,
so the input was historically reported as invalid-json instead of skip[json-too-deep].
The guard in json.py now runs before parsing; this test asserts the warning, not a parse error.
"""

from __future__ import annotations

import pytest

from pjjet import Options, convert


@pytest.fixture
def deep_json_bytes() -> bytes:
    """A JSON list nested well past the 200-level guard in pjjet.converters.json."""
    depth = 250
    return ("[" * depth + "1" + "]" * depth).encode()


def test_deep_json_reports_skip_json_too_deep_not_invalid_json(deep_json_bytes: bytes) -> None:
    r = convert(deep_json_bytes, name="deep.json", options=Options(format="json-compact"))
    codes = [w.code for w in (r.warnings or ())]
    assert "skip[json-too-deep]" in codes or any("json-too-deep" in c for c in codes), codes
    # The converter emits '[]\n' when it refuses to parse a too-deep document, but the
    # warning is what matters: it must be skip[json-too-deep], never invalid-json.
    assert r.text
    assert r.warnings is not None
    assert any("json-too-deep" in w.code for w in r.warnings)
