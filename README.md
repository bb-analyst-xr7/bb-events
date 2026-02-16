# BB Insider

CLI tools for extracting match data and tracking buzzerbeaters.

## Setup (once)

1. Install `uv`: https://docs.astral.sh/uv/
2. Create a local `.env` in repo root:
   - `BB_USERNAME=...`
   - `BB_SECURITY_CODE=...`
3. Run commands from repo root with `uv run <command> ...`
   - Full options for any command: `uv run <command> --help`

## Core Tracking Commands

### `bbinsider`
Parse a single match and print stats/events or export JSON.

Useful flags:
- `--matchid` (required)
- `--print-events`
- `--print-stats`
- `--verify`
- `--out` (default: `output/reports/<matchid>.json`)

Example:

```bash
uv run bbinsider --matchid 123786926 --print-stats --print-events
```

### `bbinsider-buzzerbeaters`
Detect buzzerbeaters in one match.

Useful flags:
- `--matchid` (required)
- `--details` (show linked shot/free-throw details)
- `--json`

Known buzzerbeater example:

```bash
uv run bbinsider-buzzerbeaters --matchid <MATCH_ID_WITH_BUZZERBEATER> --details
```

### `bbinsider-team-buzzerbeaters`
Scan team matches and build/update buzzerbeater records in the local DB.

Useful flags:
- `--teamid` (required)
- season scope: `--season`, `--seasons`, or `--season-from` + `--season-to`
- `--auto-first-season`
- `--from-first-active`
- `--db` (default: `data/buzzerbeaters.db`)
- `--tui`

Example (multi-season tracking):

```bash
uv run bbinsider-team-buzzerbeaters \
  --teamid <TEAM_ID> \
  --from-first-active \
  --auto-first-season \
  --season-to <SEASON>
```

### `bbinsider-buzzerbeater-descriptions`
Query the DB and render human-readable buzzerbeater lines and summaries.

Useful flags:
- filters: `--teamid`, `--opponent-id`, `--matchid`, `--player-id`
- `--summary`
- `--only-outcome-change`
- `--verbosity` (`0`, `1`, `2`)
- `--no-url`
- `--multi-buzzer-games`, `--multi-player-games`

Example:

```bash
uv run bbinsider-buzzerbeater-descriptions --teamid <TEAM_ID> --summary
```

## Additional Commands

### `bbinsider-team-info`
Fetch team metadata and first-season estimate.

```bash
uv run bbinsider-team-info --teamid <TEAM_ID>
```

### `bbinsider-team-shot-distance-hist`
Generate 2PT/3PT distance histograms for recent team matches.

Useful flags:
- `--teamid` (required)
- `--season` (optional season override)
- `--count` (number of most recent games)
- `--bin-width`
- `--out`

```bash
uv run bbinsider-team-shot-distance-hist --teamid <TEAM_ID> --count 20
```

### `bbinsider-shotchart`
Generate a shot chart image for a shot event type code.

Useful flags:
- positional `event_type` (integer code)
- `--out`

```bash
uv run bbinsider-shotchart 201 --out output/charts/shot_201.png
```

## Outputs

- Match XML cache: `matches/report_<matchid>.xml`
- Buzzerbeater DB: `data/buzzerbeaters.db`
- JSON reports: `output/reports/`
- Charts and other generated files: `output/`

## Privacy

- Keep `.env` local.
- Do not commit private exports/scrapes.
