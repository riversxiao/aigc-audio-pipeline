"""Xianxia & Classical Chinese polyphone phonetic overrides for eleven_v3 TTS.

`TimelineCue.text` always preserves the 100% canonical literary Chinese text
(used for `.srt` subtitles, `.md` scripts, and dual-reference ASR QA).
Whenever a line contains classical/cultivation polyphones or rare characters that
`eleven_v3` (`language_code='zh'`) is known to misread, `apply_xianxia_polyphone_overrides`
returns a homophone-guided `tts_text` string with identical Pinyin and tone.
"""

from __future__ import annotations

import re

# Ordered longest-first where phrases overlap. Every replacement strictly preserves
# exact Mainland Mandarin Pinyin + tone while eliminating polyphone ambiguity.
XIANXIA_POLYPHONE_MAP: tuple[tuple[str, str], ...] = (
    # Cultivation realms & layers (chóng vs zhòng)
    ("引气一重", "引气一崇"),
    ("引气二重", "引气二崇"),
    ("引气三重", "引气三崇"),
    ("引气四重", "引气四崇"),
    ("引气五重", "引气五崇"),
    ("引气六重", "引气六崇"),
    ("引气七重", "引气七崇"),
    ("引气八重", "引气八崇"),
    ("引气九重", "引气九崇"),
    ("八重与九重", "八崇与九崇"),
    ("九重圆满", "九崇圆满"),
    ("九重灰雾", "九崇灰雾"),
    ("重重关隘", "崇崇关隘"),
    ("第一重", "第一崇"),
    ("第二重", "第二崇"),
    ("第三重", "第三崇"),
    ("第四重", "第四崇"),
    ("第五重", "第五崇"),
    ("第六重", "第六崇"),
    ("第七重", "第七崇"),
    ("第八重", "第八崇"),
    ("第九重", "第九崇"),
    ("三重天", "三崇天"),
    ("九重天", "九崇天"),
    # jiàng vs xiáng disambiguation
    ("降生", "酱生"),
    ("降临", "酱临"),
    ("天降", "天酱"),
    ("骤降", "骤酱"),
    ("沉降", "沉酱"),
    # Cultivation titles & lineage (chuán vs zhuàn)
    ("真传", "真船"),
    ("亲传", "亲船"),
    ("单传", "单船"),
    ("嫡传", "嫡船"),
    # Classical courtesy, idioms & actions
    ("忝为", "舔为"),
    ("敛衽", "敛刃"),
    ("礼数", "礼树"),
    ("拾级而上", "涉级而上"),
    ("拾级", "涉级"),
    ("调虎离山", "掉虎离山"),
    ("此獠", "此疗"),
    ("佝偻", "沟楼"),
    # Weapons, combat, terrain & anatomy
    ("刀锷", "刀鄂"),
    ("剑锷", "剑鄂"),
    ("劈开", "批开"),
    ("劈裂", "批裂"),
    ("劈碎", "批碎"),
    ("劈死", "批死"),
    ("劈砍", "批砍"),
    ("血泊", "血坡"),
    ("躯壳", "躯咳"),
    ("龟裂", "均裂"),
    # Herbalism, alchemy & cultivation terms
    ("白芨", "白及"),
    ("参须", "深须"),
    ("参汤", "深汤"),
    ("老山参", "老山深"),
    ("血参", "血深"),
    ("龟息", "归息"),
    ("辟谷", "必谷"),
    ("拓印", "踏印"),
    ("道行", "道衡"),
    ("炮制", "袍制"),
    # Carrying on the back (bēi vs bèi)
    ("背回", "杯回"),
    ("背起麻布", "杯起麻布"),
    ("背着大黑刀", "杯着大黑刀"),
    ("背着六十四斤", "杯着六十四斤"),
    # Classical calendar, night watches & rare Xianxia characters
    ("熬过三更", "熬过三羹"),
    ("昨夜三更", "昨夜三羹"),
    ("入夜三更", "入夜三羹"),
    ("三更时分", "三羹时分"),
    ("三更夜色", "三羹夜色"),
    ("三更梆子", "三羹梆子"),
    ("三更去", "三羹去"),
    ("五更梆子", "五羹梆子"),
    ("五更前", "五羹前"),
    ("九月廿三", "九月念三"),
    ("廿三", "念三"),
    ("九月卅日", "九月萨日"),
    ("卅日", "萨日"),
    ("胡吣", "胡沁"),
    ("虫豸", "虫至"),
    ("尸蟞虫", "尸憋虫"),
    ("尸蟞", "尸憋"),
    # Classical banker's numerals used in blood-sacrifice ledgers & pasture IDs
    ("第柒拾叁号", "第七十三号"),
    ("壹号", "一号"),
    ("贰号", "二号"),
    ("叁号", "三号"),
    ("肆号", "四号"),
    ("伍号", "五号"),
    ("陆号", "六号"),
    ("柒号", "七号"),
    ("捌号", "八号"),
    ("玖号", "九号"),
    ("拾号", "十号"),
    ("玖名", "九名"),
)

