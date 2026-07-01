"""
IT Help Desk ADK Agent

Entry point for the Google Agent Development Kit (ADK) agent.
The agent uses Gemini via the ADK framework and calls the Phase 2
IT Help Desk API (deployed on Cloud Run) through its registered tools.

Environment variables
---------------------
API_BASE_URL        URL of the Phase 2 API (required in production).
                    Example: https://it-help-desk-api-xxxxx-uc.a.run.app
GOOGLE_CLOUD_PROJECT  GCP project ID (used by the ADK runtime).
GOOGLE_API_KEY      Gemini API key when running outside GCP (local dev).
"""

from google.adk.agents import Agent

from .prompts import AGENT_INSTRUCTION
from .tools import (
    add_comment,
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
)

root_agent = Agent(
    name="it_help_desk_agent",
    model="gemini-2.0-flash",
    description=(
        "An IT Help Desk agent that manages support tickets "
        "through the IT Help Desk REST API."
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[
        list_tickets,
        get_ticket,
        create_ticket,
        update_ticket,
        add_comment,
    ],
)
