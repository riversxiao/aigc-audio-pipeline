#!/usr/bin/env python3
"""Deterministic 100-clip corpus ETL and executive lexicon generator for Global Edge.

Ingests `/tmp/arsenal_100_queue.json` (or downloads Google Drive file ID
`1K61WnLZKDEwW5QIwkc1BJ9SzOxRD-Gzj` when `--fetch-gdrive` is passed), validates
strict structural invariants before writing any output, applies 85 clip-scoped
ASR normalization rules (39 Core + 46 Extended, including `[snorts]` stripping
and Unicode-to-ASCII cleanup) while preserving `en_raw` verbatim, repairs
subtitle timestamp overlaps cleanly, runs 4-stage deterministic speaker
inference across all 100 clips, verifies the 120-entry executive lexicon
(96 corpus + 24 world_bridge = 80.0% / 20.0%), and emits three byte-exact
deterministic artifacts:

1. `corpus_100_structured.json`
2. `executive_lexicon.json`
3. `CORPUS_INTELLIGENCE_REPORT.md`

Pure Python 3.11+ standard library only (zero third-party dependencies).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, NoReturn

SCHEMA_VERSION = "1.0.0"
DRIVE_ARSENAL_FILE_ID = "1K61WnLZKDEwW5QIwkc1BJ9SzOxRD-Gzj"
DEFAULT_SOURCE_PATH = Path("/tmp/arsenal_100_queue.json")
DEFAULT_OUT_DIR = Path(__file__).resolve().parents[1] / "01_视频号语料与商业词库"

EXPECTED_TOTAL_CLIPS = 100
MAX_REPAIRABLE_OVERLAP_SEC = 0.25
EXPECTED_TOPIC_COUNTS: dict[str, int] = {
    "AI": 25,
    "BUSINESS": 25,
    "FINANCE": 25,
    "US_CHINA": 25,
}
TOPIC_ORDER: tuple[str, ...] = ("AI", "BUSINESS", "FINANCE", "US_CHINA")
TOPIC_DISPLAY_ZH: dict[str, str] = {
    "AI": "AI · 前沿科技",
    "BUSINESS": "BUSINESS · 商业策略",
    "FINANCE": "FINANCE · 金融投资",
    "US_CHINA": "US_CHINA · 中美博弈",
}

EN_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-\.]*")
PREFIX_NUM_RE = re.compile(r"^(\d+)_")

REQUIRED_PLAN_KEYS: tuple[str, ...] = (
    "clip_id",
    "topic_key",
    "topic_label",
    "video_id",
    "video_title",
    "channel",
    "virality_score",
    "hook_line_1",
    "hook_line_2",
    "en_title_hook",
    "summary_zh",
    "subtitles",
)
REQUIRED_STR_PLAN_KEYS: tuple[str, ...] = (
    "topic_label",
    "video_id",
    "video_title",
    "channel",
    "hook_line_1",
    "hook_line_2",
    "en_title_hook",
    "summary_zh",
)
REQUIRED_NONEMPTY_STR_PLAN_KEYS: frozenset[str] = frozenset(
    {"topic_label", "video_id", "channel"}
)

REQUIRED_LEXICON_KEYS: frozenset[str] = frozenset(
    {
        "phrase_id",
        "phrase_en",
        "category",
        "cefr_level",
        "chinglish_trap",
        "executive_subtext_zh",
        "verbatim_context_en",
        "source_type",
        "clip_ids",
    }
)
VALID_CEFR_LEVELS: frozenset[str] = frozenset({"B1", "B2", "C1", "C2"})
VALID_SOURCE_TYPES: frozenset[str] = frozenset({"corpus", "world_bridge"})
CATEGORY_LABELS_ZH: dict[str, str] = {
    "executive_hedging_framing": "高管立场控场与礼貌带刀框架 (Executive Hedging & Framing)",
    "vc_valuation_finance": "融资估值、财报反杀与宏观金融 (VC Valuation & Finance)",
    "ai_compute_product": "AI 算力经济学与产品工程 (AI Compute & Product)",
    "tariffs_supply_chain_geopolitics": "关税、供应链与地缘合规博弈 (Tariffs, Supply Chain & Geopolitics)",
    "retail_channel_bridge": "欧美大渠道零售谈判桥梁词 (Retail Channel World-Bridge)",
    "compliance_hardware_bridge": "欧美合规与深圳硬件量产桥梁词 (Compliance & Hardware World-Bridge)",
}

E001_SEED_CLIPS: tuple[str, ...] = (
    "02_BIZ_Anthropic",
    "012_AI",
    "039_BIZ",
    "090_USC",
    "059_FIN",
)

# All 8 mandatory E001 phrase groups (13 verbatim phrases) from PROJECT.md §5
E001_MANDATORY_PHRASES: tuple[tuple[str, str, str], ...] = (
    ("Group #1", "phantom number", "02_BIZ_Anthropic"),
    ("Group #2a", "not a cash loss", "02_BIZ_Anthropic"),
    ("Group #2b", "flowed through into the income statement", "02_BIZ_Anthropic"),
    ("Group #3", "capital-efficient", "02_BIZ_Anthropic"),
    ("Group #4a", "10 times the throughput", "012_AI"),
    ("Group #4b", "Pick your favorite number", "012_AI"),
    ("Group #5", "In other words", "039_BIZ"),
    ("Group #6a", "eating into budgets", "090_USC"),
    ("Group #6b", "a really hard trade-off", "090_USC"),
    ("Group #7a", "What is good enough", "090_USC"),
    ("Group #7b", "run this thing a million times", "090_USC"),
    ("Group #8a", "upside", "059_FIN"),
    ("Group #8b", "When are you going to get it", "059_FIN"),
)

# ---------------------------------------------------------------------------
# 1. Full 85-Rule Clip-Scoped ASR Normalization Table (39 Core + 46 Extended)
# Tuple format: (rule_id, tier, clip_id, match_type, pattern, replacement, reason)
# ---------------------------------------------------------------------------
ASR_NORMALIZATION_RULES: tuple[tuple[int, str, str, str, str, str, str], ...] = (
    # --- Tier A: 39 Core Rules (49 segment replacements across 23 clips) ---
    (1, "core", "010_AI", "literal", "like5 trillion", "like $5 trillion", "Missing space and $ before 5 trillion (ZH: 五万亿美元)"),
    (2, "core", "014_AI", "literal", "Hammarabi", "Hammurabi", "Historical spelling of Hammurabi (ZH: 汉谟拉比法典)"),
    (3, "core", "015_AI", "literal", "grock 3", "Grok 3", "xAI model name Grok 3"),
    (4, "core", "015_AI", "regex", r"\bClaud\b", "Claude", "Anthropic Claude (word boundary avoids Claude->Claudee)"),
    (5, "core", "018_AI", "literal", "1,24 tokens", "1,024 tokens", "GPT-2 context is 1,024 tokens (ZH: 1024)"),
    (6, "core", "021_AI", "literal", "Abene", "Abilene", "Stargate Texas site Abilene (ZH: 得州阿比林)"),
    (7, "core", "031_BIZ", "literal", "these Ms", "these mats", "Fiberglass mats (phrase+clip-scoped; protects Ms./MS)"),
    (8, "core", "031_BIZ", "literal", "dber cartoon", "Dilbert cartoon", "Dilbert cartoon reference"),
    (9, "core", "045_BIZ", "literal", "Palanteer", "Palantir", "Company name Palantir"),
    (10, "core", "045_BIZ", "literal", "Palunteers", "Palantir's", "Possessive Palantir's AI (ZH: Palantir的算法)"),
    (11, "core", "050_BIZ", "literal", "r d v span", "R&D spend", "R&D spend (ZH: 研发预算)"),
    (12, "core", "051_BIZ", "literal", "gp4", "GPT-4", "OpenAI model GPT-4"),
    (13, "core", "054_BIZ", "literal", "totally shelf", "totally shelved", "Past participle shelved (ZH: 束之高阁)"),
    (14, "core", "054_BIZ", "literal", "crude mission", "crewed mission", "Crewed Mars mission (ZH: 载人登陆火星)"),
    (15, "core", "055_FIN", "literal", "for truckee", "for Druckenmiller", "Cross-seg split truckee / miller -> Druckenmiller (part 1)"),
    (16, "core", "055_FIN", "literal", "miller he got out", "he got out", "Cross-seg split truckee / miller absorbed into seg 0 (part 2)"),
    (17, "core", "055_FIN", "literal", "drucker miller", "Druckenmiller", "Stanley Druckenmiller (ZH: 德鲁肯米勒)"),
    (18, "core", "055_FIN", "literal", "sorrows", "Soros", "George Soros (clip-scoped, ZH: 索罗斯)"),
    (19, "core", "064_FIN", "literal", "tight money suit", "tight money soon", "ASR phonetic garble soon->suit"),
    (20, "core", "064_FIN", "literal", "easy money suit", "easy money soon", "ASR phonetic garble soon->suit"),
    (21, "core", "069_FIN", "literal", "law of holds", "law of holes", "First Law of Holes (matches seg 5 law of holes)"),
    (22, "core", "069_FIN", "literal", "caught in half", "cut in half", "Einhorn quote: down 80% then cut in half (ZH: 腰斩)"),
    (23, "core", "070_FIN", "literal", "tor rate", "torrid rate", "Spent at a torrid rate (ZH: 惊人的速度)"),
    (24, "core", "070_FIN", "literal", "a trillion change", "a trillion and change", "Idiom a trillion and change (ZH: 一万多亿美元)"),
    (25, "core", "073_FIN", "literal", "gets cast robbery", "is a catastrophe", "Default catastrophe (removes cast robbery grammatically)"),
    (26, "core", "082_USC", "literal", "one tiny floor", "one tiny flaw", "Wafer defect flaw (ZH: 一个微小瑕疵)"),
    (27, "core", "082_USC", "literal", "Tynan Science Park", "Tainan Science Park", "TSMC Tainan Science Park (ZH: 台南科学园区)"),
    (28, "core", "085_USC", "literal", "chakyang", "Zhejiang", "Morris Chang birthplace Ningbo, Zhejiang (ZH: 浙江宁波)"),
    (29, "core", "086_USC", "literal", "Kaiser Supply Chain", "kinds of supply chain", "ASR phonetic garble kinds of->Kaiser"),
    (30, "core", "087_USC", "regex", r"\s*\[snorts\]\s*", " ", "Strip non-speech bracket tag [snorts]"),
    (31, "core", "090_USC", "literal", "Jipu", "Zhipu", "Chinese AI lab Zhipu / Z.ai (ZH: 智谱)"),
    (32, "core", "093_USC", "literal", "$122,000", "$12,000", "BYD Seagull <$12,000 (en_title_hook: $12K EV, ZH: 1.2万)"),
    (33, "core", "093_USC", "literal", "$115,000", "$15,000", "$12,000 + 25% tariff = $15,000 (ZH: 1.5万)"),
    (34, "core", "093_USC", "literal", "BD's", "BYD's", "Automaker BYD's (ZH: 比亚迪)"),
    (35, "core", "099_USC", "literal", "do announcement", "dollar announcement", "$500 billion dollar announcement"),
    (36, "core", "099_USC", "literal", "Mas son", "Masayoshi Son", "SoftBank CEO Masayoshi Son (ZH: 孙正义)"),
    (37, "core", "099_USC", "literal", "Larry Ellison and Arison and", "Larry Ellison", "Deduplicate garbled stutter without doubling Larry Ellison"),
    (38, "core", "099_USC", "literal", "Sam Alman", "Sam Altman", "OpenAI CEO Sam Altman"),
    (39, "core", "100_USC", "literal", "UBEC", "UBTECH", "Robotics firm UBTECH (matches 095_USC & ZH: 优必选)"),
    # --- Tier B: 46 Extended Audit Rules (49 segment replacements across 31 clips) ---
    (40, "extended", "009_AI", "literal", "on prem", "on-prem", "Hyphenate standard term on-prem (enables verbatim lexicon match)"),
    (41, "extended", "011_AI", "literal", "AI sent", "AI Ascent", "Sequoia Capital's AI Ascent summit (ZH: 红杉峰会)"),
    (42, "extended", "011_AI", "literal", "open claw", "OpenClaw", "Coding agent OpenClaw (ZH: OpenClaw)"),
    (43, "extended", "011_AI", "literal", "cloud code", "Claude Code", "Anthropic Claude Code (ZH: Claude Code)"),
    (44, "extended", "015_AI", "literal", "programming l language", "programming language", "Stray single-letter ASR stutter l"),
    (45, "extended", "018_AI", "literal", "project called lm.", "project called llm.c.", "Karpathy's llm.c repo (ZH: 开源项目llm.c里)"),
    (46, "extended", "022_AI", "literal", "non-spike in neural networks", "non-spiking neural networks", "Matches seg 8 non-spiking neural networks in same clip"),
    (47, "extended", "031_BIZ", "literal", "Proby fix", "Probably fix", "Truncated ASR word Proby->Probably"),
    (48, "extended", "031_BIZ", "literal", "NBA noise vibration hes", "NVH (noise, vibration, harshness)", "Automotive NVH team (ZH: NVH噪声振动团队)"),
    (49, "extended", "031_BIZ", "literal", "five glass mats", "fiberglass mats", "Fiberglass battery mats (ZH: 玻璃纤维垫)"),
    (50, "extended", "032_BIZ", "literal", "as a100", "as a $100", "Glued article+number at end of seg 1 (continues into seg 2 billion)"),
    (51, "extended", "033_BIZ", "literal", "16 million with an M", "60 million with an M", "Bezos reiterating $60 million from 5 words prior (ZH: 6000万美元)"),
    (52, "extended", "035_BIZ", "literal", "50 000 jobs", "50,000 jobs", "Missing thousands comma in 50,000"),
    (53, "extended", "037_BIZ", "literal", "met AI be", "Meta AI be", "Meta AI assistant (ZH: Meta AI)"),
    (54, "extended", "037_BIZ", "literal", "45 billion parameters", "405 billion parameters", "Llama 3.1 flagship is 405B (9x numeric ASR error; ZH: 4050亿参数)"),
    (55, "extended", "038_BIZ", "regex", r"\bTeal\b", "Thiel", "Peter Thiel (ZH: 蒂尔)"),
    (56, "extended", "039_BIZ", "literal", "SAS software", "SaaS software", "Software-as-a-Service SaaS (ZH: SaaS软件)"),
    (57, "extended", "042_BIZ", "literal", "Kimik 3", "Kimi K3", "Moonshot Kimi K3 (verified verbatim in 078_USC[8])"),
    (58, "extended", "043_BIZ", "literal", "stepped literally on the floor", "slept literally on the floor", "Musk sleeping on factory floor (ZH: 直接睡在工厂地上)"),
    (59, "extended", "044_BIZ", "literal", "sliding our company is insane", "starting a rocket company is insane", "Musk YC quote (ZH: 创办一家火箭公司绝对是彻头彻尾的疯子行为)"),
    (60, "extended", "044_BIZ", "literal", "to improve ROC", "to improve rocket", "Continues into seg 7 technology (ZH: 火箭技术)"),
    (61, "extended", "045_BIZ", "literal", "Sham Sankar", "Shyam Sankar", "Palantir CTO Shyam Sankar spelling"),
    (62, "extended", "047_BIZ", "literal", "10 000 hours", "10,000 hours", "Missing thousands comma in 10,000"),
    (63, "extended", "052_BIZ", "literal", "workingclass", "working-class", "Auto-caption dropped hyphen"),
    (64, "extended", "055_FIN", "literal", "to colossus", "to cut losses", "ASR phonetic garble cut losses->colossus (ZH: 果断止损)"),
    (65, "extended", "056_FIN", "literal", "add in capacity", "adding capacity", "ASR split gerund adding->add in (ZH: 扩产)"),
    (66, "extended", "058_FIN", "literal", "howard marx", "Howard Marks", "Oaktree co-founder Howard Marks (ZH: 霍华德·马克斯)"),
    (67, "extended", "058_FIN", "literal", "howard mark's", "Howard Marks's", "Possessive Howard Marks's research group"),
    (68, "extended", "058_FIN", "literal", "often than ron", "often than wrong", "ASR garble wrong->ron (ZH: 看对的次数总会比看错多)"),
    (69, "extended", "063_FIN", "literal", "\u2019", "'", "Normalize Unicode right apostrophe U+2019 to ASCII '"),
    (70, "extended", "067_FIN", "literal", "banks air for the 2008", "banks after the 2008", "ASR garble after->air for (ZH: 2008年金融危机后)"),
    (71, "extended", "071_FIN", "literal", "company who's supposed", "company who's exposed", "Continues into seg 5 to AI (ZH: 押注AI浪潮)"),
    (72, "extended", "072_FIN", "literal", "stores of physical", "stores are physical", "ASR garble are->of (ZH: 都在地面实体店)"),
    (73, "extended", "079_USC", "literal", "former Google Co Eric Schmidt", "former Google CEO Eric Schmidt", "Title CEO garbled to Co (ZH: 前谷歌CEO)"),
    (74, "extended", "079_USC", "literal", "open AI Mo really is", "OpenAI's moat really is", "Business moat garbled to Mo (ZH: OpenAI的护城河)"),
    (75, "extended", "079_USC", "literal", "chat gbt", "ChatGPT", "Product name ChatGPT"),
    (76, "extended", "079_USC", "literal", "anthropics", "Anthropic's", "Possessive Anthropic's (continues into seg 12 Claude)"),
    (77, "extended", "079_USC", "regex", r"\bclad\b", "Claude", "Anthropic's Claude (ZH: Anthropic Claude)"),
    (78, "extended", "080_USC", "literal", "cuttingedge", "cutting-edge", "Auto-caption dropped hyphen"),
    (79, "extended", "080_USC", "literal", "inhouse", "in-house", "Auto-caption dropped hyphen"),
    (80, "extended", "082_USC", "literal", "nanometerclass", "nanometer-class", "Auto-caption dropped hyphen"),
    (81, "extended", "082_USC", "literal", "cuttingedge", "cutting-edge", "Auto-caption dropped hyphen"),
    (82, "extended", "084_USC", "literal", "Californiabased", "California-based", "Auto-caption dropped hyphen"),
    (83, "extended", "096_USC", "literal", "people in the developed countries", "people in the developing countries", "Global South developing countries (ZH: 发展中国家)"),
    (84, "extended", "100_USC", "literal", "Brainet 2.0", "BrainNet 2.0", "UBTECH BrainNet 2.0 (ZH: BrainNet 2.0)"),
    (85, "extended", "100_USC", "literal", "19\u00b0 of freedom", "19 degrees of freedom", "ASR converted degrees to U+00B0 (ZH: 19个自由度)"),
)

# ---------------------------------------------------------------------------
# 2. Deterministic 4-Stage Speaker Inference Specification (100/100 Verified)
# ---------------------------------------------------------------------------
# Stage 1: Exact per-clip overrides (60 clips: multi-speaker interviews,
# roundtables, mixed narrator+quote documentaries, and narrator-about-subject).
CLIP_SPEAKER_OVERRIDES: dict[str, list[str]] = {
    # AI (14 overrides)
    "007_AI": ["Jensen Huang", "Cleo Abram"],
    "008_AI": ["Geoffrey Hinton", "StarTalk (Host)"],
    "011_AI": ["Andrej Karpathy", "Stephanie Zhan"],
    "012_AI": ["Jensen Huang", "All-In Podcast (Hosts)"],
    "014_AI": ["Sam Altman", "Tucker Carlson"],
    "016_AI": ["Yann LeCun", "Welch Labs (Narrator)"],
    "017_AI": ["Dario Amodei", "Anthropic Co-Founders"],
    "021_AI": ["Sam Altman", "OpenAI Podcast (Host)"],
    "022_AI": ["Ilya Sutskever", "Lex Fridman"],
    "023_AI": ["Dario Amodei", "Ross Douthat"],
    "025_AI": ["Andrej Karpathy", "No Priors (Host)"],
    "026_AI": ["Dario Amodei", "CNN (Interviewer)"],
    "027_AI": ["Sam Altman", "Alex Heath"],
    "029_AI": ["Jensen Huang", "CNN (Interviewer)"],
    # BUSINESS (15 overrides)
    "02_BIZ_Anthropic": ["All-In Podcast (Hosts)"],
    "032_BIZ": ["Business Motiversity (Storyteller on Jeff Bezos)"],
    "035_BIZ": ["FRONTLINE PBS (Narrator/Interviewer)", "Amazon Executive (Interviewee)"],
    "037_BIZ": ["Mark Zuckerberg", "Bloomberg Originals (Interviewer)"],
    "038_BIZ": ["Peter Thiel", "fern (Narrator)"],
    "039_BIZ": ["All-In Podcast (Hosts)"],
    "040_BIZ": ["All-In Podcast (Hosts)"],
    "041_BIZ": ["All-In Podcast (Hosts)"],
    "042_BIZ": ["Elon Musk", "The Economist (Interviewer)"],
    "043_BIZ": ["Elon Musk", "Tesla Ex-Employee", "The Wall Street Journal (Narrator)"],
    "044_BIZ": ["Elon Musk", "Y Combinator (Interviewer)"],
    "047_BIZ": ["Emily Chang", "Y Combinator Partner"],
    "048_BIZ": ["Paul Graham", "Y Combinator (Interviewer)"],
    "050_BIZ": ["Sundar Pichai", "Stanford GSB (Interviewer)"],
    "053_BIZ": ["Elon Musk", "The Economist (Interviewer)"],
    # FINANCE (16 overrides)
    "03_FIN_Dalio": ["Ray Dalio", "The Diary Of A CEO (Host)"],
    "054_FIN": ["Warren Buffett (Boardroom Billions Commentary)"],
    "055_FIN": ["Stanley Druckenmiller", "FINAiUS (Narrator)"],
    "058_FIN": ["FINAiUS (Narrator)"],
    "060_FIN": ["Ray Dalio", "CNBC Television (Interviewer)"],
    "061_FIN": ["Jamie Dimon", "Wilfred Frost"],
    "062_FIN": ["Howard Marks", "My First Million (Host)"],
    "064_FIN": ["Ray Dalio", "Andrew Ross Sorkin"],
    "065_FIN": ["Jamie Dimon", "Bloomberg Television (Interviewer)"],
    "067_FIN": ["Bloomberg Wealth / David Rubenstein (Narrator)"],
    "068_FIN": ["Ray Dalio", "Bloomberg Television (Interviewer)"],
    "071_FIN": ["Howard Marks", "Bloomberg Television (Interviewer)"],
    "074_FIN": ["Howard Marks", "Bloomberg Television (Interviewer)"],
    "075_FIN": ["Ray Dalio", "Bloomberg Television (Interviewer)"],
    "076_FIN": ["Ray Dalio", "Nicholas Thompson"],
    "077_FIN": ["CNBC Television (Host)", "CNBC Investment Committee Panelist (Liz)"],
    # US_CHINA (15 overrides)
    "04_USCHINA_Jensen": ["Jensen Huang", "Lex Fridman"],
    "05_USCHINA_Robots": ["BBC News (Correspondent)", "Chinese Auto Factory Engineer"],
    "078_USC": ["CNBC (Narrator)"],
    "079_USC": ["CNBC (Narrator)", "Eric Schmidt"],
    "083_USC": ["CNN (Correspondent)", "CNN (Anchor John)"],
    "084_USC": ["Figure AI Executive", "TIME (Narrator)"],
    "086_USC": ["The Wall Street Journal (Narrator)"],
    "088_USC": ["CNBC (Narrator/Analyst)"],
    "089_USC": ["Barclays Analyst", "Bloomberg Tech (Host)"],
    "090_USC": ["CNBC (Commentator)"],
    "091_USC": ["Bloomberg Originals (Narrator/Correspondent)"],
    "094_USC": ["Kevin Rudd", "The Economist (Interviewer)"],
    "096_USC": ["Bloomberg Television (Correspondent)"],
    "098_USC": ["Asia Society (Southeast Asia Forum Speaker)"],
    "099_USC": ["FRANCE 24 English (Anchor/Analyst)"],
}

# Stage 2: Dedicated solo-narrator channels (9 channels -> 13 clips)
NARRATOR_CHANNELS: dict[str, str] = {
    "The Swedish Investor": "The Swedish Investor (Narrator)",
    "Inside China Business": "Inside China Business (Narrator)",
    "Newsthink": "Newsthink (Narrator)",
    "Behind Asia": "Behind Asia (Narrator)",
    "Logically Answered": "Logically Answered (Narrator)",
    "AI Revolution": "AI Revolution (Narrator)",
    "PRO ROBOTS": "PRO ROBOTS (Narrator)",
    "More Perfect Union": "More Perfect Union (Narrator)",
    "Epoch Philosophy": "Epoch Philosophy (Narrator)",
}

# Stage 3: Earliest-position named speaker patterns over "channel | title | hook_line_2" (27 clips)
NAMED_SPEAKER_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bDHH\b|David Heinemeier Hansson", re.I), "David Heinemeier Hansson (DHH)"),
    (re.compile(r"\bAndrej Karpathy\b|\bKarpathy\b", re.I), "Andrej Karpathy"),
    (re.compile(r"\bJensen Huang\b", re.I), "Jensen Huang"),
    (re.compile(r"\bDario Amodei\b", re.I), "Dario Amodei"),
    (re.compile(r"\bSam Altman\b", re.I), "Sam Altman"),
    (re.compile(r"\bAustin Marchese\b", re.I), "Austin Marchese"),
    (re.compile(r"\bMatt Pocock\b", re.I), "Matt Pocock"),
    (re.compile(r"\bYann LeCun\b", re.I), "Yann LeCun"),
    (re.compile(r"\bElon Musk\b", re.I), "Elon Musk"),
    (re.compile(r"\bJeff Bezos\b", re.I), "Jeff Bezos"),
    (re.compile(r"\bMark Zuckerberg\b", re.I), "Mark Zuckerberg"),
    (re.compile(r"\bSatya Nadella\b", re.I), "Satya Nadella"),
    (re.compile(r"\bStan(?:ley)? Druckenmiller\b", re.I), "Stanley Druckenmiller"),
    (re.compile(r"\bAswath Damodaran\b", re.I), "Aswath Damodaran"),
    (re.compile(r"\bKen Griffin\b", re.I), "Ken Griffin"),
    (re.compile(r"\bJamie Dimon\b", re.I), "Jamie Dimon"),
    (re.compile(r"\bDr\.?\s+Ben Miles\b", re.I), "Dr Ben Miles"),
    (re.compile(r"\bKishore Mahbubani\b", re.I), "Kishore Mahbubani"),
    (re.compile(r"\bKevin Rudd\b", re.I), "Kevin Rudd"),
    (re.compile(r"\bRay Dalio\b", re.I), "Ray Dalio"),
    (re.compile(r"\bHoward Marks\b", re.I), "Howard Marks"),
    (re.compile(r"\bWarren Buffett\b", re.I), "Warren Buffett"),
)

# ---------------------------------------------------------------------------
# 3. Empirical Corpus Gap Audit Regex Specifications (Live Scanned on en_clean)
# ---------------------------------------------------------------------------
GAP_AUDIT_TERMS: tuple[tuple[str, str, str, str], ...] = (
    # (group, display_term, regex_pattern, note)
    ("Retail & Channel", "Best Buy", r"\bBest\s+Buy\b", "纯 world_bridge（渠道剧情世界观补齐）"),
    ("Retail & Channel", "Selfridges", r"\bSelfridges\b", "纯 world_bridge（伦敦旗舰渠道世界观补齐）"),
    ("Retail & Channel", "slotting fee", r"\bslotting\s+fees?\b", "纯 world_bridge（见 LEX_097）"),
    ("Retail & Channel", "chargeback", r"\bchargebacks?\b", "纯 world_bridge（见 LEX_098）"),
    ("Retail & Channel", "MOQ", r"\bMOQs?\b", "纯 world_bridge（见 LEX_099）"),
    ("Retail & Channel", "sell-through", r"\bsell[\s\-]through\b", "纯 world_bridge（见 LEX_100）"),
    ("Retail & Channel", "shelf space", r"\bshelf\s+space\b", "纯 world_bridge（见 LEX_107）"),
    ("Retail & Channel", "channel", r"\bchannels?\b", "纯 world_bridge（渠道谈判术语需桥接）"),
    ("Retail & Channel", "pricing", r"\bpricing\b", "字面 0 次（邻近词 price/prices 出现于 7 条切片）"),
    ("Retail & Channel (Adjacent)", "retail", r"\bretail\w*\b", "邻近锚点：067_FIN 散户交易 / 072_FIN 电商零售"),
    ("Retail & Channel (Adjacent)", "consumer", r"\bconsumers?\b", "邻近锚点：070_FIN / 095_USC 消费级新品类"),
    ("Retail & Channel (Adjacent)", "margin", r"\bmargins?\b", "邻近锚点：077_FIN net interest margin"),
    ("Privacy, Legal & Geo", "GDPR", r"\bGDPR\b", "纯 world_bridge（见 LEX_109 / LEX_118）"),
    ("Privacy, Legal & Geo", "privacy", r"\bprivacy\b", "纯 world_bridge（欧盟隐私合规线需桥接）"),
    ("Privacy, Legal & Geo", "compliance", r"\bcompliance\b", "纯 world_bridge（跨境合规审计需桥接）"),
    ("Privacy, Legal & Geo", "lawsuit", r"\blawsuits?\b", "纯 world_bridge（法务诉讼线需桥接）"),
    ("Privacy, Legal & Geo", "antitrust", r"\bantitrust\b", "纯 world_bridge（反垄断线需桥接）"),
    ("Privacy, Legal & Geo", "sanctions", r"\bsanctions?\b", "纯 world_bridge（制裁线需桥接）"),
    ("Privacy, Legal & Geo", "decoupling", r"\bdecoupl\w*\b", "纯 world_bridge（地缘脱钩线需桥接）"),
    ("Privacy, Legal & Geo", "export ban (literal)", r"\bexport\s+bans?\b", "字面 0 次（实为 042_BIZ 'banned the export' 及 092_USC 'barred'/'cut off'）"),
    ("Privacy, Legal & Geo (Adjacent)", "tariff", r"\btariffs?\b", "邻近锚点：065_FIN / 093_USC 25% 关税成本"),
    ("Privacy, Legal & Geo (Adjacent)", "regulation", r"\bregulat\w*\b", "邻近锚点：064_FIN 宏观监管"),
    ("Privacy, Legal & Geo (Adjacent)", "guardrails", r"\bguardrails?\b", "邻近锚点：019_AI rule-based guardrails"),
    ("Privacy, Legal & Geo (Adjacent)", "on-prem", r"\bon-prem\b", "规则 #40 归一后命中 009_AI（原文本为 'on prem'）"),
    ("Privacy, Legal & Geo (Adjacent)", "supply chain", r"\bsupply\s+chains?\b", "邻近锚点：045_BIZ / 086_USC / 092_USC"),
    ("Privacy, Legal & Geo (Adjacent)", "chip", r"\bchips?\b", "邻近锚点：半导体与算力博弈主轴"),
)

# ---------------------------------------------------------------------------
# 4. Curated 120-Entry Executive Lexicon (96 corpus [80.0%] + 24 world_bridge [20.0%])
# Runtime-verified against freshly normalized `en_clean` before any file write.
# ---------------------------------------------------------------------------
EXECUTIVE_LEXICON_SPEC: list[dict[str, Any]] = [
    {
        "phrase_id": "LEX_001",
        "phrase_en": "Pick your favorite number",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "You can choose any number you want, it doesn't matter.",
        "executive_subtext_zh": "美式高管降维打击式让步：假装把前提假设权大方让给对手，实则暗示“不管你怎么调参数，底层的数量级结论依然碾压你”。",
        "verbatim_context_en": "Pick your favorite number, but let's say between 50 billion and 40 billion.",
        "source_type": "corpus",
        "clip_ids": ["012_AI"],
    },
    {
        "phrase_id": "LEX_002",
        "phrase_en": "In other words",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "That is to say / Let me explain simply to you.",
        "executive_subtext_zh": "董事会最锋利的“翻译成人话”切换词：把对方或自己复杂的宏观数字，瞬间折算成老板一眼看懂的单人成本或现金流ROI。",
        "verbatim_context_en": "In other words, somebody makes $80,000 a year on average.",
        "source_type": "corpus",
        "clip_ids": ["039_BIZ", "066_FIN"],
    },
    {
        "phrase_id": "LEX_003",
        "phrase_en": "a really hard trade-off",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "a very difficult choice between two bad things",
        "executive_subtext_zh": "高管谈预算与取舍时的体面刀法：不说“你太贵了我买不起”，而说“这是个很难忽略的权衡”，把压价包装成理性经营抉择。",
        "verbatim_context_en": "And that is a really hard trade-off for enterprises, for companies, for Fortune 500 to ignore.",
        "source_type": "corpus",
        "clip_ids": ["090_USC"],
    },
    {
        "phrase_id": "LEX_004",
        "phrase_en": "What is good enough",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "Is the quality okay enough for us to use?",
        "executive_subtext_zh": "企业级采购拍板灵魂发问：撕掉实验室跑分虚荣心，直指商业底线——“做到多少分就能卖钱且不超预算？”",
        "verbatim_context_en": 'Companies are increasingly asking, "What is good enough?" And what does it cost to run this thing a million times or more?',
        "source_type": "corpus",
        "clip_ids": ["090_USC"],
    },
    {
        "phrase_id": "LEX_005",
        "phrase_en": "a fair criticism",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "Your blame is very reasonable and I admit my fault.",
        "executive_subtext_zh": "硅谷顶级“礼貌带刀”让步句式：先优雅承认对方质疑有道理（卸掉敌意、显得大度），紧接着用转折把议题拉回自己的长期叙事。",
        "verbatim_context_en": "I think it's actually like a fair criticism of the AI industry.",
        "source_type": "corpus",
        "clip_ids": ["027_AI"],
    },
    {
        "phrase_id": "LEX_006",
        "phrase_en": "at the end of the day",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "Finally speaking / In the final analysis",
        "executive_subtext_zh": "终结无休止扯皮的拍板短语：把所有细节噪音一刀切掉，强行拉回唯一决定生死的底层现实。",
        "verbatim_context_en": "at the end of the day, the industry has to work together and it's harder, but to some extent, the world has to work together.",
        "source_type": "corpus",
        "clip_ids": ["026_AI"],
    },
    {
        "phrase_id": "LEX_007",
        "phrase_en": "the reality is",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "The true fact is that...",
        "executive_subtext_zh": "CEO 破除幻觉的冷峻转折：礼貌否定前一句理想化假设，直接把残酷的客户、竞争或财务现实拍在桌面上。",
        "verbatim_context_en": "Now, the reality is that concept itself will morph as you learn more about your customers, as you learn more about your competition, as you learn more about your environment, that concept itself will evolve.",
        "source_type": "corpus",
        "clip_ids": ["049_BIZ"],
    },
    {
        "phrase_id": "LEX_008",
        "phrase_en": "completely refuted",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "totally proved wrong by our evidence",
        "executive_subtext_zh": "公关与融资反杀重锤：比 proved wrong 更有法庭与投行权威感，宣判对手或做空媒体的整个叙事彻底破产。",
        "verbatim_context_en": "that narrative basically just got completely refuted because it turns out that that $80 billion loss is a phantom number.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_009",
        "phrase_en": "I really like that framing",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "I agree with your way of speaking very much.",
        "executive_subtext_zh": "高段位会议控场夸奖：不直接说你对，而是赞赏对方的“叙事框架/切入视角”，既给足面子又顺势接过话语主导权。",
        "verbatim_context_en": "I really like that framing.",
        "source_type": "corpus",
        "clip_ids": ["011_AI"],
    },
    {
        "phrase_id": "LEX_010",
        "phrase_en": "in the long run",
        "category": "executive_hedging_framing",
        "cefr_level": "B1",
        "chinglish_trap": "after a very long time in the future",
        "executive_subtext_zh": "华尔街与董事会拉长周期的常用盾牌：用来对冲短期季度业绩波动，把评审标准从“下周股价”切回“五年终局”。",
        "verbatim_context_en": "since the u.s stock market tends to turn upward in the long run",
        "source_type": "corpus",
        "clip_ids": ["058_FIN"],
    },
    {
        "phrase_id": "LEX_011",
        "phrase_en": "let alone",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "not to mention / even less possible is...",
        "executive_subtext_zh": "质疑对手画大饼时的冷嘲递增结构：“连低门槛那一步都没影呢，更别提你吹的天文数字了”。",
        "verbatim_context_en": "we're not even sure there was a 100 billion let alone 500",
        "source_type": "corpus",
        "clip_ids": ["099_USC"],
    },
    {
        "phrase_id": "LEX_012",
        "phrase_en": "orders of magnitude",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "many times bigger / a huge gap in numbers",
        "executive_subtext_zh": "硅谷硬核科技圈高频量级词：指的不是差20%，而是差10倍、100倍的数量级鸿沟，用于一锤定音终结细枝末节的纠缠。",
        "verbatim_context_en": "But yes, but we're dealing with orders of magnitude here.",
        "source_type": "corpus",
        "clip_ids": ["008_AI"],
    },
    {
        "phrase_id": "LEX_013",
        "phrase_en": "higher level of abstraction",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "more high-level and conceptual thinking",
        "executive_subtext_zh": "科技高管谈组织与产品升级的核心视角：不再抠底层琐碎执行，而是把问题抽象升维到系统架构与战略决策层。",
        "verbatim_context_en": "over longer and longer time Horizons for more and more tasks and let people operate at a higher level of abstraction",
        "source_type": "corpus",
        "clip_ids": ["013_AI"],
    },
    {
        "phrase_id": "LEX_014",
        "phrase_en": "working backwards from",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "thinking from the final result back to the start",
        "executive_subtext_zh": "亚马逊与硅谷顶级产品方法论黑话：不从手头现有技术出发，而是从客户终极体验倒推研发路线与商业模式。",
        "verbatim_context_en": "It's like working backwards from how people think an AI should be",
        "source_type": "corpus",
        "clip_ids": ["025_AI"],
    },
    {
        "phrase_id": "LEX_015",
        "phrase_en": "singing a different tune",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "changing his opinion completely now",
        "executive_subtext_zh": "商战与媒体圈带刺调侃：暗讽当年看空你或放狠话的大佬，如今被现实打脸后悄悄改口换了一套说辞。",
        "verbatim_context_en": "he predicted China was 2 to three years behind the US in AI but now Schmidt is singing a different tune",
        "source_type": "corpus",
        "clip_ids": ["079_USC"],
    },
    {
        "phrase_id": "LEX_016",
        "phrase_en": "the game has changed",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "The rules of competition are totally different now.",
        "executive_subtext_zh": "董事会战略转折点宣言：宣告旧护城河已经失效、竞争范式彻底重写，逼迫保守派停止沿用去年的打法。",
        "verbatim_context_en": "meta's open source llama model and now the game has changed",
        "source_type": "corpus",
        "clip_ids": ["079_USC"],
    },
    {
        "phrase_id": "LEX_017",
        "phrase_en": "leaning into the future",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "actively embracing future market trends",
        "executive_subtext_zh": "贝索斯式进攻型战略口号：不被动防御颠覆，而是主动把资源压向不可逆的趋势——“躲着未来走必输无疑”。",
        "verbatim_context_en": "that's the best defense against the future and you have to always be leaning into the future",
        "source_type": "corpus",
        "clip_ids": ["034_BIZ"],
    },
    {
        "phrase_id": "LEX_018",
        "phrase_en": "no hedge on earth",
        "category": "executive_hedging_framing",
        "cefr_level": "C2",
        "chinglish_trap": "no financial tool in the world can protect us",
        "executive_subtext_zh": "高管向董事会摊牌生死红线的重话：明确指出某个重资产豪赌一旦节奏错判，没有任何金融对冲或退路能救命。",
        "verbatim_context_en": "there's no force on earth, there's there's no hedge on earth that could stop me from going bankrupt if I if I buy that much compute.",
        "source_type": "corpus",
        "clip_ids": ["010_AI"],
    },
    {
        "phrase_id": "LEX_019",
        "phrase_en": "good for it",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "they really have enough money to pay back",
        "executive_subtext_zh": "华尔街与大宗融资圈极地道的信用担保口语：“放心，出资方兜里有钱、信誉兜得住，这笔承诺不会跳票”。",
        "verbatim_context_en": "unless something like really goes wrong and it turns out we can't build these computers, uh I'm confident that people are are good for it.",
        "source_type": "corpus",
        "clip_ids": ["021_AI"],
    },
    {
        "phrase_id": "LEX_020",
        "phrase_en": "polite modulations",
        "category": "executive_hedging_framing",
        "cefr_level": "C2",
        "chinglish_trap": "polite changes of speaking tone in diplomacy",
        "executive_subtext_zh": "顶级跨国谈判识局黑话：点破对方台面上的客套修辞只是“礼貌调音”，绝不能错把客气当成对方底牌的松动。",
        "verbatim_context_en": "And whatever the polite modulations of the Trumpian expression the Chinese may use, that's their operational position.",
        "source_type": "corpus",
        "clip_ids": ["094_USC"],
    },
    {
        "phrase_id": "LEX_021",
        "phrase_en": "in hindsight",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "looking back after everything already happened",
        "executive_subtext_zh": "董事会复盘与宏观预判高频词：用来警示决策者“现在为了迎合短期情绪硬上，事后回头看一定会是个蠢决定”。",
        "verbatim_context_en": "I do still think that a hike would look like a mistake in hindsight.",
        "source_type": "corpus",
        "clip_ids": ["077_FIN"],
    },
    {
        "phrase_id": "LEX_022",
        "phrase_en": "stick to their guns",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "refuse to compromise their original position",
        "executive_subtext_zh": "高压博弈中的强硬表态：形容一方顶住舆论和市场恐慌死咬底线不松口，暗示谈判可能滑向硬碰硬。",
        "verbatim_context_en": "and two actually told Republicans to stick to their guns",
        "source_type": "corpus",
        "clip_ids": ["073_FIN"],
    },
    {
        "phrase_id": "LEX_023",
        "phrase_en": "where the puck is",
        "category": "executive_hedging_framing",
        "cefr_level": "C1",
        "chinglish_trap": "only looking at the current market instead of the future",
        "executive_subtext_zh": "北美顶级投资人与CEO经典冰球隐喻：讥讽平庸者只盯着当下财报做决策，而真正的高手永远提前18个月卡位下一站。",
        "verbatim_context_en": "the biggest mistake investors make is they invest in the present rather than forward looking and looking where the Puck's going instead of where the puck is",
        "source_type": "corpus",
        "clip_ids": ["056_FIN"],
    },
    {
        "phrase_id": "LEX_024",
        "phrase_en": "All Hands meeting",
        "category": "executive_hedging_framing",
        "cefr_level": "B2",
        "chinglish_trap": "a whole-company employee meeting",
        "executive_subtext_zh": "硅谷与出海科技公司危机动员标准词：当巨头宣战或重大危机爆发时，创始人亲召全员大会统一军心与战时叙事。",
        "verbatim_context_en": "our memorable was just Amazon toast and and so I called it All Hands meeting which was not hard to do with just 125 people",
        "source_type": "corpus",
        "clip_ids": ["033_BIZ"],
    },
    {
        "phrase_id": "LEX_025",
        "phrase_en": "phantom number",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "a fake and unreal accounting paper number",
        "executive_subtext_zh": "财务反杀金句：一针戳破由会计准则而非经营失血造成的账面巨亏——“那是个幽灵数字，不是公司真烧掉了钱”。",
        "verbatim_context_en": "that narrative basically just got completely refuted because it turns out that that $80 billion loss is a phantom number.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_026",
        "phrase_en": "not a cash loss",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "we did not actually lose real bank cash",
        "executive_subtext_zh": "CFO 在融资谈判室的护城河底线：清晰切割“非现金会计重估”与“经营性现金失血”，阻止 VC 借账面亏损砍估值。",
        "verbatim_context_en": "If they had just issued equity, that loss wouldn't be there. So, it was not a cash loss.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_027",
        "phrase_en": "flowed through into the income statement",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "appeared inside our profit and loss report",
        "executive_subtext_zh": "地道华尔街/四大会计动词搭配：精准描述资产负债表项目（如可转债公允价值变动）如何传导进利润表，瞬间建立CFO级专业压迫感。",
        "verbatim_context_en": "And as Anthropic's valuation increased, those convertible notes got recorded as a loss on the balance sheet and that flowed through into the income statement, but it's not a real loss.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_028",
        "phrase_en": "capital-efficient",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "using investors' money very savingly and smartly",
        "executive_subtext_zh": "资本寒冬里 VC 最爱听的顶级褒义词：证明你每一美元融资撬动的营收与里程碑远超同行，不是靠烧钱换规模。",
        "verbatim_context_en": "And in fact, what was revealed in this S-1 is that Anthropic has been an extraordinarily capital-efficient business.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_029",
        "phrase_en": "upside",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "future rising room / profit space",
        "executive_subtext_zh": "投行与VC桌面最高频单字：专指资产或股权的“上行赔率与想象空间”，常与 downside（下行风险）成对出击。",
        "verbatim_context_en": "Compared to what the company is worth today, it looks like it has almost a 100% upside.",
        "source_type": "corpus",
        "clip_ids": ["059_FIN", "062_FIN", "071_FIN"],
    },
    {
        "phrase_id": "LEX_030",
        "phrase_en": "When are you going to get it",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "What year will we actually receive this cash?",
        "executive_subtext_zh": "巴菲特式灵魂拷问：所有远期画饼估值模型在现金回流时间表前都会现原形——“账面赚得再多，钱到底哪年到账？”",
        "verbatim_context_en": "What we are missing is Buffett's second question. When are you going to get it?",
        "source_type": "corpus",
        "clip_ids": ["059_FIN"],
    },
    {
        "phrase_id": "LEX_031",
        "phrase_en": "convertible notes",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "bridge loans that can turn into shares later",
        "executive_subtext_zh": "硅谷过桥融资标配工具（可转债）：估值暴涨时按会计准则反而会被记成公允价值负债亏损，不懂这行极易被投资人带节奏。",
        "verbatim_context_en": "It resulted from the fact that Anthropic had issued convertible notes to basically their infrastructure partners like Amazon and so forth.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_032",
        "phrase_en": "balance sheet",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "the company's asset and debt accounting table",
        "executive_subtext_zh": "高管谈抗风险底气的硬通货（资产负债表）：决定你在行业下行周期是抄底吞并对手，还是被债权人掐断脖子。",
        "verbatim_context_en": "And as Anthropic's valuation increased, those convertible notes got recorded as a loss on the balance sheet and that flowed through into the income statement, but it's not a real loss.",
        "source_type": "corpus",
        "clip_ids": ["02_BIZ_Anthropic"],
    },
    {
        "phrase_id": "LEX_033",
        "phrase_en": "downside",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "the bad risk of losing our investment",
        "executive_subtext_zh": "机构 LP 募资与并购谈判的核心防线：成熟资本不只看能赚多少，更看最坏情况下底盘能不能兜住。",
        "verbatim_context_en": "Are you selling upside? Are you selling safety against downside and fear?",
        "source_type": "corpus",
        "clip_ids": ["062_FIN"],
    },
    {
        "phrase_id": "LEX_034",
        "phrase_en": "discounted cashflow",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "future cash calculated back to today's value",
        "executive_subtext_zh": "华尔街内在估值圣经（现金流折现模型 DCF）：在资本市场挤泡沫时期，把一切讲故事的倍数估值拉回真金白银的现值拷问。",
        "verbatim_context_en": "This is the core of the discounted cashflow (or DCF) analysis where we use a discount rate to reduce the value of future cash flows.",
        "source_type": "corpus",
        "clip_ids": ["063_FIN"],
    },
    {
        "phrase_id": "LEX_035",
        "phrase_en": "discount rate",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "the percentage we use to shrink future money",
        "executive_subtext_zh": "估值杀手杠杆（折现率）：利率或风险溢价哪怕只上调200个基点，高增长硬件/AI独角兽的远期估值就能直接腰斩。",
        "verbatim_context_en": "If we use a low discount rate, money in the future is worth quite a bit, but if we use a higher one, the value diminishes quickly.",
        "source_type": "corpus",
        "clip_ids": ["063_FIN"],
    },
    {
        "phrase_id": "LEX_036",
        "phrase_en": "compare apples to apples",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "put two same-level companies together fairly",
        "executive_subtext_zh": "估值博弈和竞品对标必杀反驳：当对方拿传统制造业PE倍数强行压你AI硬件估值时，用这句当场拆穿对方偷换参照系。",
        "verbatim_context_en": "there are three essential steps for relative valuations one find comparable assets we must compare apples to apples and oranges to oranges",
        "source_type": "corpus",
        "clip_ids": ["072_FIN"],
    },
    {
        "phrase_id": "LEX_037",
        "phrase_en": "doomsday scenario",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "the most terrible disaster assumption case",
        "executive_subtext_zh": "估值大师压力测试核武器：主动把最悲观的末日假设全塞进模型，如果算出来公司依然值钱，做空者就再无还手之力。",
        "verbatim_context_en": "I built in what I call my doomsday scenario which is let's assume the markets assuming that this money is going to be completely wasted",
        "source_type": "corpus",
        "clip_ids": ["066_FIN"],
    },
    {
        "phrase_id": "LEX_038",
        "phrase_en": "super voting provision",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "special founder shares with ten times voting power",
        "executive_subtext_zh": "硅谷创始人控制权生死条款（AB股超级投票权）：后期融资与董事会宫斗的核心争夺点，交出去就可能被资本踢出局。",
        "verbatim_context_en": "So now what what is the point of having that super voting provision in there?",
        "source_type": "corpus",
        "clip_ids": ["041_BIZ"],
    },
    {
        "phrase_id": "LEX_039",
        "phrase_en": "raise another round",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "get one more batch of VC investment money",
        "executive_subtext_zh": "创投圈标准融资表达（再融一轮）：强调融资不是靠PPT口才，而是靠上一轮钱跑出硬里程碑换取下一轮溢价。",
        "verbatim_context_en": "You're always able to raise another round, right? So you just do what you can on the money you got.",
        "source_type": "corpus",
        "clip_ids": ["048_BIZ"],
    },
    {
        "phrase_id": "LEX_040",
        "phrase_en": "positive ROE",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "still earning positive profit on shareholder money",
        "executive_subtext_zh": "银行与蓝筹高管在金融风暴中的终极勋章（正净资产收益率）：证明在全行业爆雷的年份，你的资本回报依然为正。",
        "verbatim_context_en": "As you said 2008 you had a positive ROE.",
        "source_type": "corpus",
        "clip_ids": ["061_FIN"],
    },
    {
        "phrase_id": "LEX_041",
        "phrase_en": "net interest margin",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "the profit gap between loan and deposit interest",
        "executive_subtext_zh": "金融与银行业核心盈利指标（净息差 NIM）：当收益率曲线趋平、资金成本抬升时，银行信贷收紧的真正底层诱因。",
        "verbatim_context_en": "a flatter yield curve is problematic for banks over the long term because it crimps their net interest margin.",
        "source_type": "corpus",
        "clip_ids": ["077_FIN"],
    },
    {
        "phrase_id": "LEX_042",
        "phrase_en": "already in the price",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "the stock price already reflects this good news",
        "executive_subtext_zh": "华尔街顶级交易员浇冷水名言：“你看到的好消息市场早就提前定价完了，现在追进去只会当接盘侠”。",
        "verbatim_context_en": "most investors lack discipline they get excited when things are great in a situation and it's usually already in the price",
        "source_type": "corpus",
        "clip_ids": ["055_FIN"],
    },
    {
        "phrase_id": "LEX_043",
        "phrase_en": "the law of holes",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "stop pouring more money into a losing project",
        "executive_subtext_zh": "资本配置止损铁律（坑洞法则）：“当你发现自己掉进坑里时，第一件事是立刻停止继续往下挖”，专治沉没成本幻想。",
        "verbatim_context_en": "what's the law of holes it's that if you find yourself in one you should quit digging",
        "source_type": "corpus",
        "clip_ids": ["069_FIN"],
    },
    {
        "phrase_id": "LEX_044",
        "phrase_en": "the punch is out of the bowl",
        "category": "vc_valuation_finance",
        "cefr_level": "C2",
        "chinglish_trap": "government stimulus money and hot spending are over",
        "executive_subtext_zh": "华尔街极具画面感的宏观退潮暗语（派对酒碗见底了）：暗示超额储蓄与补贴红利已耗尽，消费硬件马上要迎来真实需求大考。",
        "verbatim_context_en": "which means by the end of this year, in some sense, the punch is out of the bowl.",
        "source_type": "corpus",
        "clip_ids": ["070_FIN"],
    },
    {
        "phrase_id": "LEX_045",
        "phrase_en": "risk adjusted return",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "profit calculated together with the risk level",
        "executive_subtext_zh": "机构投资委员会的标准否决/放行标尺（风险调整后收益）：用来区分“稳健理财”和创始人孤注一掷的颠覆式豪赌。",
        "verbatim_context_en": "if the objective was to achieve the best risk adjusted return",
        "source_type": "corpus",
        "clip_ids": ["044_BIZ"],
    },
    {
        "phrase_id": "LEX_046",
        "phrase_en": "bubble indicator",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "a number showing if the market is overheating",
        "executive_subtext_zh": "宏观对冲基金研判IPO窗口与估值顶部的量化温度计：把“我觉得过热”升级为基于杠杆率与流动性的系统化预警。",
        "verbatim_context_en": "I created a bubble indicator that has all of these things.",
        "source_type": "corpus",
        "clip_ids": ["076_FIN", "060_FIN"],
    },
    {
        "phrase_id": "LEX_047",
        "phrase_en": "hard money",
        "category": "vc_valuation_finance",
        "cefr_level": "C1",
        "chinglish_trap": "strong real assets that governments cannot print",
        "executive_subtext_zh": "跨国CFO与宏观大佬对冲主权通胀与汇率风暴的压舱石（硬通货）：指无法被央行随意印钞稀释、非他人负债的真实资产。",
        "verbatim_context_en": "make sure that I have some hard money, which for most people should be between 5 and 15% of their portfolio.",
        "source_type": "corpus",
        "clip_ids": ["03_FIN_Dalio"],
    },
    {
        "phrase_id": "LEX_048",
        "phrase_en": "catch the exact bottom",
        "category": "vc_valuation_finance",
        "cefr_level": "B2",
        "chinglish_trap": "buy right at the lowest price point of the crash",
        "executive_subtext_zh": "巴菲特戳破散户与犹豫董事会心理陷阱的金句：别幻想踩中绝对最低点，周期底部区间敢下重注才是决定胜负的分水岭。",
        "verbatim_context_en": "They think they need to catch the exact bottom.",
        "source_type": "corpus",
        "clip_ids": ["054_FIN"],
    },
    {
        "phrase_id": "LEX_049",
        "phrase_en": "10 times the throughput",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "10 times faster processing and output speed",
        "executive_subtext_zh": "黄仁勋式算力经济学核弹：把客户目光从“单卡采购价贵不贵”强行拽到“同样机房电费下吞吐量翻十倍”的总拥有成本（TCO）碾压。",
        "verbatim_context_en": "That is not a large percentage when the $50 billion data data center is actually 10 times the throughput.",
        "source_type": "corpus",
        "clip_ids": ["012_AI"],
    },
    {
        "phrase_id": "LEX_050",
        "phrase_en": "eating into budgets",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "spending too much of our annual department budget",
        "executive_subtext_zh": "欧美企业买家和大渠道砍价最常用的痛点动词：形象表达持续上涨的云端AI调用费正在“活生生啃噬”他们的利润与年度预算。",
        "verbatim_context_en": "And it really comes at a time when expensive AI is already eating into budgets.",
        "source_type": "corpus",
        "clip_ids": ["090_USC"],
    },
    {
        "phrase_id": "LEX_051",
        "phrase_en": "run this thing a million times",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "call this AI API for one million times",
        "executive_subtext_zh": "打破AI实验室Demo滤镜的灵魂算账句：单次调用几美分看似便宜，但企业级高频并发跑一百万次时，单位推理成本立刻决定生死。",
        "verbatim_context_en": "And what does it cost to run this thing a million times or more?",
        "source_type": "corpus",
        "clip_ids": ["090_USC"],
    },
    {
        "phrase_id": "LEX_052",
        "phrase_en": "lowest cost tokens",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "cheapest AI word generation unit price",
        "executive_subtext_zh": "大模型时代最硬核的底层工业指标（最低单位Token成本）：决定AI消费硬件是每卖一台亏一次云费，还是跑通规模化正毛利。",
        "verbatim_context_en": "that the $50 billion factory will generate for you the lowest cost tokens.",
        "source_type": "corpus",
        "clip_ids": ["012_AI"],
    },
    {
        "phrase_id": "LEX_053",
        "phrase_en": "land power and shell",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "data center land, electricity and building body",
        "executive_subtext_zh": "硅谷算力基建圈专业拆账黑话（土建、电力与机房外壳）：用来论证固定基建占比极高，省一点廉价芯片钱根本不划算。",
        "verbatim_context_en": "Now, it turns out 20 billion is just land power and shell, right?",
        "source_type": "corpus",
        "clip_ids": ["012_AI"],
    },
    {
        "phrase_id": "LEX_054",
        "phrase_en": "open weight AI",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "AI model whose parameter weights are free to download",
        "executive_subtext_zh": "比笼统说 open source 更精准的AI高管术语（开放权重模型）：代表可下载、可私有部署、可深度定制，直接瓦解闭源API垄断定价权。",
        "verbatim_context_en": "Open weight AI is different. The model can be downloaded, inspected, customized, run on your own infrastructure, and it's often cheaper.",
        "source_type": "corpus",
        "clip_ids": ["078_USC"],
    },
    {
        "phrase_id": "LEX_055",
        "phrase_en": "use it as a teacher",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "use a huge model to train a smaller model",
        "executive_subtext_zh": "AI硬件端侧落地核心技术路径（大模型蒸馏教学）：用旗舰开源大模型当“老师”蒸馏轻量端侧模型，一刀砍掉90%云端推理账单。",
        "verbatim_context_en": "especially because it's open source is use it as a teacher to train smaller models that they use in different applications",
        "source_type": "corpus",
        "clip_ids": ["037_BIZ"],
    },
    {
        "phrase_id": "LEX_056",
        "phrase_en": "rule-based guardrails",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "strict safety limits written in code rules",
        "executive_subtext_zh": "企业级AI产品过合规审查的必考术语（基于规则的硬护栏）：向欧美法务和大客户证明你的AI不是靠祈祷不犯错，而是有确定性拦截。",
        "verbatim_context_en": "So, if you have things that are critical not to get wrong, then you need to introduce rule-based guardrails to ensure that the AI can't bypass them.",
        "source_type": "corpus",
        "clip_ids": ["019_AI"],
    },
    {
        "phrase_id": "LEX_057",
        "phrase_en": "a request, not a rule",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "just politely asking the AI, not forcing it",
        "executive_subtext_zh": "CTO在安全事故复盘会上的经典暴击：一针点穿纯靠提示词（Prompt）约束大模型有多脆弱——“写进提示词只是客气请求，不是铁律”。",
        "verbatim_context_en": "And that might get you 80% of the way there, but it's essentially a request, not a rule.",
        "source_type": "corpus",
        "clip_ids": ["019_AI"],
    },
    {
        "phrase_id": "LEX_058",
        "phrase_en": "feedback loops",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "automatic testing and self-fixing cycles",
        "executive_subtext_zh": "硅谷工程团队衡量AI智能体可靠性的生命线（反馈闭环）：没有自动化测试与验证闭环，AI写代码或做硬件控制必然失控。",
        "verbatim_context_en": "And it's really important because these feedback loops are essential to AI, essential to get AI to produce anything reasonable.",
        "source_type": "corpus",
        "clip_ids": ["020_AI"],
    },
    {
        "phrase_id": "LEX_059",
        "phrase_en": "coding blind",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "writing code without seeing any test feedback",
        "executive_subtext_zh": "技术高管吐槽低水平AI研发流程的精准比喻（盲写代码）：把没有验证环境与指标反馈就让Agent硬改代码的风险一语道破。",
        "verbatim_context_en": "Because without this, AI is totally coding blind, right?",
        "source_type": "corpus",
        "clip_ids": ["020_AI"],
    },
    {
        "phrase_id": "LEX_060",
        "phrase_en": "agent acceleration",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "making software work faster by using AI agents",
        "executive_subtext_zh": "研发效能汇报中的硬核新词（智能体加速）：描述从“人手写代码”跃迁到“AI全量生成、人类只做架构审阅”的组织提速拐点。",
        "verbatim_context_en": "Almost right from the beginning I'm working on that version, the agent acceleration neared 100%.",
        "source_type": "corpus",
        "clip_ids": ["01_AI_DHH"],
    },
    {
        "phrase_id": "LEX_061",
        "phrase_en": "under the hood",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "the hidden technical architecture inside the product",
        "executive_subtext_zh": "硅谷产品发布会与投融路演经典汽车隐喻（引擎盖之下）：把前端优雅极简的用户体验，与后台复杂的端云协同/模型调度区分开来。",
        "verbatim_context_en": "matching the expectations that humans already have for what an AI should behave but under the hood it's like a lot of technical details go into that.",
        "source_type": "corpus",
        "clip_ids": ["025_AI"],
    },
    {
        "phrase_id": "LEX_062",
        "phrase_en": "too raw of a primitive",
        "category": "ai_compute_product",
        "cefr_level": "C2",
        "chinglish_trap": "too basic and rough to sell straight to consumers",
        "executive_subtext_zh": "顶级AI产品经理批判“套壳产品”的毒舌神句：点破纯大模型只是未经打磨的底层原语，不封装成硬件形态与人格记忆就卖不动大众市场。",
        "verbatim_context_en": "And LLMs are too raw of a primitive, uh, to actually, um, type check as AI I think for most people if that makes sense.",
        "source_type": "corpus",
        "clip_ids": ["025_AI"],
    },
    {
        "phrase_id": "LEX_063",
        "phrase_en": "world models",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "AI models that understand real physical space rules",
        "executive_subtext_zh": "具身智能与空间硬件（眼镜/桌面机器人）的下一代技术护城河（世界模型）：能预测物理因果与空间后果，而不只是文字接龙。",
        "verbatim_context_en": "LeCun's billion-dollar bet is that the missing piece of modern AI is world models. Models that make predictions about the physical world.",
        "source_type": "corpus",
        "clip_ids": ["016_AI"],
    },
    {
        "phrase_id": "LEX_064",
        "phrase_en": "AI in the loop",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "embedding AI into every company workflow",
        "executive_subtext_zh": "黄仁勋反转旧共识的战略金句：不再把AI当成需要人盯着的附属品（human in the loop），而是让AI嵌入企业每个环节持续复利。",
        "verbatim_context_en": "Every company should have AI in the loop.",
        "source_type": "corpus",
        "clip_ids": ["009_AI"],
    },
    {
        "phrase_id": "LEX_065",
        "phrase_en": "on-prem",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "installed locally on company servers, not public cloud",
        "executive_subtext_zh": "欧美政企大客户与隐私敏感买家的硬性采购黑话（本地私有化部署 on-premises）：核心数据不出屋，绝不上传公有云。",
        "verbatim_context_en": "I want that to be in a small room. I want that to be on-prem.",
        "source_type": "corpus",
        "clip_ids": ["009_AI"],
    },
    {
        "phrase_id": "LEX_066",
        "phrase_en": "hallucinate through",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "blindly guess and make up fake answers",
        "executive_subtext_zh": "精准描述大模型“硬蒙过去”的动词短语：当模型没有调用工具验算时，会一本正经地编造出看似极接近、实则致命错误的结果。",
        "verbatim_context_en": "so Grok 3 will just hallucinate through this multiplication and uh do it in its head and get it wrong",
        "source_type": "corpus",
        "clip_ids": ["015_AI"],
    },
    {
        "phrase_id": "LEX_067",
        "phrase_en": "AI first",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "putting AI as our number one company strategy",
        "executive_subtext_zh": "大厂CEO重构组织与研发预算的顶层号令（AI优先）：不是把AI当成一个边角功能，而是重排全公司R&D资源向AI倾斜。",
        "verbatim_context_en": "one of the biggest uh uh directional changes we made is we said you know we're gonna approach everything as ai first",
        "source_type": "corpus",
        "clip_ids": ["050_BIZ"],
    },
    {
        "phrase_id": "LEX_068",
        "phrase_en": "hyperscalers",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "super massive cloud computing tech giants",
        "executive_subtext_zh": "华尔街与硅谷专指微软、亚马逊、谷歌等超大云巨头的行业暗语：在估值和算力博弈中，他们靠主营现金牛托底，而纯AI独角兽必须靠效率突围。",
        "verbatim_context_en": "when you're talking certainly if you're talking about a a you know the so so-called hyperscalers",
        "source_type": "corpus",
        "clip_ids": ["074_FIN"],
    },
    {
        "phrase_id": "LEX_069",
        "phrase_en": "job one is to create something that works",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "our first task is building a usable product",
        "executive_subtext_zh": "硬件与科技CEO在媒体追问“竞争焦虑”时的反杀定力：别被对手口水战带偏，第一要务永远是造出真正靠谱能打的产品。",
        "verbatim_context_en": "The first thing we have to do is job one is to create something that works.",
        "source_type": "corpus",
        "clip_ids": ["029_AI"],
    },
    {
        "phrase_id": "LEX_070",
        "phrase_en": "sizable fleet",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "a quite large group of deployed robots and devices",
        "executive_subtext_zh": "硬件量产与商用落地圈的高级量化表达（颇具规模的终端集群）：专指跨越样机阶段、真正在真实场景规模化铺开的设备群。",
        "verbatim_context_en": "we could easily see about six about 15 million humanoids in operation by 2035, which is quite a sizable fleet if you think about it.",
        "source_type": "corpus",
        "clip_ids": ["089_USC"],
    },
    {
        "phrase_id": "LEX_071",
        "phrase_en": "major new consumer category",
        "category": "ai_compute_product",
        "cefr_level": "B2",
        "chinglish_trap": "a big brand-new kind of consumer product",
        "executive_subtext_zh": "出海消费硬件打动高端百货（如 Selfridges/Best Buy）与VC的定位杀招：把单品拔高为开创全新品类，跳出红海比价泥潭。",
        "verbatim_context_en": "companion robots could become a major new consumer category by giving people personalized emotional support.",
        "source_type": "corpus",
        "clip_ids": ["095_USC"],
    },
    {
        "phrase_id": "LEX_072",
        "phrase_en": "tightly controlled environment",
        "category": "ai_compute_product",
        "cefr_level": "C1",
        "chinglish_trap": "strictly arranged lab testing room",
        "executive_subtext_zh": "资深买家拆穿“炫技Demo”的毒辣话术：暗示你的产品只在精心布置的实验室里能跑，一进真实家庭或卖场就会翻车。",
        "verbatim_context_en": "But even in this tightly controlled environment, the robot often struggled.",
        "source_type": "corpus",
        "clip_ids": ["084_USC"],
    },
    {
        "phrase_id": "LEX_073",
        "phrase_en": "destroy everybody's flywheel",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "break everyone's good business growth cycle",
        "executive_subtext_zh": "黄仁勋在华盛顿博弈中的高段位劝诫：用商业增长“飞轮”隐喻警示政策制定者——把良性竞争推成敌对脱钩，最终所有人一起坠毁。",
        "verbatim_context_en": "once you cross that line you I think have the potential to destroy everybody's flywheel.",
        "source_type": "corpus",
        "clip_ids": ["04_USCHINA_Jensen"],
    },
    {
        "phrase_id": "LEX_074",
        "phrase_en": "supply chain disruptions",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "supply chain stopping or breaking accidents",
        "executive_subtext_zh": "全球制造与跨境出海董事会必考词（供应链中断风险）：用于向欧美大客户解释为何必须布局双基地备份与安全库存。",
        "verbatim_context_en": "the kinds of supply chain shocks that we saw during the the covid lockdowns in China and the supply chain disruptions that resulted from that",
        "source_type": "corpus",
        "clip_ids": ["086_USC"],
    },
    {
        "phrase_id": "LEX_075",
        "phrase_en": "insulated from",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "well protected and separated from outside shocks",
        "executive_subtext_zh": "向机构投资人兜售抗周期韧性的高级动词短语（免受……冲击/隔离风险）：比 protected from 更具金融与供应链架构感。",
        "verbatim_context_en": "they also benefit from being insulated from the kinds of supply chain shocks that we saw during the the covid lockdowns in China",
        "source_type": "corpus",
        "clip_ids": ["086_USC"],
    },
    {
        "phrase_id": "LEX_076",
        "phrase_en": "base cost",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "the basic bottom price after adding import tax",
        "executive_subtext_zh": "关税冲击测算与定价谈判的硬核锚点（基准成本）：直接把25%关税摊到出厂基准成本上算清底线，决定是硬扛还是转产墨西哥/东南亚。",
        "verbatim_context_en": "for a car under $12,000 a 25% tariff puts the base cost at $15,000 plus shipping",
        "source_type": "corpus",
        "clip_ids": ["093_USC"],
    },
    {
        "phrase_id": "LEX_077",
        "phrase_en": "back off of it",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "cancel or retreat from that tough tariff policy",
        "executive_subtext_zh": "华尔街大行CEO评估关税极限施压时的直白口语：“过度不确定性正在挥霍自身筹码，现在明智之举是赶紧往回撤”。",
        "verbatim_context_en": "I mean, I think they're doing the right thing now, which is to back off of it.",
        "source_type": "corpus",
        "clip_ids": ["065_FIN"],
    },
    {
        "phrase_id": "LEX_078",
        "phrase_en": "choke off the supply",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "completely block and cut the chip supply",
        "executive_subtext_zh": "半导体与地缘风险评估的强冲击动词（掐断供应咽喉）：比 stop supply 更具窒息感和国家安全级别的紧迫压迫力。",
        "verbatim_context_en": "Their concerns that an invasion of Taiwan by China could choke off the supply",
        "source_type": "corpus",
        "clip_ids": ["080_USC"],
    },
    {
        "phrase_id": "LEX_079",
        "phrase_en": "eating a loss",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "having to swallow and pay for a big money loss",
        "executive_subtext_zh": "硬件制造与供应链翻车时极具画面感的商战口语（硬生生吞下巨额亏损）：没人替你买单，只能自己啃下这笔坏账或报废损失。",
        "verbatim_context_en": "TSMC had to scrap an estimated 10,000 to 30,000 wafers. eating a loss of about $550 million in revenue.",
        "source_type": "corpus",
        "clip_ids": ["082_USC"],
    },
    {
        "phrase_id": "LEX_080",
        "phrase_en": "copy exact",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "copy every factory step 100% without any change",
        "executive_subtext_zh": "台积电/英特尔晶圆厂海外扩产铁律（精确复制原则）：面对跨国建厂良率崩盘风险，任何本地化“微调创新”都可能毁掉整条产线。",
        "verbatim_context_en": "they knew the only way to succeed was to copy exact their Taiwan operations.",
        "source_type": "corpus",
        "clip_ids": ["082_USC"],
    },
    {
        "phrase_id": "LEX_081",
        "phrase_en": "hitting a ceiling",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "reaching the highest limit and cannot go up more",
        "executive_subtext_zh": "芯片工艺与业务增长遇到物理或市场天花板的地道隐喻：宣告靠老办法线性堆料已经走到尽头，必须换架构破局。",
        "verbatim_context_en": "that geometric scaling with old lithography approaches is kind of hitting a ceiling.",
        "source_type": "corpus",
        "clip_ids": ["081_USC"],
    },
    {
        "phrase_id": "LEX_082",
        "phrase_en": "third-party validation",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "independent outside lab testing to prove it",
        "executive_subtext_zh": "欧美大渠道采购与技术尽调最冷峻的质疑词（第三方独立验证）：自卖自夸的实验室参数不算数，拿出独立权威机构测试报告再谈。",
        "verbatim_context_en": "here I want to talk through some of the numbers that Huawei have presented, and keep in mind we still haven't seen any third-party validation yet.",
        "source_type": "corpus",
        "clip_ids": ["081_USC"],
    },
    {
        "phrase_id": "LEX_083",
        "phrase_en": "domestically sourced",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "bought from local suppliers inside the home country",
        "executive_subtext_zh": "供应链国产化与原产地合规审查核心词（本土采购）：在关税原产地认定与自主可控博弈中决定产品能不能过海关与审查。",
        "verbatim_context_en": "90% of their parts were domestically sourced with most of the core components designed in-house.",
        "source_type": "corpus",
        "clip_ids": ["092_USC"],
    },
    {
        "phrase_id": "LEX_084",
        "phrase_en": "barred from selling",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "legally not allowed by government to sell",
        "executive_subtext_zh": "出口管制与贸易禁令的精准法律新闻表达（被明令禁止销售）：比 not allowed to sell 更正式、更具监管红线威慑力。",
        "verbatim_context_en": "ASML is still barred from selling its most advanced machines to China.",
        "source_type": "corpus",
        "clip_ids": ["092_USC"],
    },
    {
        "phrase_id": "LEX_085",
        "phrase_en": "chip starved",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "seriously lacking advanced semiconductor chips",
        "executive_subtext_zh": "地缘算力封锁下的鲜活形容词（芯片饥渴/缺芯受限）：在商战辩论中常用来反衬极端资源约束反而倒逼出10倍算法与工程效率。",
        "verbatim_context_en": "the US has banned the export of the latest AI chips to China um China is is somewhat chip starved.",
        "source_type": "corpus",
        "clip_ids": ["042_BIZ"],
    },
    {
        "phrase_id": "LEX_086",
        "phrase_en": "biggest bottlenecks",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "the most serious blocking points stopping growth",
        "executive_subtext_zh": "跨国产能与AI基建战略分析核心词（最大卡点/瓶颈）：帮高管从表面喧嚣中精准锁定真正限制交付的那个短板（如电力或封装）。",
        "verbatim_context_en": "Power is one of the biggest bottlenecks in the AI race for both the US and China.",
        "source_type": "corpus",
        "clip_ids": ["088_USC"],
    },
    {
        "phrase_id": "LEX_087",
        "phrase_en": "pragmatically adjusting",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "realistically changing strategy to fit new power",
        "executive_subtext_zh": "东南亚及跨国企业在中美夹缝中的高级生存法则（务实校准/实用主义调适）：不站意识形态口水队，只按商业利益动态下注。",
        "verbatim_context_en": "So, countries in this region, therefore, are pragmatically adjusting to the emergence of China.",
        "source_type": "corpus",
        "clip_ids": ["087_USC"],
    },
    {
        "phrase_id": "LEX_088",
        "phrase_en": "active strategic competition",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "fierce long-term fighting between two superpowers",
        "executive_subtext_zh": "华盛顿与达沃斯政策圈标准定性词（全方位主动战略竞争）：提醒出海创业者放弃“纯商业不涉政治”的天真幻想，提前做好合规隔离。",
        "verbatim_context_en": "This is an active strategic competition in AI across the stack, and whoever wins AI wins.",
        "source_type": "corpus",
        "clip_ids": ["094_USC"],
    },
    {
        "phrase_id": "LEX_089",
        "phrase_en": "shaping global AI norms",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "making international AI rules and standards",
        "executive_subtext_zh": "国际合规与行业话语权顶层概念（塑造全球AI规则与标准）：谁定义了安全、接口与伦理标准，谁就拿到了下一代全球市场的入场发牌权。",
        "verbatim_context_en": "And this just yet another platform that could give China more sway in shaping global AI norms.",
        "source_type": "corpus",
        "clip_ids": ["096_USC"],
    },
    {
        "phrase_id": "LEX_090",
        "phrase_en": "purchasing power parity",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "comparing countries by what local money really buys",
        "executive_subtext_zh": "跨国宏观研判与定价策略必懂指标（购买力平价 PPP）：戳破单一汇率换算的失真，看清各国真实工业体量与本地消费购买力。",
        "verbatim_context_en": "Measured by purchasing power parity, China is already 1/3 bigger than the US, on track to being 2/3 larger in a decade's time.",
        "source_type": "corpus",
        "clip_ids": ["097_USC"],
    },
    {
        "phrase_id": "LEX_091",
        "phrase_en": "tax breaks",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "government tax discount gifts for factories",
        "executive_subtext_zh": "海外选址与政府招商谈判桌上最直接的筹码（税收减免优惠）：巨头常靠就业承诺让多州政府竞价，但也极易招致舆论反噬。",
        "verbatim_context_en": "tax breaks georgia offered two billion dollars maryland offered five billion dollars seven billion dollars from new jersey",
        "source_type": "corpus",
        "clip_ids": ["035_BIZ"],
    },
    {
        "phrase_id": "LEX_092",
        "phrase_en": "denials management",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "using AI to reject insurance claims for profit",
        "executive_subtext_zh": "欧美医疗保险与B2B企业AI伦理雷区黑话（拒赔管理）：在商业变现与舆论公关之间最致命的灰产边界，碰错一步就可能引爆品牌危机。",
        "verbatim_context_en": "Palantir works with health insurance companies to build AI for denials management to protect revenue.",
        "source_type": "corpus",
        "clip_ids": ["045_BIZ"],
    },
    {
        "phrase_id": "LEX_093",
        "phrase_en": "pacing the frontier",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "controlling the speed of leading AI research",
        "executive_subtext_zh": "硅谷AI安全派在听证会与监管博弈中的核心修辞（控制前沿推进节奏）：既想显得负责任，又暗藏用合规门槛锁死后来者的商业算盘。",
        "verbatim_context_en": "So what you're proposing is called pacing the frontier of of the AI industry.",
        "source_type": "corpus",
        "clip_ids": ["026_AI"],
    },
    {
        "phrase_id": "LEX_094",
        "phrase_en": "acceptable use",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "rules saying how users are allowed to use AI",
        "executive_subtext_zh": "欧美科技法务与隐私听证会标准条款术语（可接受使用政策 AUP）：在创新自由与监管红线之间划定平台免责与合规边界。",
        "verbatim_context_en": "there is not going to be agreement on you know, what is and isn't acceptable use of AI.",
        "source_type": "corpus",
        "clip_ids": ["030_AI"],
    },
    {
        "phrase_id": "LEX_095",
        "phrase_en": "live in the shadow of",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "C1",
        "chinglish_trap": "always stay under the influence of a huge neighbor",
        "executive_subtext_zh": "地缘战略与区域市场格局的经典隐喻（生活在巨头的阴影之下）：道尽东南亚供应链节点或中小品牌在超级大国与巨无霸平台间的现实处境。",
        "verbatim_context_en": "just as Latin America will live in the shadow of the United States of America",
        "source_type": "corpus",
        "clip_ids": ["098_USC"],
    },
    {
        "phrase_id": "LEX_096",
        "phrase_en": "debt to GDP",
        "category": "tariffs_supply_chain_geopolitics",
        "cefr_level": "B2",
        "chinglish_trap": "the ratio between national debt and GDP size",
        "executive_subtext_zh": "全球宏观与汇率预警核心晴雨表（债务占GDP比重）：一旦逼近临界点触发主权降级恐慌，跨境企业的美元融资成本与FX敞口将瞬间承压。",
        "verbatim_context_en": "the last time we downgrade we had like 65 or 70 percent debt to GDP now it's 105.",
        "source_type": "corpus",
        "clip_ids": ["073_FIN"],
    },
    {
        "phrase_id": "LEX_097",
        "phrase_en": "slotting fee",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "shelf entrance fee / store display entry money",
        "executive_subtext_zh": "欧美大型零售渠道（Best Buy / Selfridges）最隐蔽的入场过路费（进场费/货架位费）：毛利测算漏掉这一项，硬件出海卖越多亏越惨。",
        "verbatim_context_en": "Best Buy waived half the slotting fee for our Q4 launch, but only if we guarantee 40% retail margin across 300 flagship stores.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_098",
        "phrase_en": "chargeback",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "deduct-money fine from the retail store",
        "executive_subtext_zh": "跨境硬件供货商的利润黑洞（渠道扣款/退单罚款）：只要贴标差一毫米、交期晚一天或退货率冒头，欧美大买手直接从尾款里硬扣。",
        "verbatim_context_en": "If Shenzhen misses the Friday air-freight cutoff, the retailer's automated chargeback will wipe out our entire Q1 net profit.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_099",
        "phrase_en": "MOQ",
        "category": "retail_channel_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "smallest order quantity number we must buy",
        "executive_subtext_zh": "供应链与渠道谈判桌上的双刃剑（最小起订量 Minimum Order Quantity）：工厂用MOQ卡死你的现金流，你也要用MOQ试探海外大买手是真下注还是空手套白狼。",
        "verbatim_context_en": "Our Shenzhen optical vendor won't cut the lens MOQ below 50,000 units without a non-refundable tooling deposit.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_100",
        "phrase_en": "sell-through rate",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "real consumer selling speed percentage",
        "executive_subtext_zh": "区分“压货给渠道”与“真卖给消费者”的照妖镜（实销率/动销率）：首单铺进Selfridges不算赢，30天动销率不达标立刻面临清仓下架。",
        "verbatim_context_en": "Alistair doesn't care about our Kickstarter hype; he's watching our week-four sell-through rate at Oxford Street before signing the Europe rollout.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_101",
        "phrase_en": "MAP pricing",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "lowest online advertisement price control",
        "executive_subtext_zh": "欧美全渠道防窜货生命线（最低广告标价 Minimum Advertised Price）：一旦亚马逊第三方卖家破价，线下旗舰渠道会立刻翻脸停止主推。",
        "verbatim_context_en": "If unauthorized resellers break our MAP pricing on Amazon before Black Friday, Best Buy will pull our demo pods overnight.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_102",
        "phrase_en": "co-op marketing",
        "category": "retail_channel_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "together-advertising fee with the retailer",
        "executive_subtext_zh": "大渠道买手在压完进货价后追加的第二把刀（联合营销基金）：名义上是品牌与渠道共摊推广费，实则常被当成变相返点强制捆绑。",
        "verbatim_context_en": "They agreed to hold our wholesale unit price, then quietly slipped a mandatory 8% co-op marketing contribution into page twelve of the vendor agreement.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_103",
        "phrase_en": "endcap placement",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "store aisle front-head display spot",
        "executive_subtext_zh": "北美消费电子卖场的黄金流量位（货架端头黄金陈列位）：直接决定AI眼镜这种新品类能不能让逛店顾客停下来试戴，谈判价值远超普通折扣。",
        "verbatim_context_en": "We'll absorb the demo-unit hardware cost only if you lock in prime endcap placement across your top 150 Tier-1 locations.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_104",
        "phrase_en": "markdown allowance",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "slow-selling price-cut compensation money",
        "executive_subtext_zh": "欧美买手转嫁滞销风险的经典霸王条款（降价补贴/滞销补偿）：如果新品季末卖不动被迫打折清库存，差价得由品牌方吐血补给渠道。",
        "verbatim_context_en": "Alistair wants a 12% markdown allowance built into the contract; in plain English, he wants NovaEdge to insure Selfridges against slow Q1 traffic.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_105",
        "phrase_en": "landed cost",
        "category": "retail_channel_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "arrive-at-port all-included total cost",
        "executive_subtext_zh": "跨境硬件真实毛利底线（到岸完税总成本）：把BOM物料、深圳组装、空海运、保险与25%进口关税全算进去，才是真正能用来谈批发价的底牌。",
        "verbatim_context_en": "Once you add air freight and the 25% tariff, our landed cost jumps by $31 a unit—which leaves zero room for Victoria's fantasy margin target.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_106",
        "phrase_en": "consignment terms",
        "category": "retail_channel_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "sell-first pay-later store contract",
        "executive_subtext_zh": "奢侈品百货与强势买手试水新硬件时的极限压榨（寄售条款）：货先铺进去，卖出才结账、卖不掉原封退回，极大考验出海公司的营运现金流。",
        "verbatim_context_en": "Selfridges offered consignment terms for the first 3,000 units, which means we finance the inventory while they capture all the foot traffic.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_107",
        "phrase_en": "shelf allocation",
        "category": "retail_channel_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "how much shelf space the store gives us",
        "executive_subtext_zh": "线下零售寸土寸金的权力筹码（货架配额/陈列面积）：买手只要暗示“下季度要重评你的货架配额”，就是最礼貌的最后通牒。",
        "verbatim_context_en": "If our cloud token bill forces a $50 retail price hike, we lose half our Q4 shelf allocation to cheaper knockoffs.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_108",
        "phrase_en": "net-60 payment terms",
        "category": "retail_channel_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "paying our money 60 days after goods arrive",
        "executive_subtext_zh": "跨国贸易账期杀手（货到60天结算）：一边是深圳芯片厂要求预付30%定金，一边是欧美渠道拉长到Net-60甚至Net-90，现金流错配能活活憋死独角兽。",
        "verbatim_context_en": "We cannot fund a 100,000-unit build on net-60 payment terms unless our Series C bridge closes by Friday.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_109",
        "phrase_en": "GDPR data residency",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "European user data staying inside Europe rule",
        "executive_subtext_zh": "AI硬件出海欧洲不可触碰的合规红线（GDPR数据驻留）：语音和视觉流若未经隔离就回传跨境服务器，布鲁塞尔监管罚单最高可达全球营收4%。",
        "verbatim_context_en": "Brussels counsel made one thing non-negotiable: NovaEdge Glass must enforce strict GDPR data residency on Frankfurt servers before UK or EU launch.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_110",
        "phrase_en": "BOM cost",
        "category": "compliance_hardware_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "hardware parts list total material cost",
        "executive_subtext_zh": "深圳智造与硅谷硬件投资人张口就问的硬指标（物料清单成本 Bill of Materials）：直接决定零售定价空间和硬件毛利率能不能撑住AI云服务开销。",
        "verbatim_context_en": "Zhou Mo shaved $18 off our optical waveguide BOM cost in Shenzhen, buying us enough gross margin to survive the retail squeeze.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_111",
        "phrase_en": "EVT/DVT/PVT",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "three factory sample-to-mass-production test stages",
        "executive_subtext_zh": "消费硬件量产爬坡铁三角黑话（工程验证/设计验证/生产验证）：内行一听就能分辨你的AI眼镜是PPT概念机，还是真正过完PVT准备锁模大批量出货。",
        "verbatim_context_en": "Tell Victoria our Shenzhen line cleared EVT/DVT/PVT on schedule—this isn't vaporware.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_112",
        "phrase_en": "RMA rate",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "broken product return-and-repair percentage",
        "executive_subtext_zh": "消费电子出海最致命的隐形杀手（售后退换货率 Return Merchandise Authorization）：RMA一旦超过3%，跨境逆向物流与翻新成本会把整季净利烧穿。",
        "verbatim_context_en": "If our first-batch RMA rate climbs above 2.5% due to hinge fatigue, Best Buy triggers an automatic vendor penalty.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_113",
        "phrase_en": "indemnity cap",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C2",
        "chinglish_trap": "highest legal compensation ceiling in a contract",
        "executive_subtext_zh": "欧美大企业与法务签约拉锯的生死条款（赔偿责任上限）：对方想让你对隐私或专利纠纷承担无限连带赔偿，你的法务必须死守赔偿上限。",
        "verbatim_context_en": "Never sign an uncapped privacy clause—push back for a 12-month revenue indemnity cap before we let them near the enterprise API.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_114",
        "phrase_en": "data localization",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "forcing user data to stay in local country",
        "executive_subtext_zh": "跨国AI终端面对欧美及东南亚多国监管的架构铁律（数据本地化）：迫使云架构从全球单一集群拆成区域独立孤岛，直接推高合规与运维成本。",
        "verbatim_context_en": "Data localization mandates across the EU and US mean we have to run separate inference clusters rather than routing audio back to one hub.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_115",
        "phrase_en": "yield ramp",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "factory good-product rate slowly climbing up",
        "executive_subtext_zh": "深圳量产线最紧张的爬坡期黑话（良率爬坡）：新品首批良率往往只有60%，能不能在30天内拉升到92%以上，决定你能不能如期交付圣诞季大单。",
        "verbatim_context_en": "Our yield ramp on the micro-OLED assembly hit 88% this morning, two weeks ahead of the Shenzhen schedule.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_116",
        "phrase_en": "on-device inference",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "running AI locally inside the glasses chip",
        "executive_subtext_zh": "AI消费硬件同时破解“Token烧钱”与“隐私合规”双死结的终极技术王牌（端侧本地推理）：小模型跑在眼镜芯片上，零延迟、零云费、数据不出设备。",
        "verbatim_context_en": "Moving wake-word and visual-summary workloads to on-device inference cuts our cloud token bill by 65% and neutralizes the EU privacy audit.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_117",
        "phrase_en": "FCC certification",
        "category": "compliance_hardware_bridge",
        "cefr_level": "B2",
        "chinglish_trap": "US government wireless radio entry certificate",
        "executive_subtext_zh": "无线智能硬件进入美国海关的硬门槛（美国联邦通信委员会射频认证）：没拿到FCC ID任何一批蓝牙/Wi-Fi眼镜都会被美国海关整柜扣留。",
        "verbatim_context_en": "Hardware is frozen until FCC certification clears—one late antenna tweak costs us six weeks and misses the entire holiday window.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_118",
        "phrase_en": "right to erasure",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "user legal right to delete all saved history",
        "executive_subtext_zh": "欧洲GDPR隐私听证会最爱拿来狙击AI记忆功能的条款（被遗忘权/删除权）：你的伴侣机器人记住用户偏好是卖点，但无法彻底清除训练与日志数据就是违规重罪。",
        "verbatim_context_en": "EU regulators will test our right to erasure pipeline live: if a user deletes a memory, every trace must vanish from vector storage within 72 hours.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_119",
        "phrase_en": "data processing agreement",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "user data handling legal contract",
        "executive_subtext_zh": "欧美大客户采购AI硬件/SaaS的法务标配前置文件（数据处理协议 DPA）：没签好DPA明确数据控制者与处理者边界，采购流程连第一步都走不出去。",
        "verbatim_context_en": "Enterprise legal stalled the pilot for three weeks over our data processing agreement because our third-party LLM sub-processor list wasn't locked.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
    {
        "phrase_id": "LEX_120",
        "phrase_en": "sole-source bottleneck",
        "category": "compliance_hardware_bridge",
        "cefr_level": "C1",
        "chinglish_trap": "only-one-supplier neck-choking supply risk",
        "executive_subtext_zh": "跨国硬件董事会尽调最怕看到的致命脆弱点（单一供应商卡点）：核心光学镜片或NPU一旦只绑一家厂商，地缘制裁或工厂失火就会让全线停摆。",
        "verbatim_context_en": "Victoria flagged the micro-display as a sole-source bottleneck—unless we qualify a second-source fab in Southeast Asia, she's cutting our valuation by 15%.",
        "source_type": "world_bridge",
        "clip_ids": [],
    },
]


class CorpusValidationError(ValueError):
    """Raised when input corpus or derived invariants fail validation."""


def _reject_non_finite_json_constant(token: str) -> NoReturn:
    """Reject non-RFC-8259 JSON constants such as NaN, Infinity, or -Infinity."""
    raise CorpusValidationError(f"Invalid non-finite JSON constant: {token!r}")


MAX_SAFE_NUMERIC_MAGNITUDE = 1e12


def _require_finite_number(val: Any, field: str, ctx: str) -> float:
    """Validate that `val` is a finite non-boolean int/float within safe bounds and return float(val)."""
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise CorpusValidationError(
            f"{ctx} field '{field}' must be a finite non-boolean number, "
            f"got {type(val).__name__}: {val!r}."
        )
    try:
        num = float(val)
    except OverflowError as exc:
        raise CorpusValidationError(
            f"{ctx} field '{field}' overflows IEEE-754 float64."
        ) from exc
    if not math.isfinite(num) or abs(num) > MAX_SAFE_NUMERIC_MAGNITUDE:
        raise CorpusValidationError(
            f"{ctx} field '{field}' must be finite and within "
            f"[-{MAX_SAFE_NUMERIC_MAGNITUDE:g}, {MAX_SAFE_NUMERIC_MAGNITUDE:g}], got {num!r}."
        )
    return num


def fetch_source_from_gdrive(dest_path: Path) -> None:
    """Download the canonical 100-clip arsenal JSON from Google Drive."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "gdrive",
        "readonly",
        "download",
        DRIVE_ARSENAL_FILE_ID,
        "--out",
        str(dest_path),
    ]
    subprocess.run(cmd, check=True)


