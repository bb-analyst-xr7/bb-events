# BB Insider

CLI utilities for BuzzerBeater match parsing, buzzerbeater detection, and team-level analysis.

## Requirements

- Python 3.10+
- `uv` (recommended): https://docs.astral.sh/uv/

## Quick Start (uv)

1. Install dependencies:
   - `uv sync`
2. Create a local `.env` file with:
   - `BB_USERNAME=...`
   - `BB_SECURITY_CODE=...`
3. Run commands with:
   - `uv run <command> ...`
4. See command options:
   - `uv run <command> --help`

Example:

```bash
uv run bbinsider --matchid 123786926 --print-stats --print-events
```

## Suggested First-Run Order

1. Parse one match and inspect output:
   - `uv run bbinsider --matchid 123786926 --print-stats --print-events`
2. Detect buzzerbeaters for a known buzzerbeater match:
   - `uv run bbinsider-buzzerbeaters --matchid <MATCH_ID_WITH_BUZZERBEATER> --details`
3. Check team metadata and first season hint:
   - `uv run bbinsider-team-info --teamid <TEAM_ID>`
4. Build team buzzerbeater history across seasons:
   - `uv run bbinsider-team-buzzerbeaters --teamid <TEAM_ID> --from-first-active --auto-first-season --season-to <SEASON>`
5. Generate description text from the DB:
   - `uv run bbinsider-buzzerbeater-descriptions --teamid <TEAM_ID> --summary`
6. Optional visual analysis:
   - `uv run bbinsider-shotchart <MATCH_ID> --out output/charts/shot_<MATCH_ID>.png`
   - `uv run bbinsider-team-shot-distance-hist --teamid <TEAM_ID> --count 20`

## Outputs And Privacy

- Match XML cache: `matches/report_<matchid>.xml`
- Buzzerbeater DB: `data/buzzerbeaters.db`
- Generated charts and private exports: `output/`
- Keep `.env` local and never commit private exports/scrapes.
