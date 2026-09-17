#!/usr/bin/env python3
"""Unit tests for spec-advance decision logic (no network)."""
import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader("spec_advance", str(ROOT / "scripts" / "spec-advance.py"))
spec = importlib.util.spec_from_loader("spec_advance", loader)
assert spec is not None
sa = importlib.util.module_from_spec(spec)
sys.modules["spec_advance"] = sa
loader.exec_module(sa)


def card(status, agents=None):
    return {
        "task_project": [{"task_status": {"title": status}}],
        "task_agent_assignee": agents or [],
    }


PLANNER_DONE = [{"name": "Factory Planner", "status": "done"}]
PLANNER_STAGED = [{"name": "Factory Planner", "status": "staged"}]
PLANNER_FAILED = [{"name": "Factory Planner", "status": "failed"}]
TESTER_STAGED = [{"name": "Factory Tester", "status": "staged"}]


class TestDecide(unittest.TestCase):
    def test_fresh_todo_dispatches_spec(self):
        self.assertEqual(sa.decide(card("TO DO"), None), "dispatch-spec")

    def test_todo_planner_present_needs_checklist(self):
        self.assertEqual(sa.decide(card("TO DO", PLANNER_STAGED), None), "need-checklist")
        self.assertEqual(sa.decide(card("TO DO", PLANNER_DONE), None), "need-checklist")

    def test_todo_planner_with_criteria_advances_any_alive_status(self):
        # API-created assignments stay 'staged' after finishing (verified Sep 17)
        self.assertEqual(sa.decide(card("TO DO", PLANNER_STAGED), 3), "advance")
        self.assertEqual(sa.decide(card("TO DO", PLANNER_DONE), 3), "advance")

    def test_todo_planner_no_criteria_waits(self):
        self.assertIsNone(sa.decide(card("TO DO", PLANNER_STAGED), 0))

    def test_todo_planner_failed_never_advances(self):
        self.assertIsNone(sa.decide(card("TO DO", PLANNER_FAILED), 3))
        self.assertIsNone(sa.decide(card("TO DO", PLANNER_FAILED), None))

    def test_in_review_fresh_dispatches_review(self):
        self.assertEqual(sa.decide(card("IN REVIEW"), None), "dispatch-review")

    def test_in_review_with_planner_row_only_still_dispatches(self):
        # the spec-lane planner row persists on the card; review dispatch keys off the tester row
        self.assertEqual(sa.decide(card("IN REVIEW", PLANNER_DONE), None), "dispatch-review")

    def test_in_review_tester_present_waits(self):
        self.assertIsNone(sa.decide(card("IN REVIEW", PLANNER_DONE + TESTER_STAGED), None))

    def test_non_open_states_ignored(self):
        for st in ("READY", "IN PROGRESS", "COMPLETE", ""):
            self.assertIsNone(sa.decide(card(st, PLANNER_DONE), 3), st)


if __name__ == "__main__":
    unittest.main(verbosity=2)
