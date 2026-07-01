"""
Unit tests for apps/agent/tools.py

Run with:
    cd apps/agent
    pip install -r requirements.txt pytest
    pytest tests/test_tools.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

# google.adk is stubbed in conftest.py before this module is imported
import apps.agent.tools as tools


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


def _mock_http_error(status_code, body="error"):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = body
    exc = __import__("requests").HTTPError(response=resp)
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = exc
    mock_resp.status_code = status_code
    mock_resp.text = body
    return mock_resp


# ---------------------------------------------------------------------------
# list_tickets
# ---------------------------------------------------------------------------

class TestListTickets:
    def test_success(self):
        data = [{"id": 1, "title": "Test ticket"}]
        with patch("apps.agent.tools.requests.get", return_value=_mock_response(data)):
            result = tools.list_tickets()
        assert result == {"tickets": data}

    def test_http_error(self):
        resp = MagicMock()
        resp.status_code = 500
        resp.text = "Internal Server Error"
        import requests as req_lib
        resp.raise_for_status.side_effect = req_lib.HTTPError(response=resp)
        with patch("apps.agent.tools.requests.get", return_value=resp):
            result = tools.list_tickets()
        assert "error" in result
        assert "500" in result["error"]

    def test_connection_error(self):
        import requests as req_lib
        with patch("apps.agent.tools.requests.get", side_effect=req_lib.ConnectionError("refused")):
            result = tools.list_tickets()
        assert "error" in result


# ---------------------------------------------------------------------------
# get_ticket
# ---------------------------------------------------------------------------

class TestGetTicket:
    def test_success(self):
        data = {"id": 42, "title": "Broken keyboard"}
        with patch("apps.agent.tools.requests.get", return_value=_mock_response(data)):
            result = tools.get_ticket(42)
        assert result == data

    def test_not_found(self):
        resp = MagicMock()
        resp.status_code = 404
        resp.text = "Not found"
        import requests as req_lib
        resp.raise_for_status.side_effect = req_lib.HTTPError(response=resp)
        with patch("apps.agent.tools.requests.get", return_value=resp):
            result = tools.get_ticket(999)
        assert "error" in result
        assert "404" in result["error"]


# ---------------------------------------------------------------------------
# create_ticket
# ---------------------------------------------------------------------------

class TestCreateTicket:
    def test_success_defaults(self):
        created = {"id": 5, "title": "VPN not working", "priority": "medium"}
        with patch("apps.agent.tools.requests.post", return_value=_mock_response(created, 201)):
            result = tools.create_ticket("VPN not working", "Cannot connect to VPN")
        assert result == created

    def test_custom_priority(self):
        created = {"id": 6, "title": "Server down", "priority": "critical"}
        with patch("apps.agent.tools.requests.post", return_value=_mock_response(created, 201)) as mock_post:
            result = tools.create_ticket("Server down", "Main server offline", priority="critical")
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1]["json"]
        assert payload["priority"] == "critical"

    def test_api_error(self):
        resp = MagicMock()
        resp.status_code = 422
        resp.text = "Validation error"
        import requests as req_lib
        resp.raise_for_status.side_effect = req_lib.HTTPError(response=resp)
        with patch("apps.agent.tools.requests.post", return_value=resp):
            result = tools.create_ticket("", "")
        assert "error" in result


# ---------------------------------------------------------------------------
# update_ticket
# ---------------------------------------------------------------------------

class TestUpdateTicket:
    def test_update_status(self):
        updated = {"id": 1, "status": "in_progress"}
        with patch("apps.agent.tools.requests.patch", return_value=_mock_response(updated)) as mock_patch:
            result = tools.update_ticket(1, status="in_progress")
        payload = mock_patch.call_args.kwargs.get("json") or mock_patch.call_args[1]["json"]
        assert payload == {"status": "in_progress"}
        assert result == updated

    def test_update_priority(self):
        updated = {"id": 1, "priority": "high"}
        with patch("apps.agent.tools.requests.patch", return_value=_mock_response(updated)):
            result = tools.update_ticket(1, priority="high")
        assert result == updated

    def test_update_no_fields(self):
        result = tools.update_ticket(1)
        assert "error" in result

    def test_update_multiple_fields(self):
        updated = {"id": 2, "status": "resolved", "assigned_to": 3}
        with patch("apps.agent.tools.requests.patch", return_value=_mock_response(updated)) as mock_patch:
            result = tools.update_ticket(2, status="resolved", assigned_to=3)
        payload = mock_patch.call_args.kwargs.get("json") or mock_patch.call_args[1]["json"]
        assert "status" in payload
        assert "assigned_to" in payload


# ---------------------------------------------------------------------------
# add_comment
# ---------------------------------------------------------------------------

class TestAddComment:
    def test_success(self):
        comment = {"id": 10, "comment": "Working on it", "ticket_id": 1}
        with patch("apps.agent.tools.requests.post", return_value=_mock_response(comment, 201)):
            result = tools.add_comment(1, "Working on it")
        assert result == comment

    def test_correct_url_used(self):
        comment = {"id": 11}
        with patch("apps.agent.tools.requests.post", return_value=_mock_response(comment)) as mock_post:
            tools.add_comment(7, "Test comment")
        url = mock_post.call_args[0][0]
        assert "/tickets/7/comments" in url

    def test_api_error(self):
        resp = MagicMock()
        resp.status_code = 404
        resp.text = "Ticket not found"
        import requests as req_lib
        resp.raise_for_status.side_effect = req_lib.HTTPError(response=resp)
        with patch("apps.agent.tools.requests.post", return_value=resp):
            result = tools.add_comment(999, "This ticket does not exist")
        assert "error" in result


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

class TestUrlConstruction:
    def test_base_url_respected(self, monkeypatch):
        monkeypatch.setattr(tools, "API_BASE_URL", "https://example.run.app")
        data = [{"id": 1}]
        with patch("apps.agent.tools.requests.get", return_value=_mock_response(data)) as mock_get:
            tools.list_tickets()
        assert mock_get.call_args[0][0] == "https://example.run.app/tickets"

    def test_trailing_slash_stripped(self, monkeypatch):
        monkeypatch.setattr(tools, "API_BASE_URL", "https://example.run.app/")
        data = [{"id": 1}]
        with patch("apps.agent.tools.requests.get", return_value=_mock_response(data)) as mock_get:
            tools.list_tickets()
        url = mock_get.call_args[0][0]
        assert not url.startswith("https://example.run.app//")
