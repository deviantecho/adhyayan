import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api.main as api_main


class StreamingControlFlowTests(unittest.TestCase):
    def test_streaming_request_only_calls_stream_generator_once(self):
        calls = []

        def fake_stream(question, chat_history, subject_filter):
            calls.append({
                "question": question,
                "history_before": list(chat_history),
                "subject_filter": subject_filter,
            })
            chat_history.append({"role": "user", "content": question})
            chat_history.append({"role": "assistant", "content": "A response."})
            yield {"type": "content", "content": "A response."}
            yield {
                "type": "done",
                "updated_history": chat_history,
                "answer": {
                    "keyIdea": "A concept.",
                    "explanation": "An explanation.",
                    "blocks": [],
                    "sources": [],
                    "retrievalDetails": [],
                },
            }

        with (
            patch.object(api_main, "llm_provider", object()),
            patch.object(api_main, "index", object()),
            patch.object(api_main, "chunks", [object()]),
            patch.object(
                api_main,
                "ask_question",
                side_effect=AssertionError(
                    "ask_question must not run for a streaming request"
                ),
            ) as non_streaming,
            patch.object(api_main, "ask_question_stream", side_effect=fake_stream) as streaming,
        ):
            response = TestClient(api_main.app).post(
                "/api/chat",
                json={
                    "message": "A generic question?",
                    "chat_history": [],
                    "subject_filter": "All Subjects",
                    "stream": True,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(non_streaming.call_count, 0)
        self.assertEqual(streaming.call_count, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["history_before"], [])

        events = [
            json.loads(line[6:])
            for line in response.text.splitlines()
            if line.startswith("data: ")
        ]
        done = next(event for event in events if event["type"] == "done")
        self.assertEqual(len(done["updated_history"]), 2)
        self.assertEqual(
            [message["role"] for message in done["updated_history"]],
            ["user", "assistant"],
        )


if __name__ == "__main__":
    unittest.main()
