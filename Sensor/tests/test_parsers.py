"""Tests for ADR Sensor parsers."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from adr_sensor.parsers.claude_parser import ClaudeParser
from adr_sensor.parsers.cline_parser import ClineParser
from adr_sensor.parsers.codex_parser import CodexParser


class TestClaudeParser:
    def test_parse_jsonl_file(self, tmp_path):
        """Test parsing a JSONL file with Claude Code format."""
        jsonl_file = tmp_path / "test.jsonl"
        messages = [
            {
                "type": "user",
                "sessionId": "session1",
                "timestamp": "2025-06-15T10:00:00Z",
                "message": {"content": "Help me write a function"},
            },
            {
                "type": "assistant",
                "sessionId": "session1",
                "timestamp": "2025-06-15T10:00:01Z",
                "message": {
                    "model": "claude-sonnet-4-20250514",
                    "content": [
                        {"type": "text", "text": "Sure! Here's a function:"},
                        {
                            "type": "tool_use",
                            "id": "tool1",
                            "name": "write_file",
                            "input": {"path": "main.py", "content": "def hello(): pass"},
                        },
                    ],
                },
            },
            {
                "type": "user",
                "sessionId": "session1",
                "timestamp": "2025-06-15T10:00:02Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tool1",
                            "content": "File written successfully",
                        }
                    ]
                },
            },
        ]
        with open(jsonl_file, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg) + "\n")

        parser = ClaudeParser()
        entries = parser.parse_jsonl_file(jsonl_file)

        assert len(entries) == 1
        entry = entries[0]
        assert entry.source == "claude"
        assert entry.session_id == "claude_session1"
        assert entry.model == "claude-sonnet-4-20250514"
        assert len(entry.chat_history) >= 1

    def test_parse_empty_file(self, tmp_path):
        """Test parsing an empty file."""
        jsonl_file = tmp_path / "empty.jsonl"
        jsonl_file.write_text("")

        parser = ClaudeParser()
        entries = parser.parse_jsonl_file(jsonl_file)
        assert len(entries) == 0

    def test_parse_all_no_directory(self):
        """Test parse_all when directory doesn't exist."""
        parser = ClaudeParser()
        parser.base_path = Path("/nonexistent/path")
        entries = parser.parse_all()
        assert entries == []

    def test_truncate_large_arguments(self):
        """Test that large arguments are truncated."""
        parser = ClaudeParser()
        args = {"short": "hello", "long": "x" * 2000}
        result = parser._truncate_large_arguments(args)
        assert result["short"] == "hello"
        assert len(result["long"]) < 2000
        assert "[truncated" in result["long"]


class TestClineParser:
    def test_parse_cline_log(self, tmp_path):
        """Test parsing a Cline task directory."""
        task_dir = tmp_path / "1234567890"
        task_dir.mkdir()

        conversation = [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Create a hello world script"}],
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "I'll create that for you."},
                ],
            },
        ]

        api_file = task_dir / "api_conversation_history.json"
        with open(api_file, "w") as f:
            json.dump(conversation, f)

        parser = ClineParser()
        entry = parser.parse_cline_log(task_dir)

        assert entry is not None
        assert entry.source == "cline"
        assert len(entry.chat_history) == 2

    def test_extract_mcp_tools(self):
        """Test MCP tool extraction from text."""
        parser = ClineParser()
        text = """
        <use_mcp_tool>
        <server_name>my-server</server_name>
        <tool_name>query_database</tool_name>
        <arguments>{"query": "SELECT * FROM users"}</arguments>
        </use_mcp_tool>
        """
        tools = parser.extract_mcp_tools(text)
        assert len(tools) == 1
        assert tools[0].tool_name == "query_database"
        assert tools[0].server_name == "my-server"
        assert tools[0].tool_type == "mcp_tool"

    def test_parse_no_directory(self):
        """Test parse_all when directory doesn't exist."""
        parser = ClineParser()
        parser.base_path = Path("/nonexistent/path")
        entries = parser.parse_all()
        assert entries == []


class TestCodexParser:
    def test_parse_jsonl_file(self, tmp_path):
        """Test parsing a Codex CLI JSONL file."""
        jsonl_file = tmp_path / "rollout-001.jsonl"
        events = [
            {"type": "session_meta", "payload": {"id": "sess1", "timestamp": "2025-06-15T10:00:00Z", "cwd": "/tmp"}},
            {"type": "turn_context", "payload": {"model": "o3-mini"}},
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "List all Python files"}],
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "call_id": "call1",
                    "name": "shell",
                    "arguments": '{"command": "find . -name \\"*.py\\""}',
                },
            },
            {
                "type": "response_item",
                "payload": {"type": "function_call_output", "call_id": "call1", "output": "main.py\ntest.py"},
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "Found 2 Python files."}],
                },
            },
        ]
        with open(jsonl_file, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        parser = CodexParser()
        entry = parser.parse_jsonl_file(jsonl_file)

        assert entry is not None
        assert entry.source == "codex"
        assert entry.session_id == "codex_sess1"
        assert entry.model == "o3-mini"
        assert len(entry.chat_history) >= 2

        # Check that tool was parsed
        assistant_msgs = [m for m in entry.chat_history if m.role == "assistant"]
        has_tools = any(len(m.tools) > 0 for m in assistant_msgs)
        assert has_tools

    def test_parse_no_directory(self):
        """Test parse_all when directory doesn't exist."""
        parser = CodexParser()
        parser.base_path = Path("/nonexistent/path")
        entries = parser.parse_all()
        assert entries == []
