"""
conftest.py — pytest configuration for apps/agent/tests.

Stubs out google-adk before any test modules are imported
so that the unit tests can run without the real ADK package installed.
"""

import sys
import types


def _stub_adk():
    for mod_name in ("google", "google.adk", "google.adk.agents"):
        if mod_name not in sys.modules:
            mod = types.ModuleType(mod_name)
            sys.modules[mod_name] = mod

    if not hasattr(sys.modules["google.adk.agents"], "Agent"):
        class _Agent:
            def __init__(self, *args, **kwargs):
                pass
        sys.modules["google.adk.agents"].Agent = _Agent


_stub_adk()
