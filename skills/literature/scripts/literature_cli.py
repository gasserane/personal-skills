"""Thin command-line driver over ``ane_package.literature`` (OpenAlex).

All logic lives in the module; this driver parses arguments and formats
compact result lines. One work per line: year | citations | velocity signal |
retraction flag | title | best link (open access preferred). The last line
reports the remaining OpenAlex daily budget when the API sent it.

Usage:
    python literature_cli.py search "query" [--from-year N] [--type review] [--per-page N]
    python literature_cli.py dup-test "planned question" [--from-year N]
    python literature_cli.py debate-map "topic" [--top-works N] [--ancestors N]
    python literature_cli.py forensic "claim to source"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _bootstrap_ane_package() -> None:
    """Put the work folder on sys.path so ane_package imports from anywhere.

    Generated from ane_package.officeops.bootstrap.BOOTSTRAP_SNIPPET.
    Do not edit here; edit the canonical copy and regenerate.
    """
    try:
        import ane_package  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    candidates = []
    env_root = os.environ.get("WORK_FOLDER_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend(Path(__file__).resolve().parents)
    candidates.append(Path.home() / "OneDrive" / "5 ANE CLAUDE work folder")

    for candidate in candidates:
        if (candidate / "ane_package" / "reporting" / "brand.py").is_file():
            sys.path.insert(0, str(candidate))
            return

    raise ModuleNotFoundError(
        "ane_package not found. Set WORK_FOLDER_ROOT to the work folder, or run "
        "this script from inside it."
    )


_bootstrap_ane_package()


def _speak_utf8() -> None:
    """Print paper titles without dying on the console encoding.

    A Windows console is cp1252 by default; scholarly titles carry curly
    quotes, diacritics and dashes that mangle or crash without this.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


_speak_utf8()

from ane_package.literature import (  # noqa: E402
    OpenAlexClient,
    citation_velocity,
    duplication_test,
    forensic_search,
    map_topic_debate,
    velocity_signal,
)


def _line(work, signal: str | None = None) -> str:
    signal = signal or velocity_signal(work)
    flag = "RETRACTED — do not cite" if work.is_retracted else ""
    parts = [
        str(work.year or "?"),
        f"{work.cited_by_count} cites",
        signal,
        work.title[:90],
        work.best_link or "no link",
    ]
    line = " | ".join(parts)
    return f"!! {line} | {flag}" if flag else f"   {line}"


def _print_works(works, header: str) -> None:
    print(header)
    if not works:
        print("   (none found)")
    for row in citation_velocity(list(works)):
        print(_line(row["work"], row["signal"]))


def _print_budget(client: OpenAlexClient) -> None:
    if client.last_remaining_usd is not None:
        print(f"\nOpenAlex budget remaining today: ${client.last_remaining_usd} USD")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="search works by topic")
    p_search.add_argument("query")
    p_search.add_argument("--from-year", type=int, default=None)
    p_search.add_argument("--type", dest="work_type", default=None)
    p_search.add_argument("--per-page", type=int, default=10)
    p_search.add_argument("--sort", default=None)

    p_dup = sub.add_parser("dup-test", help="duplication test on a planned question")
    p_dup.add_argument("question")
    p_dup.add_argument("--from-year", type=int, default=None)

    p_map = sub.add_parser("debate-map", help="common-ancestor papers on a topic")
    p_map.add_argument("topic")
    p_map.add_argument("--top-works", type=int, default=5)
    p_map.add_argument("--ancestors", type=int, default=5)
    p_map.add_argument("--from-year", type=int, default=None)

    p_for = sub.add_parser("forensic", help="source one specific factual claim")
    p_for.add_argument("claim")

    args = parser.parse_args(argv)
    client = OpenAlexClient()

    if args.command == "search":
        works = client.search_works(
            args.query,
            from_year=args.from_year,
            work_type=args.work_type,
            per_page=args.per_page,
            sort=args.sort,
        )
        _print_works(works, f"Results for: {args.query}")

    elif args.command == "dup-test":
        verdict = duplication_test(client, args.question, from_year=args.from_year)
        print(f"Duplication risk: {verdict.risk.upper()}")
        print(verdict.guidance)
        _print_works(verdict.reviews, "\nPublished reviews (closest first):")
        _print_works(verdict.nearest, "\nNearest neighbours (any type):")
        if verdict.retracted:
            print("\n!! Retracted works in the result set — do not cite:")
            for work in verdict.retracted:
                print(f"   {work.title}")

    elif args.command == "debate-map":
        result = map_topic_debate(
            client,
            args.topic,
            top_n_works=args.top_works,
            top_n_ancestors=args.ancestors,
            from_year=args.from_year,
        )
        _print_works(result.top_works, f"Top works on: {args.topic}")
        print("\nCommon ancestors (cited by N of the top works):")
        if not result.ancestors:
            print("   (no ancestor shared by 2+ top works)")
        for row in result.ancestors:
            work = row["work"]
            print(f"   cited by {row['cited_by_n_of_top']} | {_line(work).strip()}")

    elif args.command == "forensic":
        works = forensic_search(client, args.claim)
        _print_works(works, f"Sources for claim: {args.claim}")

    _print_budget(client)
    return 0


if __name__ == "__main__":
    sys.exit(main())
