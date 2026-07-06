"""Neutral behavior vocabulary for extension command frontmatter."""

from __future__ import annotations

from copy import deepcopy


BEHAVIOR_KEYS: frozenset[str] = frozenset(
    {
        "execution",
        "capability",
        "effort",
        "tools",
        "invocation",
        "visibility",
        "color",
    }
)

_TRANSLATIONS: dict[str, dict[str, dict[str, tuple[str | None, object]]]] = {
    "claude": {
        "execution": {
            "isolated": ("context", "fork"),
            "command": (None, None),
            "agent": (None, None),
        },
        "capability": {
            "fast": ("model", "claude-haiku-4-5-20251001"),
            "balanced": ("model", "claude-sonnet-4-6"),
            "strong": ("model", "claude-opus-4-6"),
        },
        "effort": {
            "low": ("effort", "low"),
            "medium": ("effort", "medium"),
            "high": ("effort", "high"),
            "max": ("effort", "max"),
        },
        "tools": {
            "none": ("allowed-tools", ""),
            "read-only": ("allowed-tools", "Read Grep Glob"),
            "write": ("allowed-tools", "Read Write Edit Grep Glob"),
            "full": (None, None),
        },
        "invocation": {
            "explicit": ("disable-model-invocation", True),
            "automatic": ("disable-model-invocation", False),
        },
        "visibility": {
            "user": ("user-invocable", True),
            "model": ("user-invocable", False),
            "both": (None, None),
        },
    },
    "copilot": {
        "execution": {
            "agent": ("mode", "agent"),
            "isolated": ("mode", "agent"),
            "command": (None, None),
        },
        "capability": {
            "fast": ("model", "Claude Haiku 4.5"),
            "balanced": ("model", "Claude Sonnet 4.5"),
            "strong": ("model", "Claude Opus 4.5"),
        },
        "tools": {
            "none": ("tools", []),
            "read-only": ("tools", ["read_file", "list_directory", "search_files"]),
            "write": ("tools", ["*"]),
            "full": ("tools", ["*"]),
        },
        "invocation": {
            "explicit": ("disable-model-invocation", True),
            "automatic": ("disable-model-invocation", False),
        },
        "visibility": {
            "user": ("user-invocable", True),
            "model": ("user-invocable", False),
            "both": (None, None),
        },
    },
    "codex": {
        "effort": {
            "low": ("effort", "low"),
            "medium": ("effort", "medium"),
            "high": ("effort", "high"),
            "max": ("effort", "max"),
        },
    },
}


def translate_behavior(
    agent_name: str,
    behavior: dict,
    agents_overrides: dict | None = None,
) -> dict:
    """Translate neutral behavior fields into agent-specific frontmatter."""
    result: dict = {}
    agent_table = _TRANSLATIONS.get(agent_name, {})

    for key, value in behavior.items():
        if key not in BEHAVIOR_KEYS:
            continue

        if key == "color" and agent_name == "claude":
            result["color"] = str(value)
            continue

        if key == "tools" and agent_name == "claude":
            if isinstance(value, list):
                result["allowed-tools"] = " ".join(str(tool) for tool in value)
                continue
            preset = agent_table.get("tools", {}).get(str(value))
            if preset is None:
                result["allowed-tools"] = str(value)
                continue
            frontmatter_key, frontmatter_value = preset
            if frontmatter_key is not None:
                result[frontmatter_key] = frontmatter_value
            continue

        key_table = agent_table.get(key, {})
        frontmatter_key, frontmatter_value = key_table.get(str(value), (None, None))
        if frontmatter_key is not None:
            result[frontmatter_key] = frontmatter_value

    if agents_overrides and isinstance(agents_overrides, dict):
        override = agents_overrides.get(agent_name)
        if isinstance(override, dict):
            result.update(override)

    return result


def strip_behavior_keys(frontmatter: dict) -> dict:
    """Return frontmatter without neutral behavior control blocks."""
    result = deepcopy(frontmatter)
    result.pop("behavior", None)
    result.pop("agents", None)
    return result


def get_deployment_type(frontmatter: dict) -> str:
    """Return the requested deployment type for behavior-aware renderers."""
    behavior = frontmatter.get("behavior")
    if isinstance(behavior, dict) and behavior.get("execution") == "agent":
        return "agent"
    return "command"

