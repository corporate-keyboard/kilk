#!/usr/bin/env python3
"""Kilk server.

A read-only MCP that exposes the Subby project's documentation
(overview, features, roadmap, glossary, tech stack, personas, data model)
as MCP resources and a small set of search/fetch tools.

Intended for LLM agents that need grounded context about Subby — what it is,
who it's for, what's in v1 vs. later phases, and the working tech choices.
"""

from __future__ import annotations

import json
import re
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# project_info ships alongside the package — see pyproject force-include.
_PACKAGE_DIR = Path(__file__).resolve().parent
_CANDIDATE_DIRS = [
    _PACKAGE_DIR / "project_info",       # installed layout
    _PACKAGE_DIR.parent / "project_info", # repo / editable layout
]
PROJECT_INFO_DIR: Path = next(
    (p for p in _CANDIDATE_DIRS if p.is_dir()),
    _CANDIDATE_DIRS[0],
)

# Friendly section -> filename map. Drives `list_sections` and `get_section`.
SECTIONS: Dict[str, str] = {
    "overview": "overview.md",
    "features": "features.md",
    "roadmap": "roadmap.md",
    "glossary": "glossary.md",
    "tech_stack": "tech_stack.md",
    "personas": "personas.md",
    "data_model": "data_model.md",
}

SECTION_TITLES: Dict[str, str] = {
    "overview": "Project overview, problem, target users, success metrics",
    "features": "Feature surface and v1 prioritisation",
    "roadmap": "Phase-by-phase delivery plan and explicit non-goals",
    "glossary": "Domain vocabulary (venue, tab, stamp, etc.)",
    "tech_stack": "Working tech choices and open questions",
    "personas": "Operator and diner personas",
    "data_model": "Sketch of core entities and relationships",
}

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("kilk")


# ---------------------------------------------------------------------------
# Enums and input models
# ---------------------------------------------------------------------------


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


SectionName = Enum(  # type: ignore[misc]
    "SectionName",
    {k.upper(): k for k in SECTIONS},
    type=str,
)


class GetSectionInput(BaseModel):
    """Input for `get_section`."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    section: SectionName = Field(  # type: ignore[valid-type]
        ...,
        description=(
            "Which section of the Subby docs to return. "
            "One of: overview, features, roadmap, glossary, tech_stack, personas, data_model."
        ),
    )


class SearchDocsInput(BaseModel):
    """Input for `search_docs`."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    query: str = Field(
        ...,
        description=(
            "Case-insensitive search term. Matches substrings inside Subby's docs "
            "(e.g., 'stripe', 'loyalty', 'booking deposit'). 2-200 chars."
        ),
        min_length=2,
        max_length=200,
    )
    limit: int = Field(
        default=10,
        description="Maximum matching snippets to return.",
        ge=1,
        le=50,
    )
    context_chars: int = Field(
        default=120,
        description="How many characters of surrounding context to include on each side of a match.",
        ge=0,
        le=500,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable, 'json' for structured.",
    )

    @field_validator("query")
    @classmethod
    def _query_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query cannot be empty or whitespace only")
        return v


class GlossaryLookupInput(BaseModel):
    """Input for `glossary_lookup`."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    term: str = Field(
        ...,
        description="Term to look up in the Subby glossary (e.g., 'tab', 'GPV', 'shift').",
        min_length=1,
        max_length=80,
    )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _read_section_file(section: str) -> str:
    """Read a section file. Raises FileNotFoundError if missing."""
    filename = SECTIONS[section]
    path = PROJECT_INFO_DIR / filename
    return path.read_text(encoding="utf-8")


def _all_sections_text() -> Dict[str, str]:
    """Load every section's text. Missing files are skipped with a warning marker."""
    out: Dict[str, str] = {}
    for key in SECTIONS:
        try:
            out[key] = _read_section_file(key)
        except FileNotFoundError:
            out[key] = f"[missing file: {SECTIONS[key]}]"
    return out


def _section_value(section: SectionName) -> str:  # type: ignore[valid-type]
    """Extract the underlying string from a SectionName enum or raw str."""
    return section.value if hasattr(section, "value") else str(section)


# ---------------------------------------------------------------------------
# Resources — expose each doc at a stable URI
# ---------------------------------------------------------------------------


