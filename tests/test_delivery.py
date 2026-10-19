"""Delivery timing and CLI routing, without API calls or credentials."""

import os
import sys
import types
import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch

# Timing tests do not need the optional OpenAI SDK installed locally.
with patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=Mock())}):
    import daily_brief as brief


class DeliveryTimingTests(unittest.TestCase):
    def run_at(self, hour, minute=0, day=date(2026, 10, 19)):
        now = datetime(2026, 10, 19, hour, minute, tzinfo=brief.TIMEZONE)
        with patch.object(brief, "datetime") as clock, patch.object(brief.time, "sleep") as sleep:
            clock.now.return_value = now
            clock.combine.side_effect = datetime.combine
            brief.wait_until_delivery_time(day)
            return sleep

    def test_early_trigger_waits_until_ten(self):
        self.run_at(4, 7).assert_called_once_with(5 * 3600 + 53 * 60)

    def test_at_target_sends_immediately(self):
        self.run_at(10).assert_not_called()

    def test_delayed_trigger_after_noon_sends_immediately(self):
        self.run_at(12, 30).assert_not_called()

    def test_previous_day_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "previous day"):
            self.run_at(0, 5, day=date(2026, 10, 18))

    def test_wait_crossing_midnight_is_rejected(self):
        with patch.object(brief, "datetime") as clock, patch.object(brief.time, "sleep"):
            clock.now.side_effect = [
                datetime(2026, 10, 19, 9, tzinfo=brief.TIMEZONE),
                datetime(2026, 10, 20, 0, tzinfo=brief.TIMEZONE),
            ]
            clock.combine.side_effect = datetime.combine
            with self.assertRaisesRegex(RuntimeError, "previous day"):
                brief.wait_until_delivery_time(date(2026, 10, 19))


class CommandTests(unittest.TestCase):
    def run_command(self, mode, event="workflow_dispatch"):
        argv = ["daily_brief.py", mode]
        with (
            patch.object(sys, "argv", argv),
            patch.dict(os.environ, {"GITHUB_EVENT_NAME": event}),
            patch.object(brief, "research", return_value="Today's briefing") as research,
            patch.object(brief, "wait_until_delivery_time") as waiting,
            patch.object(brief, "send_telegram") as send,
        ):
            brief.main()
            return research, waiting, send

    def test_scheduled_run_waits_then_sends(self):
        calls = Mock()
        with (
            patch.object(sys, "argv", ["daily_brief.py", "send"]),
            patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule"}),
            patch.object(brief, "research", return_value="Today's briefing") as research,
            patch.object(brief, "wait_until_delivery_time") as waiting,
            patch.object(brief, "send_telegram") as send,
        ):
            calls.attach_mock(research, "research")
            calls.attach_mock(waiting, "wait")
            calls.attach_mock(send, "send")
            brief.main()
        self.assertEqual([c[0] for c in calls.mock_calls], ["research", "wait", "send"])
        send.assert_called_once_with("Today's briefing")

    def test_manual_send_is_immediate(self):
        _, waiting, send = self.run_command("send")
        waiting.assert_not_called()
        send.assert_called_once()

    def test_github_schedule_waits(self):
        _, waiting, send = self.run_command("send", event="schedule")
        waiting.assert_called_once()
        send.assert_called_once()

    def test_preview_never_sends_or_waits(self):
        research, waiting, send = self.run_command("preview", event="schedule")
        research.assert_called_once()
        waiting.assert_not_called()
        send.assert_not_called()

    def test_telegram_test_does_not_research_or_wait(self):
        research, waiting, send = self.run_command("test", event="schedule")
        research.assert_not_called()
        waiting.assert_not_called()
        send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
