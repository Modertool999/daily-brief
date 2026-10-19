"""Research validation and CLI routing, without API calls or credentials."""

import os
import sys
import types
import unittest
from unittest.mock import Mock, patch

# Timing tests do not need the optional OpenAI SDK installed locally.
with patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=Mock())}):
    import daily_brief as brief


class CommandTests(unittest.TestCase):
    def run_command(self, mode, event="workflow_dispatch"):
        argv = ["daily_brief.py", mode]
        with (
            patch.object(sys, "argv", argv),
            patch.dict(os.environ, {"GITHUB_EVENT_NAME": event}),
            patch.object(brief, "research", return_value="Today's briefing") as research,
            patch.object(brief, "send_telegram") as send,
        ):
            brief.main()
            return research, send

    def test_scheduled_run_researches_then_sends(self):
        calls = Mock()
        with (
            patch.object(sys, "argv", ["daily_brief.py", "send"]),
            patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule"}),
            patch.object(brief, "research", return_value="Today's briefing") as research,
            patch.object(brief, "send_telegram") as send,
        ):
            calls.attach_mock(research, "research")
            calls.attach_mock(send, "send")
            brief.main()
        self.assertEqual([c[0] for c in calls.mock_calls], ["research", "send"])
        send.assert_called_once_with("Today's briefing")

    def test_manual_send_is_immediate(self):
        _, send = self.run_command("send")
        send.assert_called_once()

    def test_github_schedule_sends(self):
        _, send = self.run_command("send", event="schedule")
        send.assert_called_once()

    def test_preview_never_sends(self):
        research, send = self.run_command("preview", event="schedule")
        research.assert_called_once()
        send.assert_not_called()

    def test_telegram_test_does_not_research(self):
        research, send = self.run_command("test", event="schedule")
        research.assert_not_called()
        send.assert_called_once()


class ResearchTests(unittest.TestCase):
    def research_result(self, status="completed", message="Briefing"):
        result = types.SimpleNamespace(status=status, output_text=message)
        with (
            patch.dict(os.environ, {"DAILY_BRIEF_PROMPT": "Brief for {DATE}"}),
            patch.object(brief, "OpenAI") as client,
        ):
            client.return_value.responses.create.return_value = result
            return brief.research()

    def test_complete_briefing(self):
        self.assertEqual(self.research_result(), "Briefing")

    def test_partial_output_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Research incomplete"):
            self.research_result(status="incomplete")

    def test_invalid_message_is_rejected(self):
        for message in ("", " " * 10, "x" * 1201):
            with self.subTest(length=len(message)), self.assertRaises(RuntimeError):
                self.research_result(message=message)

    def test_telegram_error_does_not_expose_token(self):
        with (
            patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "secret", "TELEGRAM_CHAT_ID": "123"}),
            patch.object(brief.urllib.request, "urlopen", side_effect=OSError("URL contains secret")),
        ):
            with self.assertRaises(RuntimeError) as error:
                brief.send_telegram("Briefing")
            self.assertNotIn("secret", str(error.exception))
            self.assertTrue(error.exception.__suppress_context__)


if __name__ == "__main__":
    unittest.main()
