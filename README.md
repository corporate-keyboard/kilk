# Kilk

A read-only **Model Context Protocol** server that exposes the Subby project's documentation — overview, features, roadmap, glossary, tech stack, personas, and data model — to any MCP-aware LLM client (Claude Desktop, Claude Code, Cursor, etc.).

## What's Subby?

Subby is an all-in-one operations platform for local hospitality venues — pubs, cafés, small restaurants — combining digital menus, payments, table bookings, and loyalty into a single product. See [`project_info/overview.md`](./project_info/overview.md).

## What this MCP gives you

**Resources**

- `subby://docs/{section}` — raw markdown for each section.

**Tools**

- `list_sections` — enumerate available docs.
- `get_section` — fetch one section in full.
- `search_docs` — case-insensitive substring search across every section.
- `glossary_lookup` — single-term glossary lookup.
- `project_summary` — compact JSON summary, good as a warmup call.

All tools are read-only and side-effect-free.

## Install

Requires Python 3.10+.

```bash
git clone https://github.com/corporate-keyboard/kilk.git
cd kilk
pip install -e .
```

## Run

```bash
kilk
```

Or:

```bash
python -m kilk.server
```

The server speaks **stdio** by default — point your MCP client at the command.

## Wire it into Claude Desktop / Claude Code

Add to your MCP client config (Claude Desktop: `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "subby-info": {
      "command": "kilk"
    }
  }
}
```

If you prefer not to install globally:

```json
{
  "mcpServers": {
    "subby-info": {
      "command": "python",
      "args": ["-m", "kilk.server"],
      "cwd": "/absolute/path/to/kilk"
    }
  }
}
```

## Editing the docs

All project knowledge lives in [`project_info/`](./project_info/) as plain markdown. Edit the files and restart the MCP server — the next tool call will read the updated content.

| File | Purpose |
| --- | --- |
| `overview.md` | Problem, target users, success metrics |
| `features.md` | Full feature surface + v1 priority |
| `roadmap.md` | Phase-by-phase plan, explicit non-goals |
| `glossary.md` | Domain vocabulary |
| `tech_stack.md` | Working tech choices and open questions |
| `personas.md` | Operator and diner personas |
| `data_model.md` | Sketch of core entities |

## Publishing this repo to GitHub

```bash
# from the repo root
git init
git add .
git commit -m "Initial Kilk"

# create the remote repo (requires the `gh` CLI, authenticated)
gh repo create kilk --public --source=. --remote=origin --push

# or, without gh:
git remote add origin git@github.com:YOUR-USERNAME/kilk.git
git branch -M main
git push -u origin main
```

## License

MIT. See [`LICENSE`](./LICENSE).
