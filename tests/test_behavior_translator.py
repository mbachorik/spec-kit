"""Tests for neutral extension behavior frontmatter translation."""

import pytest

from specify_cli.behavior import (
    get_deployment_type,
    strip_behavior_keys,
    translate_behavior,
)


@pytest.mark.parametrize(
    ("capability", "model"),
    [
        ("fast", "haiku"),
        ("balanced", "sonnet"),
        ("strong", "opus"),
    ],
)
def test_translate_claude_capability_uses_versionless_model_alias(
    capability, model
):
    assert translate_behavior("claude", {"capability": capability}) == {
        "model": model
    }


def test_translate_claude_tools_invocation_and_visibility():
    result = translate_behavior(
        "claude",
        {
            "tools": "read-only",
            "invocation": "explicit",
            "visibility": "model",
        },
    )

    assert result == {
        "allowed-tools": "Read Grep Glob",
        "disable-model-invocation": True,
        "user-invocable": False,
    }


def test_translate_claude_custom_tool_list():
    result = translate_behavior("claude", {"tools": ["Read", "Grep", "Bash"]})

    assert result == {"allowed-tools": "Read Grep Bash"}


def test_translate_copilot_tools_and_agent_override():
    result = translate_behavior(
        "copilot",
        {"tools": "read-only"},
        {"copilot": {"model": "Claude Sonnet 4.5"}},
    )

    assert result == {
        "tools": ["read_file", "list_directory", "search_files"],
        "model": "Claude Sonnet 4.5",
    }


def test_strip_behavior_keys_leaves_other_frontmatter():
    result = strip_behavior_keys(
        {
            "description": "Run a command",
            "behavior": {"tools": "read-only"},
            "agents": {"claude": {"model": "claude-opus"}},
        }
    )

    assert result == {"description": "Run a command"}


def test_get_deployment_type_reads_behavior_execution():
    assert get_deployment_type({"behavior": {"execution": "agent"}}) == "agent"
    assert get_deployment_type({"behavior": {"execution": "command"}}) == "command"
    assert get_deployment_type({}) == "command"

