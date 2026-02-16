import argparse
import sqlite3


def _pretty_shot_label(label: str | None) -> str | None:
    if not label:
        return None
    return label.replace("_", " ").lower()


def _match_type_label(match_type: str | None) -> str:
    if not match_type:
        return "unknown competition"
    return match_type.upper()


def _home_away(is_home: int | None) -> str:
    if is_home is None:
        return ""
    return "home" if int(is_home) == 1 else "away"


def _period_label(period: str | None) -> str:
    if not period:
        return "regulation"
    if period.lower() == "reg":
        return "regulation"
    if period.lower().startswith("q"):
        q = period.lower()
        if q == "q1":
            return "first quarter"
        if q == "q2":
            return "second quarter"
        if q == "q3":
            return "third quarter"
        if q == "q4":
            return "regulation"
        return period.upper()
    if period.lower().startswith("ot"):
        return period.upper()
    return period


def _realtime_for_period(period: str | None) -> int:
    if not period or period.lower() == "reg":
        return 2880 - 5
    if period.lower().startswith("q"):
        try:
            q_index = int(period[1:])
        except Exception:
            q_index = 4
        q_index = max(1, min(4, q_index))
        return 720 * q_index - 5
    if period.lower().startswith("ot"):
        try:
            ot_index = int(period[2:])
        except Exception:
            ot_index = 1
        return 2880 + 720 * ot_index - 5
    return 2880 - 5


def _article_for(word: str) -> str:
    return "an" if word[:1].lower() in ("a", "e", "i", "o", "u") else "a"


def _is_dunk(label: str | None) -> bool:
    if not label:
        return False
    return "DUNK" in label.upper()


def _outcome_changed(row: dict) -> bool:
    period = (row.get("period") or "").lower()
    if period in ("q1", "q2", "q3"):
        return False
    before_home = row.get("score_before_home")
    before_away = row.get("score_before_away")
    after_home = row.get("score_after_home")
    after_away = row.get("score_after_away")
    is_home = row.get("is_home")
    if None in (before_home, before_away, after_home, after_away, is_home):
        return False
    # Team perspective: compare before/after to detect swing
    if int(is_home) == 1:
        before = before_home - before_away
        after = after_home - after_away
    else:
        before = before_away - before_home
        after = after_away - after_home
    # Any change in game status at the buzzer (lead, tie, lose)
    return (before > 0 and after <= 0) or (before == 0 and after != 0) or (before < 0 and after >= 0)