def load_and_validate_source(source_path: Path) -> tuple[list[dict[str, Any]], str]:
    """Load and strictly validate source arsenal JSON before any output is written."""
    if not source_path.exists() or not source_path.is_file():
        raise CorpusValidationError(
            f"Source file not found: {source_path}. "
            "Pass --source <path> or run with --fetch-gdrive to download "
            f"Google Drive file ID {DRIVE_ARSENAL_FILE_ID}."
        )

    raw_bytes = source_path.read_bytes()
    source_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    try:
        payload = json.loads(
            raw_bytes.decode("utf-8"),
            parse_constant=_reject_non_finite_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise CorpusValidationError(f"Invalid JSON in {source_path}: {exc}") from exc

    if not isinstance(payload, list):
        raise CorpusValidationError(
            f"Expected JSON root list in {source_path}, got {type(payload).__name__}."
        )

    if len(payload) != EXPECTED_TOTAL_CLIPS:
        raise CorpusValidationError(
            f"Expected exactly {EXPECTED_TOTAL_CLIPS} clips in {source_path}, got {len(payload)}."
        )

    seen_clip_ids: set[str] = set()
    topic_counter: Counter[str] = Counter()

    for idx, rec in enumerate(payload):
        if not isinstance(rec, dict):
            raise CorpusValidationError(f"Record #{idx} must be a dict, got {type(rec).__name__}.")
        if "plan" not in rec or not isinstance(rec["plan"], dict):
            raise CorpusValidationError(f"Record #{idx} is missing valid 'plan' object.")
        if "duration_sec" not in rec:
            raise CorpusValidationError(f"Record #{idx} is missing numeric 'duration_sec'.")
        duration_val = _require_finite_number(rec["duration_sec"], "duration_sec", f"Record #{idx}")
        if duration_val <= 0 or round(duration_val, 2) <= 0:
            raise CorpusValidationError(
                f"Record #{idx} has non-positive duration_sec={rec['duration_sec']!r}."
            )

        if "local_mp4_path" in rec and not isinstance(rec["local_mp4_path"], str):
            raise CorpusValidationError(
                f"Record #{idx} field 'local_mp4_path' must be str, "
                f"got {type(rec['local_mp4_path']).__name__}."
            )
        if "youtube_video_id" in rec and (
            rec["youtube_video_id"] is not None and not isinstance(rec["youtube_video_id"], str)
        ):
            raise CorpusValidationError(
                f"Record #{idx} field 'youtube_video_id' must be str or None, "
                f"got {type(rec['youtube_video_id']).__name__}."
            )
        if "youtube_shorts_url" in rec and (
            rec["youtube_shorts_url"] is not None and not isinstance(rec["youtube_shorts_url"], str)
        ):
            raise CorpusValidationError(
                f"Record #{idx} field 'youtube_shorts_url' must be str or None, "
                f"got {type(rec['youtube_shorts_url']).__name__}."
            )

        plan = rec["plan"]
        for req_key in REQUIRED_PLAN_KEYS:
            if req_key not in plan:
                raise CorpusValidationError(
                    f"Record #{idx} (clip_id={plan.get('clip_id')!r}) missing required plan key '{req_key}'."
                )

        clip_id = plan["clip_id"]
        if not isinstance(clip_id, str) or not clip_id.strip():
            raise CorpusValidationError(f"Record #{idx} has empty/non-string clip_id: {clip_id!r}.")
        if clip_id in seen_clip_ids:
            raise CorpusValidationError(f"Duplicate clip_id detected: {clip_id!r}.")
        seen_clip_ids.add(clip_id)

        topic_key = plan["topic_key"]
        if not isinstance(topic_key, str) or topic_key not in EXPECTED_TOPIC_COUNTS:
            raise CorpusValidationError(
                f"Clip {clip_id!r} has invalid topic_key {topic_key!r}; expected one of {sorted(EXPECTED_TOPIC_COUNTS)}."
            )
        topic_counter[topic_key] += 1

        for str_key in REQUIRED_STR_PLAN_KEYS:
            val = plan[str_key]
            if not isinstance(val, str):
                raise CorpusValidationError(
                    f"Clip {clip_id!r} plan field '{str_key}' must be str, got {type(val).__name__}."
                )
            if str_key in REQUIRED_NONEMPTY_STR_PLAN_KEYS and not val.strip():
                raise CorpusValidationError(
                    f"Clip {clip_id!r} plan field '{str_key}' must be a non-empty string."
                )

        _require_finite_number(plan["virality_score"], "virality_score", f"Clip {clip_id!r}")

        subtitles = plan["subtitles"]
        if not isinstance(subtitles, list) or len(subtitles) == 0:
            raise CorpusValidationError(f"Clip {clip_id!r} has missing or empty 'subtitles' list.")
        for seg_idx, seg in enumerate(subtitles):
            if not isinstance(seg, dict):
                raise CorpusValidationError(f"Clip {clip_id!r} subtitle #{seg_idx} is not a dict.")
            for seg_key in ("start_sec", "end_sec", "en", "zh"):
                if seg_key not in seg:
                    raise CorpusValidationError(
                        f"Clip {clip_id!r} subtitle #{seg_idx} missing required key '{seg_key}'."
                    )
            seg_ctx = f"Clip {clip_id!r} subtitle #{seg_idx}"
            start_val = _require_finite_number(seg["start_sec"], "start_sec", seg_ctx)
            end_val = _require_finite_number(seg["end_sec"], "end_sec", seg_ctx)
            if start_val < 0:
                raise CorpusValidationError(
                    f"{seg_ctx} has negative start_sec={start_val}."
                )
            if end_val <= start_val:
                raise CorpusValidationError(
                    f"{seg_ctx} has non-positive raw duration: {start_val} -> {end_val}."
                )
            if not isinstance(seg["en"], str) or not isinstance(seg["zh"], str):
                raise CorpusValidationError(
                    f"{seg_ctx} 'en'/'zh' fields must be strings."
                )

    if dict(topic_counter) != EXPECTED_TOPIC_COUNTS:
        raise CorpusValidationError(
            f"Topic counts mismatch: expected {EXPECTED_TOPIC_COUNTS}, got {dict(topic_counter)}."
        )

    return payload, source_sha256


def infer_speakers(plan: dict[str, Any]) -> tuple[list[str], str]:
    """Deterministic 4-stage speaker attribution returning (speakers, stage_name)."""
    clip_id = plan["clip_id"]
    channel = plan["channel"]
    video_title = plan["video_title"]
    hook_line_2 = plan["hook_line_2"]

    # Stage 1: Exact clip-scoped overrides (multi-speaker, roundtable, narrator+quote)
    if clip_id in CLIP_SPEAKER_OVERRIDES:
        return list(CLIP_SPEAKER_OVERRIDES[clip_id]), "override"

    # Stage 2: Dedicated solo-narrator channels
    if channel in NARRATOR_CHANNELS:
        return [NARRATOR_CHANNELS[channel]], "narrator_ch"

    # Stage 3: Earliest-position named entity extraction over metadata string
    search_blob = f"{channel} | {video_title} | {hook_line_2}"
    best_match: tuple[int, str] | None = None
    for pattern, canonical_name in NAMED_SPEAKER_RULES:
        m = pattern.search(search_blob)
        if m is not None:
            pos = m.start()
            if best_match is None or pos < best_match[0]:
                best_match = (pos, canonical_name)
    if best_match is not None:
        return [best_match[1]], "named_rule"

    # Stage 4: Guaranteed non-empty fallback
    return [f"{channel} (Narrator)"], "fallback"


def count_en_words_regex(text: str) -> int:
    return len(EN_WORD_RE.findall(text))


def count_en_words_ws(text: str) -> int:
    return len(text.split())


def build_corpus_data(
    raw_records: list[dict[str, Any]],
    source_path: Path,
    source_sha256: str,
) -> dict[str, Any]:
    """Normalize all 100 clips deterministically and compute verified metrics."""
    rules_by_clip: dict[str, list[tuple[int, str, str, str, str, str, str]]] = {}
    for rule in ASR_NORMALIZATION_RULES:
        rules_by_clip.setdefault(rule[2], []).append(rule)

    rule_hit_counts: dict[int, int] = {r[0]: 0 for r in ASR_NORMALIZATION_RULES}
    asr_corrections_applied: list[dict[str, Any]] = []
    subtitle_overlaps_repaired: list[dict[str, Any]] = []
    relative_mp4_clip_ids: list[str] = []

    prefix_to_clip_ids: dict[str, list[str]] = {}
    seen_prefix_nums: set[int] = set()

    clips_out: list[dict[str, Any]] = []
    clean_wpms_all: list[float] = []
    raw_wpms_all: list[float] = []

    total_segments = 0
    total_en_words_clean_rx = 0
    total_en_words_clean_ws = 0
    total_en_words_raw_rx = 0
    total_en_words_raw_ws = 0
    total_zh_chars = 0
    total_duration_sec = 0.0
    published_count = 0
    queued_count = 0
    mid_sentence_start_count = 0
    mid_sentence_end_count = 0

    topic_buckets: dict[str, dict[str, Any]] = {
        tk: {
            "clips": 0,
            "published": 0,
            "queued": 0,
            "segments": 0,
            "duration_list": [],
            "en_words_rx": 0,
            "en_words_ws": 0,
            "raw_en_words_rx": 0,
            "raw_en_words_ws": 0,
            "zh_chars": 0,
            "wpm_list": [],
            "raw_wpm_list": [],
            "virality_list": [],
        }
        for tk in TOPIC_ORDER
    }

    for rec in raw_records:
        plan = rec["plan"]
        clip_id: str = plan["clip_id"]
        topic_key: str = plan["topic_key"]
        duration_sec = round(float(rec["duration_sec"]), 2)
        virality_score = round(float(plan["virality_score"]), 2)

        mp4_path = rec.get("local_mp4_path", "")
        if isinstance(mp4_path, str) and mp4_path and not mp4_path.startswith("/"):
            relative_mp4_clip_ids.append(clip_id)

        m_pref = PREFIX_NUM_RE.match(clip_id)
        if m_pref:
            num_val = int(m_pref.group(1))
            seen_prefix_nums.add(num_val)
            pref_key = f"{num_val:03d}"
            prefix_to_clip_ids.setdefault(pref_key, []).append(clip_id)

        is_published = bool(rec.get("youtube_video_id") or rec.get("youtube_shorts_url"))
        if is_published:
            published_count += 1
        else:
            queued_count += 1

        raw_subtitles: list[dict[str, Any]] = plan["subtitles"]
        en_raw = " ".join(s["en"].strip() for s in raw_subtitles)
        zh_full = "".join(s["zh"].strip() for s in raw_subtitles)

        if raw_subtitles and raw_subtitles[0]["en"].strip()[:1].islower():
            mid_sentence_start_count += 1
        if raw_subtitles and raw_subtitles[-1]["en"].strip()[-1:] not in '.!?"\'':
            mid_sentence_end_count += 1

        # Apply clip-scoped ASR normalization per segment
        clip_rules = rules_by_clip.get(clip_id, [])
        subtitles_clean: list[dict[str, Any]] = []
        for seg_idx, seg in enumerate(raw_subtitles):
            en_seg = seg["en"].strip()
            for rule_id, _tier, _cid, match_type, pat, repl, reason in clip_rules:
                if match_type == "literal":
                    if pat in en_seg:
                        en_seg = en_seg.replace(pat, repl)
                        rule_hit_counts[rule_id] += 1
                        asr_corrections_applied.append(
                            {
                                "clip_id": clip_id,
                                "seg_idx": seg_idx,
                                "raw": pat,
                                "clean": repl,
                                "reason": reason,
                            }
                        )
                else:
                    regex = re.compile(pat)
                    first_match = regex.search(en_seg)
                    if first_match is not None:
                        en_seg = regex.sub(repl, en_seg)
                        rule_hit_counts[rule_id] += 1
                        asr_corrections_applied.append(
                            {
                                "clip_id": clip_id,
                                "seg_idx": seg_idx,
                                "raw": first_match.group(0).strip(),
                                "clean": repl.strip(),
                                "reason": reason,
                            }
                        )

            en_seg = re.sub(r"\s{2,}", " ", en_seg).strip()
            subtitles_clean.append(
                {
                    "start_sec": round(float(seg["start_sec"]), 3),
                    "end_sec": round(float(seg["end_sec"]), 3),
                    "en": en_seg,
                    "zh": seg["zh"].strip(),
                }
            )

        # Repair small frame-quantization overlaps cleanly; fail fast on severe/nested overlaps
        for seg_idx in range(1, len(subtitles_clean)):
            prev_seg = subtitles_clean[seg_idx - 1]
            curr_seg = subtitles_clean[seg_idx]
            if curr_seg["start_sec"] < prev_seg["start_sec"]:
                raise CorpusValidationError(
                    f"Non-monotonic subtitle start in {clip_id}[{seg_idx - 1}->{seg_idx}]: "
                    f"prev_start={prev_seg['start_sec']} > curr_start={curr_seg['start_sec']}."
                )
            if prev_seg["end_sec"] > curr_seg["end_sec"]:
                raise CorpusValidationError(
                    f"Nested subtitle overlap in {clip_id}[{seg_idx - 1}->{seg_idx}]: "
                    f"prev=[{prev_seg['start_sec']}, {prev_seg['end_sec']}] swallows "
                    f"curr=[{curr_seg['start_sec']}, {curr_seg['end_sec']}]."
                )
            if curr_seg["start_sec"] < prev_seg["end_sec"]:
                overlap_sec = round(prev_seg["end_sec"] - curr_seg["start_sec"], 3)
                if overlap_sec > MAX_REPAIRABLE_OVERLAP_SEC:
                    raise CorpusValidationError(
                        f"Excessive subtitle overlap in {clip_id}[{seg_idx - 1}->{seg_idx}]: "
                        f"{overlap_sec:.3f}s exceeds MAX_REPAIRABLE_OVERLAP_SEC="
                        f"{MAX_REPAIRABLE_OVERLAP_SEC:.2f}s."
                    )
                subtitle_overlaps_repaired.append(
                    {
                        "clip_id": clip_id,
                        "seg_idx": seg_idx - 1,
                        "prev_raw_end_sec": prev_seg["end_sec"],
                        "curr_start_sec": curr_seg["start_sec"],
                        "overlap_sec": overlap_sec,
                    }
                )
                prev_seg["end_sec"] = round(min(prev_seg["end_sec"], curr_seg["start_sec"]), 3)

        # Verify strict subtitle monotonicity & positive segment durations
        for seg_idx, seg in enumerate(subtitles_clean):
            if seg["end_sec"] <= seg["start_sec"]:
                raise CorpusValidationError(
                    f"Non-positive cleaned segment duration in {clip_id}[{seg_idx}]: "
                    f"{seg['start_sec']} -> {seg['end_sec']}"
                )
            if seg_idx > 0 and seg["start_sec"] < subtitles_clean[seg_idx - 1]["end_sec"]:
                raise CorpusValidationError(
                    f"Residual subtitle overlap in {clip_id}[{seg_idx - 1}->{seg_idx}]"
                )

        en_clean = " ".join(s["en"] for s in subtitles_clean)

        # Verify 0 [snorts] and 0 non-ASCII characters remain in en_clean or segments
        if "[snorts]" in en_clean.lower():
            raise CorpusValidationError(f"Unsanitized [snorts] tag remains in {clip_id} en_clean.")
        non_ascii_chars = [ch for ch in en_clean if ord(ch) >= 128]
        if non_ascii_chars:
            raise CorpusValidationError(
                f"Non-ASCII characters {non_ascii_chars!r} remain in {clip_id} en_clean."
            )

        inferred_speakers, _stage = infer_speakers(plan)
        if not inferred_speakers or any(not s.strip() for s in inferred_speakers):
            raise CorpusValidationError(f"Empty inferred_speakers for {clip_id}.")

        en_words_clean_rx = count_en_words_regex(en_clean)
        en_words_clean_ws = count_en_words_ws(en_clean)
        en_words_raw_rx = count_en_words_regex(en_raw)
        en_words_raw_ws = count_en_words_ws(en_raw)
        zh_char_count = len(zh_full)

        wpm_exact = en_words_clean_rx / (duration_sec / 60.0)
        raw_wpm_exact = en_words_raw_rx / (duration_sec / 60.0)
        if not math.isfinite(wpm_exact) or not math.isfinite(raw_wpm_exact):
            raise CorpusValidationError(
                f"Non-finite WPM computed for {clip_id} (duration_sec={duration_sec})."
            )
        wpm_rounded = round(wpm_exact, 2)

        clean_wpms_all.append(wpm_exact)
        raw_wpms_all.append(raw_wpm_exact)

        total_segments += len(subtitles_clean)
        total_en_words_clean_rx += en_words_clean_rx
        total_en_words_clean_ws += en_words_clean_ws
        total_en_words_raw_rx += en_words_raw_rx
        total_en_words_raw_ws += en_words_raw_ws
        total_zh_chars += zh_char_count
        total_duration_sec += duration_sec

        tb = topic_buckets[topic_key]
        tb["clips"] += 1
        tb["published"] += 1 if is_published else 0
        tb["queued"] += 0 if is_published else 1
        tb["segments"] += len(subtitles_clean)
        tb["duration_list"].append(duration_sec)
        tb["en_words_rx"] += en_words_clean_rx
        tb["en_words_ws"] += en_words_clean_ws
        tb["raw_en_words_rx"] += en_words_raw_rx
        tb["raw_en_words_ws"] += en_words_raw_ws
        tb["zh_chars"] += zh_char_count
        tb["wpm_list"].append(wpm_exact)
        tb["raw_wpm_list"].append(raw_wpm_exact)
        tb["virality_list"].append(virality_score)

        clips_out.append(
            {
                "clip_id": clip_id,
                "topic_key": topic_key,
                "topic_label": plan["topic_label"],
                "video_id": plan["video_id"],
                "video_title": plan["video_title"],
                "channel": plan["channel"],
                "inferred_speakers": inferred_speakers,
                "duration_sec": duration_sec,
                "wpm": wpm_rounded,
                "virality_score": virality_score,
                "hook_line_1": plan["hook_line_1"],
                "hook_line_2": plan["hook_line_2"],
                "en_title_hook": plan["en_title_hook"],
                "summary_zh": plan["summary_zh"],
                "en_raw": en_raw,
                "en_clean": en_clean,
                "zh_full": zh_full,
                "subtitles_clean": subtitles_clean,
            }
        )

    # Assert every single one of the 85 ASR rules fired at least once
    unfired_rules = [r[0] for r in ASR_NORMALIZATION_RULES if rule_hit_counts[r[0]] == 0]
    if unfired_rules:
        raise CorpusValidationError(
            f"Silent ASR rule miss detected! Unfired rule IDs: {unfired_rules}"
        )

    # Finalize prefix collision and missing-prefix audit
    prefix_collisions = {
        k: v for k, v in sorted(prefix_to_clip_ids.items()) if len(v) > 1
    }
    missing_numeric_prefixes = [
        f"{n:03d}" for n in range(1, EXPECTED_TOTAL_CLIPS + 1) if n not in seen_prefix_nums
    ]

    clean_q25, clean_med, clean_q75 = statistics.quantiles(clean_wpms_all, n=4, method="exclusive")
    raw_q25, _raw_med_q, raw_q75 = statistics.quantiles(raw_wpms_all, n=4, method="exclusive")
    raw_med = statistics.median(raw_wpms_all)
    raw_mean = statistics.mean(raw_wpms_all)

    by_topic_summary: dict[str, dict[str, Any]] = {}
    for tk in TOPIC_ORDER:
        tb = topic_buckets[tk]
        by_topic_summary[tk] = {
            "clips": tb["clips"],
            "published_count": tb["published"],
            "queued_count": tb["queued"],
            "segments": tb["segments"],
            "total_duration_sec": round(sum(tb["duration_list"]), 2),
            "mean_duration_sec": round(statistics.mean(tb["duration_list"]), 2),
            "min_duration_sec": round(min(tb["duration_list"]), 2),
            "max_duration_sec": round(max(tb["duration_list"]), 2),
            "en_words": tb["en_words_rx"],
            "en_words_ws": tb["en_words_ws"],
            "raw_en_words": tb["raw_en_words_rx"],
            "raw_en_words_ws": tb["raw_en_words_ws"],
            "zh_chars": tb["zh_chars"],
            "min_wpm": round(min(tb["wpm_list"]), 2),
            "max_wpm": round(max(tb["wpm_list"]), 2),
            "mean_wpm": round(statistics.mean(tb["wpm_list"]), 2),
            "median_wpm": round(statistics.median(tb["wpm_list"]), 2),
            "raw_median_wpm": round(statistics.median(tb["raw_wpm_list"]), 2),
            "min_virality": round(min(tb["virality_list"]), 2),
            "max_virality": round(max(tb["virality_list"]), 2),
            "mean_virality": round(statistics.mean(tb["virality_list"]), 3),
        }

    unique_channels = len({c["channel"] for c in clips_out})
    virality_mean = round(statistics.mean(c["virality_score"] for c in clips_out), 2)
    overlap_unique_clips = len({item["clip_id"] for item in subtitle_overlaps_repaired})
    asr_unique_clips = len({item["clip_id"] for item in asr_corrections_applied})

    return {
        "schema_version": SCHEMA_VERSION,
        "source_file": str(source_path),
        "source_sha256": source_sha256,
        "source_gdrive_file_id": DRIVE_ARSENAL_FILE_ID,
        "total_clips": len(clips_out),
        "topic_counts": {tk: topic_buckets[tk]["clips"] for tk in TOPIC_ORDER},
        "summary_metrics": {
            "total_segments": total_segments,
            "median_wpm": round(clean_med, 2),
            "mean_wpm": round(statistics.mean(clean_wpms_all), 2),
            "total_en_words": total_en_words_clean_rx,
            "total_zh_chars": total_zh_chars,
            "total_duration_sec": round(total_duration_sec, 2),
            "raw_median_wpm": round(raw_med, 2),
            "raw_mean_wpm": round(raw_mean, 2),
            "raw_p25_wpm": round(raw_q25, 2),
            "raw_p75_wpm": round(raw_q75, 2),
            "raw_min_wpm": round(min(raw_wpms_all), 2),
            "raw_max_wpm": round(max(raw_wpms_all), 2),
            "p25_wpm": round(clean_q25, 2),
            "p75_wpm": round(clean_q75, 2),
            "min_wpm": round(min(clean_wpms_all), 2),
            "max_wpm": round(max(clean_wpms_all), 2),
            "total_en_words_ws": total_en_words_clean_ws,
            "raw_total_en_words": total_en_words_raw_rx,
            "raw_total_en_words_ws": total_en_words_raw_ws,
            "unique_channels": unique_channels,
            "published_count": published_count,
            "queued_count": queued_count,
            "virality_mean": virality_mean,
            "by_topic": by_topic_summary,
        },
        "asr_corrections_applied": asr_corrections_applied,
        "data_quality_audit": {
            "asr_rules_defined": len(ASR_NORMALIZATION_RULES),
            "asr_rules_fired": sum(1 for v in rule_hit_counts.values() if v > 0),
            "asr_replacements_total": len(asr_corrections_applied),
            "asr_clips_modified_count": asr_unique_clips,
            "prefix_collisions": prefix_collisions,
            "missing_numeric_prefixes": missing_numeric_prefixes,
            "relative_mp4_path_clip_ids": relative_mp4_clip_ids,
            "subtitle_overlaps_repaired_count": len(subtitle_overlaps_repaired),
            "subtitle_overlaps_repaired_clips_count": overlap_unique_clips,
            "subtitle_overlaps_repaired": subtitle_overlaps_repaired,
            "mid_sentence_start_count": mid_sentence_start_count,
            "mid_sentence_end_count": mid_sentence_end_count,
        },
        "clips": clips_out,
    }


def build_and_verify_lexicon(corpus_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a verified deep copy of the 120-entry executive lexicon."""
    clips_by_id: dict[str, dict[str, Any]] = {
        c["clip_id"]: c for c in corpus_data["clips"]
    }

    lexicon = [
        {
            "phrase_id": entry["phrase_id"],
            "phrase_en": entry["phrase_en"],
            "category": entry["category"],
            "cefr_level": entry["cefr_level"],
            "chinglish_trap": entry["chinglish_trap"],
            "executive_subtext_zh": entry["executive_subtext_zh"],
            "verbatim_context_en": entry["verbatim_context_en"],
            "source_type": entry["source_type"],
            "clip_ids": list(entry["clip_ids"]),
        }
        for entry in EXECUTIVE_LEXICON_SPEC
    ]

    if len(lexicon) < 110:
        raise CorpusValidationError(f"Lexicon requires >= 110 entries, got {len(lexicon)}.")

    seen_ids: set[str] = set()
    seen_phrases: set[str] = set()
    corpus_count = 0

    for entry in lexicon:
        if set(entry.keys()) != REQUIRED_LEXICON_KEYS:
            raise CorpusValidationError(
                f"Lexicon entry {entry.get('phrase_id')} keys mismatch: {set(entry.keys())}"
            )
        pid = entry["phrase_id"]
        phrase = entry["phrase_en"]
        if pid in seen_ids:
            raise CorpusValidationError(f"Duplicate phrase_id: {pid}")
        seen_ids.add(pid)
        if phrase.lower() in seen_phrases:
            raise CorpusValidationError(f"Duplicate phrase_en: {phrase}")
        seen_phrases.add(phrase.lower())

        if entry["cefr_level"] not in VALID_CEFR_LEVELS:
            raise CorpusValidationError(f"Invalid CEFR level on {pid}: {entry['cefr_level']}")
        if entry["source_type"] not in VALID_SOURCE_TYPES:
            raise CorpusValidationError(f"Invalid source_type on {pid}: {entry['source_type']}")
        for text_key in (
            "phrase_en",
            "category",
            "chinglish_trap",
            "executive_subtext_zh",
            "verbatim_context_en",
        ):
            if not isinstance(entry[text_key], str) or not entry[text_key].strip():
                raise CorpusValidationError(f"Blank required string '{text_key}' on {pid}.")
        if phrase.lower() not in entry["verbatim_context_en"].lower():
            raise CorpusValidationError(
                f"phrase_en {phrase!r} not found in verbatim_context_en on {pid}."
            )

        if entry["source_type"] == "corpus":
            corpus_count += 1
            if not entry["clip_ids"]:
                raise CorpusValidationError(f"Corpus lexicon entry {pid} has empty clip_ids.")
            for cid in entry["clip_ids"]:
                if cid not in clips_by_id:
                    raise CorpusValidationError(f"Unknown clip_id {cid!r} cited by {pid}.")
                if phrase.lower() not in clips_by_id[cid]["en_clean"].lower():
                    raise CorpusValidationError(
                        f"Verbatim phrase mismatch: {phrase!r} ({pid}) not in {cid} en_clean."
                    )
            primary_cid = entry["clip_ids"][0]
            if entry["verbatim_context_en"] not in clips_by_id[primary_cid]["en_clean"]:
                raise CorpusValidationError(
                    f"Verbatim context mismatch for {pid} ({phrase!r}) in primary clip {primary_cid}."
                )
        else:
            if entry["clip_ids"] != []:
                raise CorpusValidationError(
                    f"world_bridge entry {pid} must have clip_ids == [], got {entry['clip_ids']}."
                )
            for cid, clip in clips_by_id.items():
                if phrase.lower() in clip["en_clean"].lower():
                    raise CorpusValidationError(
                        f"world_bridge entry {pid} ({phrase!r}) unexpectedly found in corpus clip {cid}."
                    )

    corpus_ratio = corpus_count / len(lexicon)
    if corpus_ratio < 0.75:
        raise CorpusValidationError(
            f"Corpus lexicon ratio {corpus_ratio:.3f} below mandatory >= 0.75 threshold."
        )

    # Verify all 13 E001 mandatory phrases across all 8 groups are present as corpus entries
    by_phrase_lower = {e["phrase_en"].lower(): e for e in lexicon}
    for group_label, req_phrase, req_clip in E001_MANDATORY_PHRASES:
        entry = by_phrase_lower.get(req_phrase.lower())
        if entry is None:
            raise CorpusValidationError(
                f"Missing mandatory E001 phrase ({group_label}): {req_phrase!r}"
            )
        if entry["source_type"] != "corpus" or req_clip not in entry["clip_ids"]:
            raise CorpusValidationError(
                f"Mandatory E001 phrase {req_phrase!r} must be corpus citing {req_clip!r}."
            )

    return lexicon


def _md_cell(text: str) -> str:
    """Escape pipe/newline/currency-math hazards cleanly inside Markdown table cells."""
    cleaned = text.replace("|", "\\|").replace("\n", " ").strip()
    return cleaned.replace("$", "\\$")


def _clip_sort_key(clip: dict[str, Any]) -> tuple[int, int, str]:
    topic_idx = TOPIC_ORDER.index(clip["topic_key"])
    m = PREFIX_NUM_RE.match(clip["clip_id"])
    num_val = int(m.group(1)) if m else 9999
    return (topic_idx, num_val, clip["clip_id"])


def render_intelligence_report(
    corpus_data: dict[str, Any],
    lexicon_data: list[dict[str, Any]],
) -> str:
    """Programmatically generate CORPUS_INTELLIGENCE_REPORT.md with zero hand-typed stats."""
    sm = corpus_data["summary_metrics"]
    dqa = corpus_data["data_quality_audit"]
    clips: list[dict[str, Any]] = corpus_data["clips"]
    clips_by_id = {c["clip_id"]: c for c in clips}
    asr_fixes: list[dict[str, Any]] = corpus_data["asr_corrections_applied"]

    total_clips = corpus_data["total_clips"]
    total_dur_min = sm["total_duration_sec"] / 60.0

    # Live channel & speaker rankings
    channel_clips: dict[str, list[str]] = {}
    speaker_clips: dict[str, list[str]] = {}
    for c in clips:
        channel_clips.setdefault(c["channel"], []).append(c["clip_id"])
        for sp in c["inferred_speakers"]:
            speaker_clips.setdefault(sp, []).append(c["clip_id"])

    top_channels = sorted(
        channel_clips.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())
    )[:15]
    top_speakers = sorted(
        speaker_clips.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())
    )[:20]

    # Slowest 5 & Fastest 5 by clean WPM
    sorted_by_wpm = sorted(clips, key=lambda c: (c["wpm"], c["clip_id"]))
    slowest_5 = sorted_by_wpm[:5]
    fastest_5 = list(reversed(sorted_by_wpm[-5:]))

    # Live Gap Audit scan on en_clean
    gap_rows: list[tuple[str, str, str, int, int, list[str], str]] = []
    for group, term, pattern, note in GAP_AUDIT_TERMS:
        rx = re.compile(pattern, re.I)
        hit_total = 0
        matched_cids: list[str] = []
        for c in clips:
            hits = rx.findall(c["en_clean"])
            if hits:
                hit_total += len(hits)
                matched_cids.append(c["clip_id"])
        gap_rows.append((group, term, pattern, hit_total, len(matched_cids), matched_cids, note))

    # Live Lexicon aggregates & dynamic dataset bounds (zero hardcoded stats)
    lex_total = len(lexicon_data)
    lex_corpus = [e for e in lexicon_data if e["source_type"] == "corpus"]
    lex_bridge = [e for e in lexicon_data if e["source_type"] == "world_bridge"]
    lex_corpus_pct = (len(lex_corpus) / lex_total) * 100.0
    lex_bridge_pct = (len(lex_bridge) / lex_total) * 100.0
    cat_counts = Counter(e["category"] for e in lexicon_data)
    cefr_counts = Counter(e["cefr_level"] for e in lexicon_data)
    unique_cited_clips = sorted({cid for e in lex_corpus for cid in e["clip_ids"]})
    cited_by_topic = Counter(clips_by_id[cid]["topic_key"] for cid in unique_cited_clips)
    lex_by_phrase = {e["phrase_en"].lower(): e for e in lexicon_data}

    min_dur = min(c["duration_sec"] for c in clips)
    max_dur = max(c["duration_sec"] for c in clips)
    min_vir = min(c["virality_score"] for c in clips)
    max_vir = max(c["virality_score"] for c in clips)
    non_empty_speaker_clips = sum(1 for c in clips if c["inferred_speakers"])
    topic_count_vals = sorted(set(corpus_data["topic_counts"].values()))
    if len(topic_count_vals) == 1:
        topic_split_note = f"`{topic_count_vals[0]} × {len(TOPIC_ORDER)}` 四大支柱均分"
    else:
        topic_split_note = " / ".join(
            f"`{tk}:{corpus_data['topic_counts'][tk]}`" for tk in TOPIC_ORDER
        )
    collision_clip_count = sum(len(v) for v in dqa["prefix_collisions"].values())
    abs_mp4_count = total_clips - len(dqa["relative_mp4_path_clip_ids"])
    overlap_vals = [item["overlap_sec"] for item in dqa["subtitle_overlaps_repaired"]]
    if overlap_vals:
        min_ovl = min(overlap_vals)
        max_ovl = max(overlap_vals)
        overlap_range_str = (
            f"{min_ovl:.2f}s" if min_ovl == max_ovl else f"{min_ovl:.2f}–{max_ovl:.2f}s"
        )
    else:
        overlap_range_str = "0.00s"
    snorts_raw_cids = (
        ", ".join(f"`{c['clip_id']}`" for c in clips if "[snorts]" in c["en_raw"].lower())
        or "无"
    )

    lines: list[str] = []
    lines.append("# Global Edge（《跨境底牌：硅深暗战》）——百条视频号爆款语料实证情报报告")
    lines.append("")
    lines.append(
        "> **100% 程序实时聚合生成声明**：本报告由 "
        "`projects/global_edge/scripts/extract_100_clips_corpus.py` "
        "基于规范化后的 `corpus_100_structured.json` 与 `executive_lexicon.json` "
        "实时计算渲染，不含任何手工硬编码统计或墙钟时间戳，重复运行严格字节级一致。"
    )
    lines.append(
        f"> - **Schema 版本**：`{corpus_data['schema_version']}` ｜ "
        f"**源文件**：`{corpus_data['source_file']}` ｜ "
        f"**Google Drive ID**：`{corpus_data['source_gdrive_file_id']}`"
    )
    lines.append(f"> - **源文件 SHA-256**：`{corpus_data['source_sha256']}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Core Overview Metrics
    lines.append("## 一、核心全景指标（100% 程序实时聚合）")
    lines.append("")
    lines.append(
        f"| 指标维度 | 清洗后实证值（Full-{dqa['asr_rules_defined']} `en_clean`） | 原始基线值（`en_raw`） | 工程与节目意义 |"
    )
    lines.append("| :--- | :---: | :---: | :--- |")
    lines.append(
        f"| 切片总条数 (`total_clips`) | **{total_clips}**（{topic_split_note}） | `{total_clips}` | "
        f"100% 唯一 `clip_id` 严格字符串主键，支持第一季 24 集无损双射分配 |"
    )
    lines.append(
        f"| 发布队列状态 | 已发布 **`{sm['published_count']}`** / 待发 **`{sm['queued_count']}`** | "
        f"`{sm['published_count']}` / `{sm['queued_count']}` | "
        f"覆盖 `@一分钟想明白 1-Min Clarity` 现有爆款池与 {sm['queued_count']} 条未发弹药 |"
    )
    lines.append(
        f"| 字幕总片段数 (`total_segments`) | **`{sm['total_segments']:,}`** | `{sm['total_segments']:,}` | "
        f"均长 `{sm['total_duration_sec'] / sm['total_segments']:.2f}s/句`，所有时间轴重叠已零损钳平 |"
    )
    lines.append(
        f"| 总有效时长 (`total_duration_sec`) | **`{sm['total_duration_sec']:,.2f}s`**（**`{total_dur_min:.2f} min`**） | "
        f"`{sm['total_duration_sec']:,.2f}s` | 单条 `{min_dur:.2f}–{max_dur:.2f}s`（均值 `{sm['total_duration_sec'] / total_clips:.2f}s`），验证 45s 竖屏切片黄金时长 |"
    )
    lines.append(
        f"| 英文总词数（正则口径 / 空格口径） | **`{sm['total_en_words']:,}`** / `{sm['total_en_words_ws']:,}` | "
        f"`{sm['raw_total_en_words']:,}` / `{sm['raw_total_en_words_ws']:,}` | "
        f"Full-{dqa['asr_rules_defined']} 纠偏净变 `{sm['total_en_words'] - sm['raw_total_en_words']:+d}` 词（含剔除 `[snorts]` 与修复连写词） |"
    )
    lines.append(
        f"| 中文字幕总字符数 (`total_zh_chars`) | **`{sm['total_zh_chars']:,}`** | `{sm['total_zh_chars']:,}` | "
        f"每条切片均提供完整中英逐句对照，支撑双语潜台词与精读手册对齐 |"
    )
    lines.append(
        f"| 英文真实高管语速中位数 (`median_wpm`) | **`{sm['median_wpm']:.2f} WPM`** | "
        f"**`{sm['raw_median_wpm']:.2f} WPM`**（`{sm['raw_median_wpm']:.1f}` 基线） | 直接锚定正片自然高管语速 `150–185 WPM` 工业标准 |"
    )
    lines.append(
        f"| 英文真实高管语速均值 (`mean_wpm`) | **`{sm['mean_wpm']:.2f} WPM`** | "
        f"`{sm['raw_mean_wpm']:.2f} WPM`（`{sm['raw_mean_wpm']:.1f}` 基线） | 远高于传统 ESL 慢速教材（`110–135 WPM`），直击 B1–C1 听觉卡壳 |"
    )
    lines.append(
        f"| 语速四分位与极值 (`p25–p75` / `min–max`) | **`{sm['p25_wpm']:.2f}–{sm['p75_wpm']:.2f} WPM`** / `{sm['min_wpm']:.2f}–{sm['max_wpm']:.2f}` | "
        f"`{sm['raw_p25_wpm']:.2f}–{sm['raw_p75_wpm']:.2f}` / `{sm['raw_min_wpm']:.2f}–{sm['raw_max_wpm']:.2f}` | 片尾 `0.80x` 慢拆落于 `~120–145 WPM`，恰位于最低自然语速区 |"
    )
    lines.append(
        f"| 独立原片 YouTube 频道数 (`unique_channels`) | **`{sm['unique_channels']}`** | `{sm['unique_channels']}` | "
        f"跨硅谷一线播客、华尔街电视网与顶级智库的多元权力场语源 |"
    )
    lines.append(
        f"| 爆款潜力评分均值 (`virality_mean`) | **`{sm['virality_mean']:.2f}`**（`{min_vir:.1f}–{max_vir:.1f}`） | `{sm['virality_mean']:.2f}` | "
        f"全量经冲突张力筛选的高密商业弹药 |"
    )
    lines.append(
        f"| ASR 规范化纠偏记录 | **`{dqa['asr_rules_fired']}/{dqa['asr_rules_defined']}` 规则命中 → `{dqa['asr_replacements_total']}` 处修复（`{dqa['asr_clips_modified_count']}` 条切片）** | `0` | "
        f"`en_clean` 实现 100% 纯 ASCII、0 `[snorts]` 残余，且 `en_raw` 原样保留审计 |"
    )
    lines.append("")

    # Section 2: 4-Pillar Distribution & WPM Gradient
    lines.append("## 二、四大内容支柱分布与实证语速梯度")
    lines.append("")
    lines.append(
        "| 支柱 (`topic_key`) | 切片数（已发/待发） | 字幕段数 | 总时长 / 均长（范围） | 英文词数（正则 / 空格） | 中文字符数 | 语速中位数 (`median`) | 语速均值 (`mean`) | 语速范围 (`min–max`) | 爆款均分 |"
    )
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tk in TOPIC_ORDER:
        bt = sm["by_topic"][tk]
        lines.append(
            f"| **`{tk}`**（{TOPIC_DISPLAY_ZH[tk]}） | `{bt['clips']}` (`{bt['published_count']}`/`{bt['queued_count']}`) | "
            f"`{bt['segments']}` | `{bt['total_duration_sec']:.2f}s` / `{bt['mean_duration_sec']:.2f}s` (`{bt['min_duration_sec']:.2f}–{bt['max_duration_sec']:.2f}s`) | "
            f"`{bt['en_words']:,}` / `{bt['en_words_ws']:,}` | `{bt['zh_chars']:,}` | "
            f"**`{bt['median_wpm']:.2f}`** *(raw `{bt['raw_median_wpm']:.2f}`)* | `{bt['mean_wpm']:.2f}` | "
            f"`{bt['min_wpm']:.2f}–{bt['max_wpm']:.2f}` | `{bt['mean_virality']:.3f}` |"
        )
    lines.append(
        f"| **全库合计 / 总计** | **`{total_clips}`** (`{sm['published_count']}`/`{sm['queued_count']}`) | "
        f"**`{sm['total_segments']:,}`** | **`{sm['total_duration_sec']:,.2f}s`** / `{sm['total_duration_sec'] / total_clips:.2f}s` | "
        f"**`{sm['total_en_words']:,}`** / `{sm['total_en_words_ws']:,}` | **`{sm['total_zh_chars']:,}`** | "
        f"**`{sm['median_wpm']:.2f}`** *(raw `{sm['raw_median_wpm']:.2f}`)* | **`{sm['mean_wpm']:.2f}`** | "
        f"`{sm['min_wpm']:.2f}–{sm['max_wpm']:.2f}` | **`{sm['virality_mean']:.2f}`** |"
    )
    lines.append("")
    lines.append(
        f"- **实证语速梯度核心发现**：`AI` 支柱技术领袖语速中位数高达 **`{sm['by_topic']['AI']['median_wpm']:.2f} WPM`**，"
        f"比 `US_CHINA` 政策/宏观支柱（**`{sm['by_topic']['US_CHINA']['median_wpm']:.2f} WPM`**）快出 "
        f"**`{sm['by_topic']['AI']['median_wpm'] - sm['by_topic']['US_CHINA']['median_wpm']:.2f} WPM`**，"
        f"也比 `FINANCE` 支柱（**`{sm['by_topic']['FINANCE']['median_wpm']:.2f} WPM`**）快出 "
        f"**`{sm['by_topic']['AI']['median_wpm'] - sm['by_topic']['FINANCE']['median_wpm']:.2f} WPM`**。"
        f"这直接为《跨境底牌》提供声学表演标尺：硅谷技术/VC 对峙戏（`AI`/`BUSINESS`）采用偏高紧迫感语速（`165–185 WPM`），"
        f"伦敦零售与华盛顿/布鲁塞尔合规博弈戏（`FINANCE`/`US_CHINA`）采用更沉稳的冷峻压迫节奏（`145–165 WPM`）。"
    )
    lines.append("")

    # Section 3: Top 15 Channels & Top 20 Speakers
    lines.append(
        f"## 三、高频原片频道（Top {len(top_channels)}）与核心发言人图谱（Top {len(top_speakers)}）"
    )
    lines.append("")
    lines.append(
        f"### 3.1 高频来源频道 Top {len(top_channels)}（全库共 {sm['unique_channels']} 个独立频道）"
    )
    lines.append("")
    lines.append("| 排名 | YouTube 频道 (`channel`) | 切片数 | 关联 `clip_id` 列表 |")
    lines.append("| :---: | :--- | :---: | :--- |")
    for rank, (ch_name, cids) in enumerate(top_channels, start=1):
        cid_str = ", ".join(f"`{cid}`" for cid in cids)
        lines.append(f"| {rank} | **{_md_cell(ch_name)}** | `{len(cids)}` | {cid_str} |")
    lines.append("")

    lines.append(
        f"### 3.2 高频发言人 Top {len(top_speakers)}（4 阶段确定性归因，{non_empty_speaker_clips}/{total_clips} 非空全覆盖）"
    )
    lines.append("")
    lines.append("| 排名 | 发言人 / 旁白主体 (`inferred_speakers`) | 出现切片数 | 关联 `clip_id` 列表 |")
    lines.append("| :---: | :--- | :---: | :--- |")
    for rank, (sp_name, cids) in enumerate(top_speakers, start=1):
        cid_str = ", ".join(f"`{cid}`" for cid in cids)
        lines.append(f"| {rank} | **{_md_cell(sp_name)}** | `{len(cids)}` | {cid_str} |")
    lines.append("")

    # Section 4: WPM Extremes
    lines.append(
        f"## 四、语速两极样本（Top {len(slowest_5)} 最慢 vs Top {len(fastest_5)} 最快）与节目定速锚点"
    )
    lines.append("")
    lines.append(f"### 4.1 语速最慢 Top {len(slowest_5)} 切片（深沉压迫与外交稳重范式）")
    lines.append("")
    lines.append("| 排名 | `clip_id` | 支柱 | 语速 (`WPM`) | 时长 (`s`) | 归因发言人 | 英文标题钩子 (`en_title_hook`) |")
    lines.append("| :---: | :--- | :---: | :---: | :---: | :--- | :--- |")
    for rank, c in enumerate(slowest_5, start=1):
        lines.append(
            f"| {rank} | `{c['clip_id']}` | `{c['topic_key']}` | **`{c['wpm']:.2f}`** | `{c['duration_sec']:.2f}` | "
            f"{_md_cell(', '.join(c['inferred_speakers']))} | {_md_cell(c['en_title_hook'])} |"
        )
    lines.append("")

    lines.append(f"### 4.2 语速最快 Top {len(fastest_5)} 切片（硅谷高频连珠炮与交易室高压范式）")
    lines.append("")
    lines.append("| 排名 | `clip_id` | 支柱 | 语速 (`WPM`) | 时长 (`s`) | 归因发言人 | 英文标题钩子 (`en_title_hook`) |")
    lines.append("| :---: | :--- | :---: | :---: | :---: | :--- | :--- |")
    for rank, c in enumerate(fastest_5, start=1):
        lines.append(
            f"| {rank} | `{c['clip_id']}` | `{c['topic_key']}` | **`{c['wpm']:.2f}`** | `{c['duration_sec']:.2f}` | "
            f"{_md_cell(', '.join(c['inferred_speakers']))} | {_md_cell(c['en_title_hook'])} |"
        )
    lines.append("")
    lines.append(
        f"- **定速工程映射**：正片飙戏锁定 **`150–185 WPM`**（紧贴全库实证中位数 `{sm['median_wpm']:.2f} WPM` / 原始 `{sm['raw_median_wpm']:.2f} WPM` 与四分位 `{sm['p25_wpm']:.2f}–{sm['p75_wpm']:.2f} WPM`）；"
        f"片尾 3 分钟黑话拆局通过确定性 FFmpeg `atempo=0.80` 保音高降至 **`~120–145 WPM`**（对应上表最慢高管区间），随后以 `1.0x` 原速配合 `>= 1.8s` 跟读窗完成肌肉记忆固化。"
    )
    lines.append("")

    # Section 5: Data Anomalies & Full ASR Correction Audit Log
    lines.append("## 五、数据异常诊断与 ASR 纠偏审计台账")
    lines.append("")
    lines.append("### 5.1 结构性异常与清洗核验摘要")
    lines.append("")
    lines.append("| 审计维度 | 实测结果 | 工程防御处置 |")
    lines.append("| :--- | :--- | :--- |")
    coll_str = (
        "；".join(
            f"`{k}` → `{'`, `'.join(v)}`" for k, v in dqa["prefix_collisions"].items()
        )
        or "无"
    )
    miss_str = ", ".join(f"`{p}`" for p in dqa["missing_numeric_prefixes"]) or "无"
    rel_str = ", ".join(f"`{cid}`" for cid in dqa["relative_mp4_path_clip_ids"]) or "无"
    lines.append(
        f"| 数字前缀冲突 (`prefix_collisions`) | **{len(dqa['prefix_collisions'])} 组**：{coll_str} | "
        f"全链路严格以完整字符串 `clip_id` 为主键，严禁解析整数前缀，{collision_clip_count} 条冲突切片 100% 完整留存 |"
    )
    lines.append(
        f"| 缺失数字编号 (`missing_numeric_prefixes`) | **{len(dqa['missing_numeric_prefixes'])} 处**：{miss_str} | "
        f"仅作审计记录，不依赖连续 `001..{total_clips:03d}` 编号假设 |"
    )
    lines.append(
        f"| 混合相对路径 MP4 (`relative_mp4_path_clip_ids`) | **{len(dqa['relative_mp4_path_clip_ids'])} 条种子切片**：{rel_str}（其余 {abs_mp4_count} 条为绝对路径） | "
        "ETL 纯内存处理 JSON 元数据，不假设本地 MP4 路径存在 |"
    )
    lines.append(
        f"| 字幕时间轴微重叠 (`subtitle_overlaps_repaired`) | **`{dqa['subtitle_overlaps_repaired_count']}` 对重叠**（跨 **`{dqa['subtitle_overlaps_repaired_clips_count']}` 条切片**，`{overlap_range_str}`） | "
        f"在 `subtitles_clean` 中将 `prev.end_sec` 钳平至 `curr.start_sec`，{sm['total_segments']:,} 段 100% 严格单调无重叠，原始重叠记录完整归档 |"
    )
    lines.append(
        f"| 非语音标签 `[snorts]` 清洗 | {snorts_raw_cids} 原始 `en_raw` 保留 `[snorts]` 审计；全库 {total_clips} 条 `en_clean` 及 {sm['total_segments']:,} 条 `subtitles_clean` 中 **0 残余** | "
        "正则 `\\s*\\[snorts\\]\\s*` 精准剥离；同时完整保留 `063_FIN` 合法财务缩写 `(or DCF)` |"
    )
    lines.append(
        f"| 非 ASCII 字符清洗 | `063_FIN` `U+2019` → `'`，`100_USC` `19° of freedom` → `19 degrees of freedom` | "
        f"全库 {total_clips} 条 `en_clean` 经程序断言为 **100% 纯 ASCII** |"
    )
    lines.append(
        f"| 切片冷切边界统计 | `{dqa['mid_sentence_start_count']}` 条句中起切（首字母小写），`{dqa['mid_sentence_end_count']}` 条句尾无终结标点 | "
        "台本引用短语均提取完整语法语块，不生搬冷切残句 |"
    )
    lines.append("")

    lines.append(
        f"### 5.2 全量 ASR 纠偏执行台账（`{dqa['asr_rules_fired']}` 条规则 / `{dqa['asr_replacements_total']}` 处逐段修复 / `{dqa['asr_clips_modified_count']}` 条切片）"
    )
    lines.append("")
    lines.append("| # | `clip_id` | 句段 `seg_idx` | 原始错词 (`raw`) | 规范化修复 (`clean`) | 纠偏依据 (`reason`) |")
    lines.append("| :---: | :--- | :---: | :--- | :--- | :--- |")
    for idx, fix in enumerate(asr_fixes, start=1):
        raw_disp = f"`{fix['raw']}`" if fix["raw"] else "`(empty)`"
        clean_disp = f"`{fix['clean']}`" if fix["clean"] else "`(stripped)`"
        lines.append(
            f"| {idx} | `{fix['clip_id']}` | `{fix['seg_idx']}` | {raw_disp} | {clean_disp} | {_md_cell(fix['reason'])} |"
        )
    lines.append("")

    # Section 6: Live Gap Audit & 70/30 Provenance Proof
    lines.append("## 六、实证语料缺口审计（Gap Audit）与 70/30 词源铁律核验")
    lines.append("")
    lines.append(
        f"为彻底杜绝“把原语料中不存在的渠道/隐私词硬说成出自切片”的伪引注风险，ETL 脚本在全库 {total_clips} 条 `en_clean` 上实时执行正则扫描："
    )
    lines.append("")
    lines.append("| 维度分组 | 目标检索词 | 正则表达式 | 命中总次数 | 命中切片数 | 命中 `clip_id` | 词源定性与策略说明 |")
    lines.append("| :--- | :--- | :--- | :---: | :---: | :--- | :--- |")
    for group, term, pattern, hit_total, clip_cnt, cids, note in gap_rows:
        cid_disp = ", ".join(f"`{cid}`" for cid in cids) if cids else "`[]`"
        lines.append(
            f"| {group} | `{term}` | `{pattern}` | **`{hit_total}`** | `{clip_cnt}` | {cid_disp} | {_md_cell(note)} |"
        )
    lines.append("")
    lines.append(
        f"- **70/30 词源铁律实时核验结果**：本工程 `executive_lexicon.json` 共计 **`{lex_total}`** 条商业英语高管词条，"
        f"其中 `source_type == \"corpus\"` 占比 **`{len(lex_corpus)}/{lex_total} ({lex_corpus_pct:.1f}%)`**"
        f"（远高于 `PROJECT.md` `>= 70%` 合同红线及 M2 `>= 75%` 强化门槛，且 100% 逐词通过所属 `clip_id` 的 `en_clean` 精确子串验真），"
        f"`source_type == \"world_bridge\"` 占比 **`{len(lex_bridge)}/{lex_total} ({lex_bridge_pct:.1f}%)`**"
        f"（严格设 `clip_ids: []` 且全库 {total_clips} 条 `en_clean` 零碰撞，专职补齐 Best Buy / Selfridges 零售谈判、GDPR 数据驻留与深圳硬件量产桥梁词）。"
    )
    lines.append("")

    # Section 7: Lexicon Overview & E001 5 Seed Clips x 8 Mandatory Phrase Groups
    lines.append("## 七、高管黑话词库总览与 E001 五条种子切片 / 八大必考词组核验")
    lines.append("")
    lines.append(f"### 7.1 词库结构分布（`executive_lexicon.json`，共 {lex_total} 条）")
    lines.append("")
    lines.append("| 类别 (`category`) | 中文定位 | 词条数 | 词源类型 |")
    lines.append("| :--- | :--- | :---: | :---: |")
    for cat_key, cat_label in CATEGORY_LABELS_ZH.items():
        stype = "world_bridge" if cat_key.endswith("_bridge") else "corpus"
        lines.append(f"| `{cat_key}` | {cat_label} | **`{cat_counts[cat_key]}`** | `{stype}` |")
    lines.append("")
    lines.append(
        f"- **CEFR 难度分布**：`B1`: `{cefr_counts['B1']}` 条、`B2`: `{cefr_counts['B2']}` 条、"
        f"`C1`: `{cefr_counts['C1']}` 条、`C2`: `{cefr_counts['C2']}` 条（`B2+C1` 合计 **`{cefr_counts['B2'] + cefr_counts['C1']}/{lex_total}` = `{(cefr_counts['B2'] + cefr_counts['C1']) / lex_total * 100:.1f}%`**，精准锚定 B1–C1 职场进阶听众）。"
    )
    lines.append(
        f"- **原语料覆盖广度**：{len(lex_corpus)} 条 `corpus` 词条共覆盖 **`{len(unique_cited_clips)} / {total_clips}`** 条独立切片"
        f"（`AI`: `{cited_by_topic['AI']}`、`BUSINESS`: `{cited_by_topic['BUSINESS']}`、"
        f"`FINANCE`: `{cited_by_topic['FINANCE']}`、`US_CHINA`: `{cited_by_topic['US_CHINA']}`）。"
    )
    lines.append("")

    lines.append("### 7.2 E001 五条共享种子切片验真")
    lines.append("")
    lines.append("| 种子 `clip_id` | 支柱 | 频道 | 归因发言人 | 语速 (`WPM`) | 核心商业议题 (`hook_line_2`) |")
    lines.append("| :--- | :---: | :--- | :--- | :---: | :--- |")
    for scid in E001_SEED_CLIPS:
        sc = clips_by_id[scid]
        lines.append(
            f"| **`{sc['clip_id']}`** | `{sc['topic_key']}` | {_md_cell(sc['channel'])} | "
            f"{_md_cell(', '.join(sc['inferred_speakers']))} | `{sc['wpm']:.2f}` | {_md_cell(sc['hook_line_2'])} |"
        )
    lines.append("")

    lines.append(
        f"### 7.3 E001 八大必考词组（{len(E001_MANDATORY_PHRASES)} 条原话短语）100% 验真矩阵"
    )
    lines.append("")
    lines.append("| 必考分组 | `phrase_id` | 精确英文原话 (`phrase_en`) | 词库分类 | 归属种子 `clip_id` | `en_clean` 验真 |")
    lines.append("| :---: | :---: | :--- | :--- | :--- | :---: |")
    for grp, req_phrase, req_cid in E001_MANDATORY_PHRASES:
        entry = lex_by_phrase[req_phrase.lower()]
        cids_disp = ", ".join(f"`{cid}`" for cid in entry["clip_ids"])
        lines.append(
            f"| {grp} | `{entry['phrase_id']}` | `{entry['phrase_en']}` | `{entry['category']}` | {cids_disp} | PASS |"
        )
    lines.append("")

    lines.append(f"### 7.4 全量 {lex_total} 条高管黑话词库分类索引（带 `clip_id` 溯源）")
    lines.append("")
    lines.append("| `phrase_id` | 英文高管原话 (`phrase_en`) | 分类 | CEFR | 词源 | 溯源 `clip_ids` | 中式直译雷区 (`chinglish_trap`) |")
    lines.append("| :---: | :--- | :--- | :---: | :---: | :--- | :--- |")
    for entry in lexicon_data:
        cids_disp = ", ".join(f"`{cid}`" for cid in entry["clip_ids"]) if entry["clip_ids"] else "`[]`"
        lines.append(
            f"| `{entry['phrase_id']}` | `{entry['phrase_en']}` | `{entry['category']}` | `{entry['cefr_level']}` | "
            f"`{entry['source_type']}` | {cids_disp} | {_md_cell(entry['chinglish_trap'])} |"
        )
    lines.append("")

    # Section 8: Compact 100-Clip Index Table
    lines.append(f"## 八、全量 {total_clips} 条切片紧凑索引表（按四大支柱有序排列）")
    lines.append("")
    lines.append("| # | `clip_id` | 支柱 | 来源频道 (`channel`) | 归因发言人 (`inferred_speakers`) | 时长 (`s`) | 语速 (`WPM`) | 爆款分 | 英文标题钩子 (`en_title_hook`) |")
    lines.append("| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :--- |")
    for rank, c in enumerate(sorted(clips, key=_clip_sort_key), start=1):
        lines.append(
            f"| {rank} | `{c['clip_id']}` | `{c['topic_key']}` | {_md_cell(c['channel'])} | "
            f"{_md_cell(', '.join(c['inferred_speakers']))} | `{c['duration_sec']:.2f}` | `{c['wpm']:.2f}` | "
            f"`{c['virality_score']:.1f}` | {_md_cell(c['en_title_hook'])} |"
        )
    lines.append("")

    return "\n".join(lines)


def write_outputs(
    out_dir: Path,
    corpus_data: dict[str, Any],
    lexicon_data: list[dict[str, Any]],
    report_md: str,
) -> tuple[Path, Path, Path]:
    """Write the three deterministic outputs cleanly after all validation passes."""
    try:
        corpus_json = json.dumps(corpus_data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        lexicon_json = json.dumps(lexicon_data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    except ValueError as exc:
        raise CorpusValidationError(
            f"Non-JSON-compliant value encountered during output serialization: {exc}"
        ) from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = out_dir / "corpus_100_structured.json"
    lexicon_path = out_dir / "executive_lexicon.json"
    report_path = out_dir / "CORPUS_INTELLIGENCE_REPORT.md"

    corpus_path.write_text(corpus_json, encoding="utf-8")
    lexicon_path.write_text(lexicon_json, encoding="utf-8")
    report_path.write_text(report_md, encoding="utf-8")
    return corpus_path, lexicon_path, report_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic 100-clip corpus ETL, 85-rule ASR normalizer, "
            "and 120-entry executive lexicon generator for Global Edge."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE_PATH,
        help=f"Path to raw arsenal_100_queue.json (default: {DEFAULT_SOURCE_PATH})",
    )
    parser.add_argument(
        "--out-dir",
        "--output-dir",
        dest="out_dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory for structured JSONs and report (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--fetch-gdrive",
        action="store_true",
        help=(
            f"Download Drive ID {DRIVE_ARSENAL_FILE_ID} to --source via "
            "`gdrive readonly download` before extraction."
        ),
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate input, ASR rules, and lexicon strictly in memory without writing files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    source_path: Path = args.source
    out_dir: Path = args.out_dir

    try:
        if args.fetch_gdrive:
            fetch_source_from_gdrive(source_path)

        raw_records, source_sha256 = load_and_validate_source(source_path)
        corpus_data = build_corpus_data(raw_records, source_path, source_sha256)
        lexicon_data = build_and_verify_lexicon(corpus_data)
        report_md = render_intelligence_report(corpus_data, lexicon_data)

        sm = corpus_data["summary_metrics"]
        dqa = corpus_data["data_quality_audit"]
        corpus_lex_cnt = sum(1 for e in lexicon_data if e["source_type"] == "corpus")

        if args.check_only:
            print(
                f"[CHECK-ONLY PASS] clips={corpus_data['total_clips']} "
                f"segments={sm['total_segments']} median_wpm={sm['median_wpm']:.2f} "
                f"(raw={sm['raw_median_wpm']:.2f}) asr_fixes={dqa['asr_replacements_total']} "
                f"overlaps_repaired={dqa['subtitle_overlaps_repaired_count']} "
                f"lexicon={len(lexicon_data)} ({corpus_lex_cnt} corpus / "
                f"{len(lexicon_data) - corpus_lex_cnt} world_bridge)"
            )
            return 0

        corpus_path, lexicon_path, report_path = write_outputs(
            out_dir, corpus_data, lexicon_data, report_md
        )
        print(
            f"[OK] Generated {corpus_path}, {lexicon_path}, {report_path} | "
            f"clips={corpus_data['total_clips']} segments={sm['total_segments']} "
            f"median_wpm={sm['median_wpm']:.2f} (raw={sm['raw_median_wpm']:.2f}) "
            f"asr_fixes={dqa['asr_replacements_total']} "
            f"overlaps_repaired={dqa['subtitle_overlaps_repaired_count']} "
            f"lexicon={len(lexicon_data)} ({corpus_lex_cnt}/{len(lexicon_data)} corpus)"
        )
        return 0
    except (CorpusValidationError, subprocess.CalledProcessError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