# Leading tag + 祠堂 aspiration slip fix observed in eleven_v3 ('[dramatically] 祠堂' -> cū táng)
_LEADING_TAG_CITANG = re.compile(r"^(\s*(?:\[[^\[\]]+\]\s*)+)祠堂")


# Modern finance, business & Buffett Shareholder Letters polyphone disambiguation.
# Kept strictly separate from XIANXIA_POLYPHONE_MAP so terms like '重仓' (zhòng cāng)
# vs '资产重组' (chóng zǔ) and '老行当' (háng dang) are pronounced with 100% accuracy.
FINANCE_POLYPHONE_MAP: tuple[tuple[str, str], ...] = (
    # Industry / profession (háng vs xíng)
    ("老行当", "老航当"),
    ("这行当", "这航当"),
    ("干这一行", "干这一航"),
    ("干哪一行", "干哪一航"),
    ("外行人", "外航人"),
    ("内行人", "内航人"),
    ("同行们", "同航们"),
    ("全行业", "全航业"),
    ("夕阳行业", "夕阳航业"),
    ("传统行业", "传统航业"),
    ("餐饮行里", "餐饮航里"),
    # Financial restructuring / multi-layer (chóng vs zhòng)
    ("资产重组", "资产崇组"),
    ("破产重组", "破产崇组"),
    ("债务重组", "债务崇组"),
    ("双重暴击", "双崇暴击"),
    ("双重护城河", "双崇护城河"),
    ("多重杠杆", "多崇杠杆"),
    ("第一重防线", "第一崇防线"),
    ("第二重防线", "第二崇防线"),
    ("第三重防线", "第三崇防线"),
    # Market adjustments (tiáo vs diào)
    ("调仓换股", "条仓换股"),
    ("调仓", "条仓"),
    ("大幅回调", "大幅回条"),
    ("市场回调", "市场回条"),
    ("股价回调", "股价回条"),
    ("利率下调", "利率下条"),
    ("评级下调", "评级下条"),
    ("下调预期", "下条预期"),
    ("上调预期", "上条预期"),
    # Accounting, idioms & colloquial expressions
    ("摊薄收益", "摊博收益"),
    ("每股摊薄", "每股摊博"),
    ("摊薄", "摊博"),
    ("否极泰来", "匹极泰来"),
    ("勒紧裤腰带", "嘞紧裤腰带"),
    # Smooth foreign name dot separators for TTS while keeping canonical '·' in SRT
    ("伯克希尔·哈撒韦", "伯克希尔哈撒韦"),
    ("沃伦·巴菲特", "沃伦巴菲特"),
    ("查理·芒格", "查理芒格"),
    ("本杰明·格雷厄姆", "本杰明格雷厄姆"),
    ("阿吉特·贾恩", "阿吉特贾恩"),
    ("雷曼·兄弟", "雷曼兄弟"),
)


def apply_xianxia_polyphone_overrides(text: str) -> str:
    """Return phonetic `tts_text` override if `text` contains error-prone polyphones; else return `text`."""
    if not text:
        return text
    out = _LEADING_TAG_CITANG.sub(r"\1磁堂", text)
    for canonical, phonetic in XIANXIA_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    return out


def apply_finance_polyphone_overrides(text: str) -> str:
    """Return phonetic `tts_text` override for modern finance/business Mandarin podcast lines."""
    if not text:
        return text
    out = text
    for canonical, phonetic in FINANCE_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    return out


def apply_domain_polyphone_overrides(text: str, domain: str = "xianxia") -> str:
    """Apply domain-appropriate Mandarin polyphone overrides (`xianxia`, `finance_podcast`, or `none`)."""
    if not text or domain == "none":
        return text
    if domain == "finance_podcast":
        return apply_finance_polyphone_overrides(text)
    return apply_xianxia_polyphone_overrides(text)


def compute_tts_text_override(canonical_tagged_text: str, domain: str = "xianxia") -> str:
    """Return non-empty `tts_text` only when phonetic disambiguation differs from `canonical_tagged_text`."""
    overridden = apply_domain_polyphone_overrides(canonical_tagged_text, domain=domain)
    return overridden if overridden != canonical_tagged_text else ""