def describe_row(row: dict, with_forum: bool = True) -> str:
    team = row.get("team_name", "Unknown Team")
    opp = row.get("opponent_name", "Unknown Opponent")
    period = _period_label(row.get("period"))
    player = row.get("player_name", "Unknown Player")
    comment = row.get("comment", "")
    match_type = _match_type_label(row.get("match_type"))
    ha = _home_away(row.get("is_home"))
    team_id = row.get("team_id")
    opponent_id = row.get("opponent_id")
    player_id = row.get("player_id")
    match_id = row.get("match_id")

    if with_forum:
        if team_id is not None:
            team = f"{team} [team={team_id}]"
        if opponent_id is not None:
            opp = f"{opp} [team={opponent_id}]"
        if player_id is not None:
            player = f"{player} [player={player_id}]"
        if match_id is not None:
            match_type = f"{match_type} [match={match_id}]"

    before_home = row.get("score_before_home")
    before_away = row.get("score_before_away")
    after_home = row.get("score_after_home")
    after_away = row.get("score_after_away")

    score_part = ""
    if before_home is not None and before_away is not None and after_home is not None and after_away is not None:
        score_part = f"turning the score from {before_home}–{before_away} to {after_home}–{after_away}"

    kind = row.get("event_kind")
    if kind == "shot":
        shot_label_raw = row.get("shot_type_label")
        shot_label = _pretty_shot_label(shot_label_raw) or "shot"
        # Normalize dunk variants
        if shot_label_raw and shot_label_raw.upper().startswith("DUNK"):
            shot_label = "dunk"
        dist_ft = row.get("shot_distance_ft")
        if not _is_dunk(shot_label_raw) and dist_ft is not None:
            detail = f"{player} hit a {shot_label} from {dist_ft:.1f} ft"
        else:
            detail = f"{player} hit a {shot_label}"
    elif kind == "free_throw":
        detail = f"{player} made a free throw"
    else:
        detail = f"{player} scored"

    article = _article_for(ha) if ha else "a"
    season = row.get("season")
    season_prefix = f"In season {season}, " if season is not None else ""
    base = f"{season_prefix}{team} hit {article} {ha} buzzerbeater in {match_type} {period} against {opp}: {detail} as time expired"
    if score_part:
        return f"{base}, {score_part}."
    return f"{base}."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/buzzerbeaters.db")
    parser.add_argument("--teamid", type=int, default=None, help="Filter by scoring team id")
    parser.add_argument("--opponent-id", type=int, default=None, help="Filter by opponent team id")
    parser.add_argument("--matchid", type=int, default=None, help="Filter by match id")
    parser.add_argument("--player-id", type=int, default=None, help="Filter by player id")
    parser.add_argument("--only-outcome-change", action="store_true", help="Only buzzerbeaters that flipped to a win")
    parser.add_argument("--no-url", action="store_true", help="Disable BB forum tags and viewer link")
    parser.add_argument(
        "--link-domain",
        choices=("com", "org"),
        default="com",
        help="Domain suffix for viewer links (default: com)",
    )
    parser.add_argument("--summary", action="store_true", help="Print a summary at the end")
    parser.add_argument(
        "--top-players",
        type=int,
        default=5,
        help="Number of top players to show in the summary",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=2,
        help="0=match/player/time only, 1=compact, 2=full description",
    )
    parser.add_argument(
        "--columns",
        type=str,
        default="match_id,player_id,game_clock",
        help="Comma-separated columns for verbosity 0 output",
    )
    parser.add_argument(
        "--multi-buzzer-games",
        action="store_true",
        help="Show players with multiple buzzerbeaters in the same game (respects filters)",
    )
    parser.add_argument(
        "--multi-player-games",
        action="store_true",
        help="Show games where multiple players scored buzzerbeaters for the same team (respects filters)",
    )
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = "SELECT * FROM buzzerbeaters"
    filters = []
    params = []
    if args.teamid is not None:
        filters.append("team_id = ?")
        params.append(args.teamid)
    if args.opponent_id is not None:
        filters.append("opponent_id = ?")
        params.append(args.opponent_id)
    if args.matchid is not None:
        filters.append("match_id = ?")
        params.append(args.matchid)
    if args.player_id is not None:
        filters.append("player_id = ?")
        params.append(args.player_id)
    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY match_id"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    printed = 0
    summary_periods: dict[str, int] = {}
    summary_match_types: dict[str, int] = {}
    summary_players: dict[str, int] = {}
    summary_shot_types: dict[str, int] = {}
    summary_distances: list[tuple[float, int | None]] = []

    columns = [c.strip() for c in args.columns.split(",") if c.strip()]
    if not columns:
        columns = ["match_id", "player_id", "game_clock"]

    filtered_rows = []
    for row in rows:
        row_dict = dict(row)
        if args.only_outcome_change and not _outcome_changed(row_dict):
            continue
        filtered_rows.append(row_dict)

    if args.multi_buzzer_games:
        counts = {}
        times = {}
        for row_dict in filtered_rows:
            key = (
                row_dict.get("match_id"),
                row_dict.get("player_id"),
                row_dict.get("player_name"),
            )
            counts[key] = counts.get(key, 0) + 1
            times.setdefault(key, []).append(row_dict.get("game_clock"))
        hits = [(k, v) for k, v in counts.items() if v > 1]
        hits.sort(key=lambda x: (-x[1], x[0][0] or 0, x[0][1] or 0))
        print("match_id\tplayer_id\tplayer_name\tcount\ttimes")
        for (match_id, player_id, player_name), count in hits:
            tlist = sorted(t for t in times.get((match_id, player_id, player_name), []) if t is not None)
            times_str = ",".join(str(t) for t in tlist)
            print(f"{match_id}\t{player_id}\t{player_name}\t{count}\t{times_str}")
        return

    if args.multi_player_games:
        players = {}
        times = {}
        for row_dict in filtered_rows:
            key = (row_dict.get("match_id"), row_dict.get("team_id"))
            name = row_dict.get("player_name")
            if not name:
                continue
            players.setdefault(key, set()).add(name)
            times.setdefault(key, []).append(row_dict.get("game_clock"))
        hits = [
            (match_id, team_id, sorted(list(names)))
            for (match_id, team_id), names in players.items()
            if len(names) > 1
        ]
        hits.sort(key=lambda x: (-len(x[2]), x[0] or 0, x[1] or 0))
        print("match_id\tteam_id\tplayer_count\tplayers\ttimes")
        for match_id, team_id, names in hits:
            tlist = sorted(
                t for t in times.get((match_id, team_id), []) if t is not None
            )
            times_str = ",".join(str(t) for t in tlist)
            print(
                f"{match_id}\t{team_id}\t{len(names)}\t{', '.join(names)}\t{times_str}"
            )
        return

    if args.verbosity <= 0:
        print("\t".join(columns))
    for row_dict in filtered_rows:
        if args.verbosity <= 0:
            values = []
            for col in columns:
                values.append(str(row_dict.get(col, "")))
            print("\t".join(values))
        else:
            desc = describe_row(row_dict, with_forum=not args.no_url)
            if not args.no_url:
                period = row_dict.get("period")
                rt = _realtime_for_period(period)
                match_id = row_dict.get("match_id")
                if match_id is not None:
                    viewer = f"https://buzzerbeater.{args.link_domain}/match/{match_id}/reportmatch.aspx?realTime={rt}"
                    desc += f" [link={viewer}]"
            print(desc)
            print()
        printed += 1

        if args.summary:
            period_label = _period_label(row_dict.get("period"))
            summary_periods[period_label] = summary_periods.get(period_label, 0) + 1
            match_label = _match_type_label(row_dict.get("match_type"))
            summary_match_types[match_label] = summary_match_types.get(match_label, 0) + 1
            player_name = row_dict.get("player_name") or "Unknown Player"
            summary_players[player_name] = summary_players.get(player_name, 0) + 1
            shot_label = row_dict.get("shot_type_label")
            if shot_label:
                summary_shot_types[shot_label] = summary_shot_types.get(shot_label, 0) + 1
            dist = row_dict.get("shot_distance_ft")
            if dist is not None:
                summary_distances.append((float(dist), row_dict.get("match_id")))

    if args.summary:
        print("Summary")
        print(f"total: {printed}")
        if summary_periods:
            print("by_period:")
            order = [
                "first quarter",
                "second quarter",
                "third quarter",
                "regulation",
            ]
            ordered = [k for k in order if k in summary_periods]
            ot_keys = sorted(
                [k for k in summary_periods.keys() if k.upper().startswith("OT")],
                key=lambda x: int(x[2:]) if x[2:].isdigit() else 999,
            )
            other = [
                k
                for k in summary_periods.keys()
                if k not in ordered and k not in ot_keys
            ]
            for key in ordered + ot_keys + sorted(other):
                print(f"- {key}: {summary_periods[key]}")
        if summary_match_types:
            print("by_match_type:")
            for key in sorted(summary_match_types.keys()):
                print(f"- {key}: {summary_match_types[key]}")
        if summary_players and args.top_players > 0:
            print("top_players:")
            top = sorted(summary_players.items(), key=lambda x: (-x[1], x[0]))[
                : args.top_players
            ]
            for name, count in top:
                print(f"- {name}: {count}")
        if summary_shot_types:
            print("by_shot_type:")
            for key in sorted(summary_shot_types.keys()):
                print(f"- {key}: {summary_shot_types[key]}")
        if summary_distances:
            # Histogram bins in feet
            bins = [0, 5, 10, 15, 20, 25, 30, 35, 45, 100]
            counts = [0 for _ in range(len(bins) - 1)]
            for d, _ in summary_distances:
                for i in range(len(bins) - 1):
                    if bins[i] <= d < bins[i + 1]:
                        counts[i] += 1
                        break
            print("distance_hist_ft:")
            for i, c in enumerate(counts):
                print(f"- {bins[i]}–{bins[i+1]}: {c}")
            longest = max(summary_distances, key=lambda x: x[0])
            print(f"longest: {longest[0]:.1f} ft (match_id={longest[1]})")


if __name__ == "__main__":
    main()
