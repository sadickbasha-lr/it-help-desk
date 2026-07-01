"""
IT Help Desk Agent Tools

Each function is an ADK tool that calls the Phase 2 API.
The API base URL is read from the API_BASE_URL environment variable.
"""

import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")


def _url(path: str) -> str:
    return f"{API_BASE_URL.rstrip('/')}{path}"


def list_tickets() -> dict:
    """List all IT help desk tickets.

    Returns:
        A dictionary with a list of tickets or an error message.
    """
    try:
        response = requests.get(_url("/tickets"), timeout=10)
        response.raise_for_status()
        return {"tickets": response.json()}
    except requests.HTTPError as exc:
        return {"error": f"API error {exc.response.status_code}: {exc.response.text}"}
    except requests.RequestException as exc:
        return {"error": str(exc)}


def get_ticket(ticket_id: int) -> dict:
    """Fetch a single IT help desk ticket by its ID.

    Args:
        ticket_id: The numeric ID of the ticket to retrieve.

    Returns:
        The ticket data as a dictionary, or an error message.
    """
    try:
        response = requests.get(_url(f"/tickets/{ticket_id}"), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        return {"error": f"API error {exc.response.status_code}: {exc.response.text}"}
    except requests.RequestException as exc:
        return {"error": str(exc)}


def create_ticket(title: str, description: str, priority: str = "medium", created_by: int = 1) -> dict:
    """Create a new IT help desk ticket.

    Args:
        title: A short summary of the issue.
        description: A detailed description of the problem.
        priority: Ticket priority — one of 'low', 'medium', 'high', or 'critical'.
            Defaults to 'medium'.
        created_by: User ID of the person raising the ticket. Defaults to 1.

    Returns:
        The newly created ticket as a dictionary, or an error message.
    """
    payload = {
        "title": title,
        "description": description,
        "priority": priority,
        "created_by": created_by,
    }
    try:
        response = requests.post(_url("/tickets"), json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        return {"error": f"API error {exc.response.status_code}: {exc.response.text}"}
    except requests.RequestException as exc:
        return {"error": str(exc)}


def update_ticket(ticket_id: int, status: str = None, priority: str = None, assigned_to: int = None) -> dict:
    """Update an existing IT help desk ticket.

    Args:
        ticket_id: The numeric ID of the ticket to update.
        status: New status value. Common values: 'open', 'in_progress', 'resolved', 'closed'.
        priority: New priority value: 'low', 'medium', 'high', or 'critical'.
        assigned_to: User ID to assign the ticket to.

    Returns:
        The updated ticket as a dictionary, or an error message.
    """
    payload = {}
    if status is not None:
        payload["status"] = status
    if priority is not None:
        payload["priority"] = priority
    if assigned_to is not None:
        payload["assigned_to"] = assigned_to

    if not payload:
        return {"error": "No fields provided to update. Provide at least one of: status, priority, assigned_to."}

    try:
        response = requests.patch(_url(f"/tickets/{ticket_id}"), json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        return {"error": f"API error {exc.response.status_code}: {exc.response.text}"}
    except requests.RequestException as exc:
        return {"error": str(exc)}


def add_comment(ticket_id: int, comment: str, user_id: int = 1) -> dict:
    """Add a comment to an existing IT help desk ticket.

    Args:
        ticket_id: The numeric ID of the ticket to comment on.
        comment: The text content of the comment.
        user_id: User ID of the person adding the comment. Defaults to 1.

    Returns:
        The created comment as a dictionary, or an error message.
    """
    payload = {
        "comment": comment,
        "user_id": user_id,
    }
    try:
        response = requests.post(_url(f"/tickets/{ticket_id}/comments"), json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        return {"error": f"API error {exc.response.status_code}: {exc.response.text}"}
    except requests.RequestException as exc:
        return {"error": str(exc)}
