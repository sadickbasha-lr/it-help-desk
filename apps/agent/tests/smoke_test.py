"""
Smoke test — runs against a live API_BASE_URL.

Usage
-----
    API_BASE_URL=https://your-cloud-run-url.run.app python tests/smoke_test.py

The script exits with code 0 on success and 1 on any failure.
"""

import os
import sys

# Add parent directory to path so we can import tools without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Stub google.adk so we can import tools without ADK installed
import types
for mod_name in ("google", "google.adk", "google.adk.agents"):
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)
if not hasattr(sys.modules["google.adk.agents"], "Agent"):
    class _Agent:
        def __init__(self, *args, **kwargs): pass
    sys.modules["google.adk.agents"].Agent = _Agent

import tools  # noqa: E402

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"
failures = []


def check(label, result):
    if isinstance(result, dict) and "error" in result:
        print(f"  {FAIL}  {label}: {result['error']}")
        failures.append(label)
    else:
        print(f"  {PASS}  {label}")
    return result


print(f"\nSmoking-testing tools against: {tools.API_BASE_URL}\n")

# 1. list_tickets
result = check("list_tickets()", tools.list_tickets())

# 2. create_ticket
new_ticket = check(
    "create_ticket()",
    tools.create_ticket(
        title="Smoke test ticket",
        description="Created by automated smoke test — safe to close.",
        priority="low",
    ),
)

# 3. get_ticket (uses the ticket we just created, or ticket 1 as fallback)
ticket_id = new_ticket.get("id") if isinstance(new_ticket, dict) and "id" in new_ticket else 1
check(f"get_ticket({ticket_id})", tools.get_ticket(ticket_id))

# 4. add_comment
check(
    f"add_comment({ticket_id})",
    tools.add_comment(ticket_id, "Smoke test comment — safe to delete."),
)

# 5. update_ticket
check(
    f"update_ticket({ticket_id}, status='closed')",
    tools.update_ticket(ticket_id, status="closed"),
)

print()
if failures:
    print(f"FAILED: {len(failures)} check(s) failed: {', '.join(failures)}")
    sys.exit(1)
else:
    print("All smoke tests passed.")
    sys.exit(0)
