import json
from pathlib import Path

from app.jira.parsers import flatten_changelog_events


def test_flatten_changelog_includes_created_and_project_moved() -> None:
    fixture = Path("tests/fixtures/sample_issue.json")
    issue = json.loads(fixture.read_text(encoding="utf-8"))
    issue["changelog"] = {
        "histories": [
            {
                "id": "20001",
                "created": "2026-03-03T12:00:00.000+0000",
                "author": {"accountId": "abc123"},
                "items": [
                    {"field": "project", "fromString": "EIT", "toString": "ABC"},
                ],
            }
        ]
    }
    issue["fields"]["project"] = {"key": "EIT"}

    events = flatten_changelog_events(issue, run_id=10)

    assert events[0]["event_type"] == "created"
    moved = [e for e in events if e["event_type"] == "project_moved"]
    assert len(moved) == 1
    assert moved[0]["from_project_key"] == "EIT"
    assert moved[0]["to_project_key"] == "ABC"
