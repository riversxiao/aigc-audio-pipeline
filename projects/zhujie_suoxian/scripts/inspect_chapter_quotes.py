#!/usr/bin/env python3
"""Helper CLI to inspect exact paragraph numbers, spoken dialogue quotes, and context for any chapter range."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.adapter import _QUOTE_SPLIT, is_spoken_dialogue_quote
from aigc_audio_pipeline.compiler import extract_spoken_quotes_in_chapter, parse_chapter_paragraphs

_SSD_DIR = Path("/tmp/zhujie_source_chapters")
SOURCE_DIR = _SSD_DIR if _SSD_DIR.is_dir() else Path("/shared/user/.gemini/config/zhujie_suoxian_audio/source_chapters")


def inspect_chapter(ch_num: int) -> None:
    cands = sorted(SOURCE_DIR.glob(f"第{ch_num:02d}章_*.md")) + sorted(SOURCE_DIR.glob(f"第{ch_num}章_*.md"))
    seen = []
    for c in cands:
        if c not in seen and int(c.name.split("章")[0].lstrip("第")) == ch_num:
            seen.append(c)
    if not seen:
        raise FileNotFoundError(f"Chapter {ch_num} not found in {SOURCE_DIR}")
    md_path = seen[0]
    title, paras = parse_chapter_paragraphs(md_path)
    quotes = extract_spoken_quotes_in_chapter(paras)
    print(f"=== E{ch_num:03d} | {md_path.name} | title={title!r} | paras={len(paras)} | spoken_quotes={len(quotes)} ===")
    for p_idx, p in enumerate(paras, 1):
        if len(p) <= 22 or any(sfx_w in p for sfx_w in ("轰", "咔嚓", "噗嗤", "嗡", "铛")):
            if len(p) <= 26:
                print(f"  [SHORT/ONOMATOPOEIA? P{p_idx}] {p}")
    for q_idx, (p_idx, sub_i, q_txt) in enumerate(quotes):
        prev_p = paras[p_idx - 2][-55:] if p_idx >= 2 else ""
        cur_p = paras[p_idx - 1]
        parts = _QUOTE_SPLIT.split(cur_p)
        print(f"  Q#{q_idx:02d} @ P{p_idx}.{sub_i}: {q_txt[:52]!r}")
        print(f"       prev_P{p_idx-1}: ...{prev_p}")
        print(f"       cur_P{p_idx} : {cur_p[:95]}")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if "-" in arg:
            a, b = arg.split("-", 1)
            for n in range(int(a), int(b) + 1):
                inspect_chapter(n)
        else:
            inspect_chapter(int(arg))