@mcp.resource("subby://docs/{section}")
def doc_resource(section: str) -> str:
    """Return the raw markdown for a Subby docs section.

    URI template: ``subby://docs/{section}`` where section is one of:
    overview, features, roadmap, glossary, tech_stack, personas, data_model.
    """
    if section not in SECTIONS:
        raise ValueError(
            f"Unknown section '{section}'. Valid sections: {sorted(SECTIONS)}"
        )
    try:
        return _read_section_file(section)
    except FileNotFoundError as exc:
        raise ValueError(f"Section file missing on disk: {exc}") from exc


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="list_sections",
    annotations={
        "title": "List Subby docs sections",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def list_sections() -> str:
    """List every documentation section this MCP exposes.

    Use this first to discover what's available before calling `get_section`
    or `search_docs`.

    Returns:
        str: JSON string with shape:
            {
              "sections": [
                {"name": "overview",  "title": "...", "resource_uri": "subby://docs/overview"},
                ...
              ]
            }
    """
    sections = [
        {
            "name": name,
            "title": SECTION_TITLES[name],
            "resource_uri": f"subby://docs/{name}",
        }
        for name in SECTIONS
    ]
    return json.dumps({"sections": sections}, indent=2)


@mcp.tool(
    name="get_section",
    annotations={
        "title": "Get a Subby docs section",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def get_section(params: GetSectionInput) -> str:
    """Return the full markdown text of one Subby docs section.

    Args:
        params (GetSectionInput): Validated input containing:
            - section (SectionName): which section to read.

    Returns:
        str: The raw markdown contents of the section, or an error string
        beginning with 'Error:' if the file is missing.
    """
    section = _section_value(params.section)
    try:
        return _read_section_file(section)
    except FileNotFoundError:
        return (
            f"Error: section file '{SECTIONS[section]}' not found. "
            f"Expected at {PROJECT_INFO_DIR}."
        )


@mcp.tool(
    name="search_docs",
    annotations={
        "title": "Search Subby docs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def search_docs(params: SearchDocsInput) -> str:
    """Search every Subby docs section for a substring and return matching snippets.

    Case-insensitive substring match. Returns up to `limit` snippets, each with
    `context_chars` characters of surrounding context.

    Args:
        params (SearchDocsInput): Validated input containing:
            - query (str): search term.
            - limit (int): max snippets.
            - context_chars (int): context window per match.
            - response_format ('markdown' | 'json').

    Returns:
        str: Markdown bullet list of matches, or a JSON object:
        {
          "query": str,
          "total_matches": int,
          "returned": int,
          "matches": [
            {"section": str, "line": int, "snippet": str},
            ...
          ]
        }
        If nothing matches, returns "No matches for '<query>'".
    """
    query = params.query.strip()
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    matches: List[dict] = []
    for section, text in _all_sections_text().items():
        for m in pattern.finditer(text):
            start = max(0, m.start() - params.context_chars)
            end = min(len(text), m.end() + params.context_chars)
            snippet = text[start:end].replace("\n", " ").strip()
            line_no = text.count("\n", 0, m.start()) + 1
            matches.append(
                {
                    "section": section,
                    "line": line_no,
                    "snippet": snippet,
                }
            )
            if len(matches) >= params.limit:
                break
        if len(matches) >= params.limit:
            break

    if not matches:
        return f"No matches for '{query}'"

    if params.response_format == ResponseFormat.JSON:
        return json.dumps(
            {
                "query": query,
                "total_matches": len(matches),
                "returned": len(matches),
                "matches": matches,
            },
            indent=2,
        )

    lines = [f"# Search results for '{query}' ({len(matches)} match(es))", ""]
    for m in matches:
        lines.append(f"- **{m['section']}** (line {m['line']}): {m['snippet']}")
    return "\n".join(lines)


@mcp.tool(
    name="glossary_lookup",
    annotations={
        "title": "Look up a Subby glossary term",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def glossary_lookup(params: GlossaryLookupInput) -> str:
    """Look up a single term in the Subby glossary.

    Args:
        params (GlossaryLookupInput): Validated input containing:
            - term (str): glossary term to look up (case-insensitive).

    Returns:
        str: The matching glossary line(s), or "No glossary entry for '<term>'".
    """
    try:
        glossary_text = _read_section_file("glossary")
    except FileNotFoundError:
        return "Error: glossary file is missing."

    term = params.term.strip().lower()
    hits: List[str] = []
    for line in glossary_text.splitlines():
        # Glossary entries look like:  - **Tab** — A short description.
        stripped = line.strip()
        if not stripped.startswith("- **"):
            continue
        # Pull the term out of the bold-wrapped prefix.
        try:
            head, _ = stripped.split("**", 2)[1:3]
        except ValueError:
            continue
        if term in head.lower():
            hits.append(stripped)

    if not hits:
        return f"No glossary entry for '{params.term}'"
    return "\n".join(hits)


@mcp.tool(
    name="project_summary",
    annotations={
        "title": "Subby project summary",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def project_summary() -> str:
    """Return a compact, agent-friendly summary of the Subby project.

    Useful as a single warmup call when an agent first connects, so it can
    decide whether to drill into a specific section.

    Returns:
        str: JSON with name, one-liner, sections list, and v1 feature priority.
    """
    try:
        overview = _read_section_file("overview")
    except FileNotFoundError:
        overview = ""

    one_liner = ""
    for line in overview.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.lower().startswith("## "):
            one_liner = line
            break

    return json.dumps(
        {
            "name": "Subby",
            "one_liner": one_liner
            or "All-in-one ops platform for local hospitality venues.",
            "sections": [
                {"name": k, "title": SECTION_TITLES[k]} for k in SECTIONS
            ],
            "v1_feature_priority": [
                "Menu hosting + QR",
                "Payments (Stripe only)",
                "Bookings",
                "Loyalty (stamp mode only)",
                "Operator dashboard",
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Kilk server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
