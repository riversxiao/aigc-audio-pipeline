#!/usr/bin/env python3
"""Standalone CLI runner for Global Edge (projects/global_edge/) 4-Tier Opaque-Box E2E Suite.

Usage:
  PYTHONPATH=src python3 tests/e2e_global_edge/run_e2e.py --list
  PYTHONPATH=src python3 tests/e2e_global_edge/run_e2e.py --self-test
  PYTHONPATH=src python3 tests/e2e_global_edge/run_e2e.py --tier 1|2|3|4|all [--json-out <path>] [--verbose]

Zero third-party dependencies (Python 3.11+ stdlib only).
NEVER create tests/e2e_global_edge/__init__.py.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
SRC_ROOT = REPO_ROOT / "src"

for _p in (str(THIS_DIR), str(SRC_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import e2e_helpers as h  # noqa: E402
import e2e_tier1_features as tier1  # noqa: E402
import e2e_tier2_boundaries as tier2  # noqa: E402
import e2e_tier3_pairwise as tier3  # noqa: E402
import e2e_tier4_workloads as tier4  # noqa: E402

TIER_MODULES = {
    1: ("Tier 1 — Feature Coverage (Happy Path)", tier1.TESTS),
    2: ("Tier 2 — Boundary, Corner & Negative Cases", tier2.TESTS),
    3: ("Tier 3 — Cross-Feature Pairwise Combinations", tier3.TESTS),
    4: ("Tier 4 — Real-World E2E Application Scenarios", tier4.TESTS),
}

ALL_19_FEATURES = [f"F{i:02d}" for i in range(1, 20)]


def _collect_all() -> dict[int, list[h.TestCaseSpec]]:
    seen_global: set[str] = set()
    by_tier: dict[int, list[h.TestCaseSpec]] = {}
    for tier_num, (_label, tests) in TIER_MODULES.items():
        for spec in tests:
            if spec.test_id in seen_global:
                raise RuntimeError(f"Duplicate test_id across tiers: {spec.test_id}")
            seen_global.add(spec.test_id)
        by_tier[tier_num] = list(tests)
    return by_tier


def _write_json_out(json_out: str | None, payload: dict[str, Any]) -> None:
    if not json_out:
        return
    out_path = Path(json_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _cmd_list(by_tier: dict[int, list[h.TestCaseSpec]], json_out: str | None) -> int:
    t1_c = Counter(t.feature_id for t in by_tier[1])
    t2_c = Counter(t.feature_id for t in by_tier[2])

    print("=" * 78)
    print("Global Edge (projects/global_edge/) — 4-Tier Opaque-Box E2E Test Catalog")
    print("=" * 78)
    for tier_num in (1, 2, 3, 4):
        label, _ = TIER_MODULES[tier_num]
        specs = by_tier[tier_num]
        print(f"\n[{label}] ({len(specs)} tests)")
        for spec in specs:
            print(f"  {spec.test_id:10s} [{spec.feature_id:7s}] {spec.title}")

    print("\n" + "-" * 78)
    print("Feature Coverage Table (F01–F19)")
    print(f"{'Feature':<10s} {'Tier 1':>8s} {'Tier 2':>8s} {'Status':>10s}")
    feature_ok = True
    for fid in ALL_19_FEATURES:
        c1 = t1_c.get(fid, 0)
        c2 = t2_c.get(fid, 0)
        ok = c1 >= 5 and c2 >= 5
        if not ok:
            feature_ok = False
        print(f"{fid:<10s} {c1:>8d} {c2:>8d} {'OK' if ok else 'LOW':>10s}")

    n1, n2, n3, n4 = len(by_tier[1]), len(by_tier[2]), len(by_tier[3]), len(by_tier[4])
    total = n1 + n2 + n3 + n4
    thresholds_ok = (
        n1 >= 95
        and n2 >= 95
        and n3 >= 19
        and n4 >= 10
        and total >= 218
        and feature_ok
    )

    print("-" * 78)
    print(
        f"Summary: Tier1={n1} (>=95), Tier2={n2} (>=95), Tier3={n3} (>=19), "
        f"Tier4={n4} (>=10), TOTAL={total} (>=218) | Thresholds={'PASS' if thresholds_ok else 'FAIL'}"
    )
    print("=" * 78)

    if json_out:
        payload = {
            "counts": {"tier1": n1, "tier2": n2, "tier3": n3, "tier4": n4, "total": total},
            "feature_coverage": {fid: {"tier1": t1_c.get(fid, 0), "tier2": t2_c.get(fid, 0)} for fid in ALL_19_FEATURES},
            "thresholds_passed": thresholds_ok,
            "tests": [
                {"test_id": s.test_id, "tier": s.tier, "feature": s.feature_id, "title": s.title}
                for tn in (1, 2, 3, 4)
                for s in by_tier[tn]
            ],
        }
        _write_json_out(json_out, payload)

    return 0 if thresholds_ok else 1


def _cmd_self_test(json_out: str | None, verbose: bool) -> int:
    t0 = time.monotonic()
    results = h.run_self_test_suite()
    elapsed = time.monotonic() - t0

    print("=" * 78)
    print("Global Edge E2E — 18-Family Positive/Negative Mutation Self-Test")
    print("=" * 78)
    passed_fams = 0
    total_pos = 0
    total_mut = 0
    for r in results:
        if r["status"] == "PASS":
            passed_fams += 1
        total_pos += int(r["positives_passed"])
        total_mut += int(r["mutants_caught"])
        line = (
            f"  Family {r['family']:02d} [{r['status']:4s}] "
            f"positives={r['positives_passed']:2d} mutants_caught={r['mutants_caught']:2d} | {r['name']}"
        )
        print(line)
        if r["message"] and (verbose or r["status"] != "PASS"):
            print(f"      -> {r['message']}")

    all_ok = len(results) == 18 and passed_fams == 18
    print("-" * 78)
    print(
        f"Self-Test Summary: {passed_fams}/{len(results)} families PASSED | "
        f"positives_passed={total_pos} | mutants_caught={total_mut} | "
        f"elapsed={elapsed:.2f}s | verdict={'PASS' if all_ok else 'FAIL'}"
    )
    print("=" * 78)

    if json_out:
        payload = {
            "mode": "self-test",
            "families_passed": passed_fams,
            "families_total": len(results),
            "positives_passed": total_pos,
            "mutants_caught": total_mut,
            "elapsed_s": round(elapsed, 3),
            "passed": all_ok,
            "results": results,
        }
        _write_json_out(json_out, payload)

    return 0 if all_ok else 1


def _cmd_run_tiers(
    by_tier: dict[int, list[h.TestCaseSpec]],
    tier_arg: str,
    json_out: str | None,
    verbose: bool,
) -> int:
    if tier_arg == "all":
        selected_tiers = [1, 2, 3, 4]
    else:
        selected_tiers = [int(tier_arg)]

    suite_start = time.monotonic()
    all_records: list[dict[str, Any]] = []
    tier_summaries: dict[int, dict[str, int]] = {}

    print("=" * 78)
    print(f"Global Edge (projects/global_edge/) — Running E2E Tier(s): {selected_tiers}")
    print("=" * 78)

    for tn in selected_tiers:
        label, _ = TIER_MODULES[tn]
        specs = by_tier[tn]
        t_pass = 0
        t_fail = 0
        t_err = 0
        print(f"\n>>> {label} ({len(specs)} tests)")
        for spec in specs:
            t0 = time.monotonic()
            status = "PASS"
            msg = ""
            try:
                spec.fn()
                t_pass += 1
            except AssertionError as exc:
                status = "FAIL"
                t_fail += 1
                msg = str(exc) or "AssertionError"
            except Exception as exc:  # noqa: BLE001
                status = "ERROR"
                t_err += 1
                msg = f"{type(exc).__name__}: {exc}"
                if verbose:
                    msg += "\n" + traceback.format_exc()
            dur = time.monotonic() - t0
            all_records.append(
                {
                    "tier": spec.tier,
                    "feature": spec.feature_id,
                    "test_id": spec.test_id,
                    "title": spec.title,
                    "status": status,
                    "duration_s": round(dur, 4),
                    "message": msg,
                }
            )
            if verbose or status != "PASS":
                short_msg = msg.splitlines()[0] if msg else ""
                print(f"  [{status:5s}] {spec.test_id:10s} ({dur:5.2f}s) {short_msg[:120]}")
        tier_summaries[tn] = {
            "passed": t_pass,
            "failed": t_fail,
            "errors": t_err,
            "total": len(specs),
        }
        print(
            f"<<< Tier {tn} Summary: passed={t_pass} failed={t_fail} errors={t_err} total={len(specs)}"
        )

    total_elapsed = time.monotonic() - suite_start
    tot_pass = sum(s["passed"] for s in tier_summaries.values())
    tot_fail = sum(s["failed"] for s in tier_summaries.values())
    tot_err = sum(s["errors"] for s in tier_summaries.values())
    tot_all = sum(s["total"] for s in tier_summaries.values())
    ok = tot_fail == 0 and tot_err == 0 and tot_pass == tot_all and tot_all > 0

    print("\n" + "=" * 78)
    print(
        f"OVERALL E2E SUMMARY: passed={tot_pass} failed={tot_fail} errors={tot_err} "
        f"total={tot_all} elapsed={total_elapsed:.2f}s | verdict={'PASS' if ok else 'FAIL'}"
    )
    print("=" * 78)

    if json_out:
        payload = {
            "tiers_executed": selected_tiers,
            "summary": {
                "passed": tot_pass,
                "failed": tot_fail,
                "errors": tot_err,
                "total": tot_all,
                "elapsed_s": round(total_elapsed, 3),
                "verdict": "PASS" if ok else "FAIL",
            },
            "per_tier": {str(k): v for k, v in tier_summaries.items()},
            "results": all_records,
        }
        _write_json_out(json_out, payload)

    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Independent 4-Tier Opaque-Box E2E Test Suite for Global Edge (projects/global_edge/)."
    )
    p.add_argument(
        "--tier",
        choices=("1", "2", "3", "4", "all"),
        default="all",
        help="Tier(s) to execute (default: all).",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List all registered E2E test cases and verify F01-F19 coverage thresholds.",
    )
    p.add_argument(
        "--self-test",
        action="store_true",
        help="Run the 18-family positive/negative synthetic mutation test suite.",
    )
    p.add_argument(
        "--json-out",
        default="",
        help="Optional path to write structured JSON report.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print every PASS/FAIL test line and full tracebacks on unexpected errors.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    json_out = args.json_out.strip() or None
    if args.self_test:
        return _cmd_self_test(json_out=json_out, verbose=args.verbose)
    by_tier = _collect_all()
    if args.list:
        return _cmd_list(by_tier=by_tier, json_out=json_out)
    return _cmd_run_tiers(
        by_tier=by_tier,
        tier_arg=args.tier,
        json_out=json_out,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    raise SystemExit(main())
