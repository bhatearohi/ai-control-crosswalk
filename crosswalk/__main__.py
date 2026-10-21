"""Command line interface.

    python -m crosswalk validate
    python -m crosswalk build
    python -m crosswalk stats [--sector finance]
    python -m crosswalk gaps
    python -m crosswalk query LLM01 --to ISO42001
"""
from __future__ import annotations

import argparse
import sys

from . import analysis
from .build import build_all
from .model import ROOT, load
from .validate import validate


def _validated():
    cw = load()
    errors = validate(cw)
    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    return cw


def cmd_validate(_args) -> None:
    cw = _validated()
    n_maps = sum(len(v) for c in cw.controls for v in c["maps"].values())
    print(f"OK - {len(cw.controls)} controls, {len(cw.frameworks)} frameworks, {n_maps} mappings.")


def cmd_build(_args) -> None:
    cw = _validated()
    for path in build_all(cw):
        print(f"wrote {path.relative_to(ROOT)}")


def cmd_stats(args) -> None:
    cw = _validated()
    label = f" for sector '{args.sector}' (priority >= {args.min_priority})" if args.sector else ""
    print(f"Coverage{label}:")
    for fw_id, d in analysis.coverage(cw, args.sector, args.min_priority).items():
        bar = "#" * int(d["percent"] / 5)
        print(f"  {cw.frameworks[fw_id]['short']:<15} {d['covered']:>3}/{d['total']:<3} {d['percent']:>5.1f}%  {bar}")


def cmd_gaps(_args) -> None:
    cw = _validated()
    g = analysis.gaps(cw)
    if not g:
        print("No gaps - every framework item maps to at least one control.")
    for fw_id, items in g.items():
        print(f"\n{cw.frameworks[fw_id]['name']}")
        for item in items:
            print(f"  {item['id']:<10} {item['title']}")


def cmd_query(args) -> None:
    cw = _validated()
    try:
        res = analysis.pivot(cw, args.item, args.to)
    except KeyError as exc:
        sys.exit(str(exc))
    src = res["source"]
    print(f"{src['id']} - {src['title']}  ({cw.frameworks[src['framework']]['short']})")
    print(f"Linked via controls: {', '.join(res['via_controls']) or 'none'}\n")
    print(f"Related {cw.frameworks[args.to]['short']} items:")
    for t in res["targets"]:
        print(f"  {t['id']:<10} {t['title']}   [via {', '.join(t['via'])}]")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="crosswalk", description="AI Control Crosswalk tooling")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="check data integrity").set_defaults(fn=cmd_validate)
    sub.add_parser("build", help="build dashboard and exports").set_defaults(fn=cmd_build)
    s = sub.add_parser("stats", help="coverage per framework")
    s.add_argument("--sector", choices=["manufacturing", "finance", "healthcare"])
    s.add_argument("--min-priority", default="high", choices=["high", "medium", "low"])
    s.set_defaults(fn=cmd_stats)
    sub.add_parser("gaps", help="framework items with no mapped control").set_defaults(fn=cmd_gaps)
    q = sub.add_parser("query", help="pivot from one framework item to another framework")
    q.add_argument("item", help="e.g. LLM01, ASI03, Art.14, A.6.2.4, MIT-2.2, OECD-1.3")
    q.add_argument("--to", required=True, choices=["MIT", "OWASP-LLM", "OWASP-ASI", "OECD", "ISO42001", "EUAIA"])
    q.set_defaults(fn=cmd_query)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
