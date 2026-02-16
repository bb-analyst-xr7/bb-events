import argparse
import contextlib
import io
import re
from pathlib import Path

from comments import Comments
from event import convert, FreeThrowEvent, ShotEvent
from main import parse_xml
from buzzerbeaters import (
    _build_period_ends,
    _period_ends_from_events,
    _period_label_from_end,
    _matching_period_end,
)


def _match_id_from_path(path: Path) -> int | None:
    m = re.search(r"report_(\d+)\.xml$", path.name)
    return int(m.group(1)) if m else None


def _score_events_in_window(baseevents, window_start: int, window_end: int):
    scores = []
    for be in baseevents:
        if be.gameclock < window_start or be.gameclock > window_end:
            continue
        if isinstance(be, ShotEvent) and be.has_scored():
            scores.append(("shot", be.gameclock, be.att_team, str(be.shot_type)))
        elif isinstance(be, FreeThrowEvent) and be.has_scored():
            scores.append(("ft", be.gameclock, be.att_team, str(be.free_throw_type)))
    return scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matches-dir", default="matches")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--include-non-ot", action="store_true")
    parser.add_argument("--only-buzzer-comments", action="store_true")
    args = parser.parse_args()

    matches_dir = Path(args.matches_dir)
    files = sorted(matches_dir.glob("report_*.xml"))
    if args.limit:
        files = files[: args.limit]

    for path in files:
        text = path.read_text(errors="ignore")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                events, ht, at = parse_xml(text)
        except Exception:
            continue

        max_clock = max((ev.gameclock.clock for ev in events), default=0)
        if not args.include_non_ot and max_clock <= 2880:
            continue

        comments = Comments()
        for ev in events:
            with contextlib.redirect_stdout(io.StringIO()):
                ev.comment = comments.get_comment(ev, [ht, at])

        baseevents = convert(events)
        period_ends = _period_ends_from_events(events)
        if not period_ends:
            period_ends = _build_period_ends(max_clock)

        match_id = _match_id_from_path(path)
        print(f"match_id={match_id} max_clock={max_clock} period_ends={period_ends}")

        # Comments near period end
        near_end_comments = []
        buzzer_comments = []
        for ev in events:
            end = _matching_period_end(ev.gameclock.clock, period_ends)
            if end is None:
                continue
            comment = (ev.comment or "").strip()
            if not comment:
                continue
            label = _period_label_from_end(end, period_ends)
            line = (ev.gameclock.clock, label, comment)
            near_end_comments.append(line)
            if "buzzer" in comment.lower():
                buzzer_comments.append(line)

        if args.only_buzzer_comments:
            for clock, label, comment in buzzer_comments:
                print(f"  buzzer_comment t={clock} {label}: {comment}")
        else:
            for clock, label, comment in near_end_comments:
                print(f"  comment t={clock} {label}: {comment}")
            for clock, label, comment in buzzer_comments:
                print(f"  buzzer_comment t={clock} {label}: {comment}")

        # Scoring events near period ends
        for end in period_ends:
            window_start = end - 5
            scores = _score_events_in_window(baseevents, window_start, end)
            if not scores:
                continue
            label = _period_label_from_end(end, period_ends)
            print(f"  scores near end {label} ({window_start}-{end}):")
            for kind, clock, team, shot_type in scores:
                tname = ht.name if team == 0 else at.name
                print(f"    {kind} t={clock} team={tname} type={shot_type}")

        print()


if __name__ == "__main__":
    main()
