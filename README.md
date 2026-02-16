# BB Events

CLI tools for extracting match data and tracking buzzerbeaters.

## Setup (once)

1. Install `uv`: https://docs.astral.sh/uv/
2. Create a local `.env` in repo root:
   - `BB_USERNAME=...`
   - `BB_SECURITY_CODE=...`
3. No extra install needed! Just run commands with with `uv run <command> ...`
   - Full options for any command: `uv run <command> --help`

## Main Tracking Workflow (3 commands)

These are the primary tracking commands for buzzerbeaters:

1. `bb-buzzerbeaters`: check one match for buzzerbeaters (read-only, no DB writes).
2. `bb-team-buzzerbeaters`: scan many matches and write/update `data/buzzerbeaters.db`.
3. `bb-buzzerbeater-descriptions`: read `data/buzzerbeaters.db` and render text/summary output.

### `bb-buzzerbeaters`

Detect buzzerbeaters in one match.

Useful flags:

- `--matchid` (required)
- `--details` (show linked shot/free-throw details)
- `--json`

Example (use your own match ID that has a buzzerbeater):

```bash
uv run bb-buzzerbeaters --matchid <MATCH_ID> --details
```

### `bb-team-buzzerbeaters`

Scan team matches and build/update buzzerbeater records in the local DB.

Option guide:

- `--teamid` (required): team to track.
- Season selection (pick one approach):
  - `--season <S>`: one season only.
  - `--seasons <S1,S2,...>`: explicit list.
  - `--season-from <A> --season-to <B>`: inclusive range.
- `--auto-first-season`: auto-detect the first season for the team name.
  - With no season flags, scans detected-first-season through current season.
  - With `--season-to`, sets the start from detected first season.
- `--from-first-active`: for the first scanned season, start from the team's first active match instead of all completed matches. Useful for teams that debuted mid-season.
- `--db <PATH>`: target SQLite database path (default `data/buzzerbeaters.db`).

Main usage (multi-season tracking with auto-detected start):

```bash
uv run bb-team-buzzerbeaters \
  --teamid 142720 \
  --from-first-active \
  --auto-first-season \
  --season-to 71
```

First output lines:

```text
Starting team buzzerbeater scan for team 142720...
Loading environment and credentials...
Authenticating with BB API...
Auto-detecting first season from team history...
Resolved seasons to scan: ...
Resolving first active match in the first scanned season...
Resolved seasons to scan: 
9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,
69,70,71
Warning: Buzzerbeaters are currently not tracked in seasons 1-14.
Resolving first active match in the first scanned season...
First active match resolved.
```

![Season Progress TUI](docs/images/team-buzzerbeaters-tui.png)


After this command runs, the DB will have a `buzzerbeaters` table with one row per detected buzzerbeater event, linked to matches/players/opponents. Next, use `bb-buzzerbeater-descriptions` to query and render human-readable summaries (see next section).

Alternatively (explicit range):

```bash
uv run bb-team-buzzerbeaters \
  --teamid 142720 \
  --season-from <SEASON_FROM> \
  --season-to <SEASON_TO>
```

### `bb-buzzerbeater-descriptions`

Query the DB and render human-readable buzzerbeater lines and summaries.

Option guide:

- Data source:
  - `--db <PATH>` (default `data/buzzerbeaters.db`)
- Filters:
  - `--teamid`, `--opponent-id`, `--matchid`, `--player-id`
- Output mode:
  - `--verbosity 0`: tabular rows.
  - `--columns "col1,col2,..."`: columns used with `--verbosity 0`.
  - `--verbosity 1` or `--verbosity 2`: descriptive text output.
- Summary controls:
  - `--summary`: append aggregate breakdowns.
  - `--top-players <N>`: top players count in summary.
- Content filters:
  - `--only-outcome-change`: only events that changed game state at the buzzer.
- Link formatting:
  - `--no-url`: remove forum tags/viewer links from text.
  - `--link-domain {com,org}`: choose link domain suffix (default: `com`).
- Special report modes (return immediately with dedicated tables):
  - `--multi-buzzer-games`
  - `--multi-player-games`

Example:

```bash
uv run bb-buzzerbeater-descriptions --teamid 142720 --summary
```

with first lines of output:

```text
uv run bb-buzzerbeater-descriptions --teamid 142720 --summary                                                                                                         
In season 15, Xeftilaikos [team=142720] hit an away buzzerbeater in LEAGUE.RS.TV [match=29629491] third quarter against fueg0 B.C [team=27726]: Antonio Peña Rubia [player=8350168] hit a two pointer elbow from 18.4 ft as time expired, turning the score from 49–82 to 49–84. [link=https://buzzerbeater.com/match/29629491/reportmatch.aspx?realTime=2155]

In season 15, Xeftilaikos [team=142720] hit an away buzzerbeater in LEAGUE.RS [match=29629553] third quarter against lewntes [team=88703]: Nikos Kastanakis [player=11177319] hit a three pointer wing from 25.7 ft as time expired, turning the score from 53–67 to 53–70. [link=https://buzzerbeater.com/match/29629553/reportmatch.aspx?realTime=2155]

In season 15, Xeftilaikos [team=142720] hit an away buzzerbeater in LEAGUE.SEMIFINAL [match=32604939] regulation against Harlems [team=88881]: Asimakis Kontis [player=11177331] hit a three pointer wing from 24.8 ft as time expired, turning the score from 109–103 to 109–106. [link=https://buzzerbeater.com/match/32604939/reportmatch.aspx?realTime=2875]

In season 15, Xeftilaikos [team=142720] hit an away buzzerbeater in FRIENDLY [match=32829570] regulation against tromponiakos bc [team=27645]: Asimakis Kontis [player=11177331] hit a fade away from 4.9 ft as time expired, turning the score from 67–94 to 67–96. [link=https://buzzerbeater.com/match/32829570/reportmatch.aspx?realTime=2875]
```

Example (compact table export):

```bash
uv run bb-buzzerbeater-descriptions \
  --teamid 142720 \
  --verbosity 0 \
  --columns "match_id,player_id,game_clock,period"
```

with first lines of output:

```text
match_id        player_id       game_clock      period
29629491        8350168 2160    Q3
29629553        11177319        2160    Q3
32604939        11177331        2880    Q4
32829570        11177331        2880    Q4
32934473        11868055        2880    Q4
32934481        11977485        720     Q1
32934497        11977485        720     Q1
32934505        11977485        2160    Q3
32934537        11977485        720     Q1
32934577        11177319        2880    Q4
```

## Additional Commands

### `bbinsider`

Parse a single match and print stats/events or export JSON.

Useful flags:

- `--matchid` (required)
- `--print-events`
- `--print-stats`
- `--verify`
- `--out` (default: `output/reports/<matchid>.json`)

```bash
uv run bbinsider --matchid <MATCH_ID> --print-stats --print-events
```

### `bb-team-shot-distance-hist`

Generate 2PT/3PT distance histograms for recent team matches.

Useful flags:

- `--teamid` (required)
- `--season` (optional season override)
- `--count` (number of most recent games)
- `--bin-width`
- `--out`

```bash
uv run bb-team-shot-distance-hist --teamid 142720 --count 20
```

### `bbinsider-shotchart`

Generate a shot chart image for a shot event type code.

Useful flags:

- positional `event_type` (integer code)
- `--out`

```bash
uv run bbinsider-shotchart <SHOT_EVENT_TYPE> --out output/charts/shot_<SHOT_EVENT_TYPE>.png
```

Acknowledgements:

- BBAPI
- BBInsider
