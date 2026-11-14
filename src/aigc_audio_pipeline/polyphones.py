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

# Sci-Fi & SCP Foundation Mandarin phonetic overrides (prevents '模因' -> mú yīn,
# hyphenated code minus-sign glitches, and English accent drift on Keter/Euclid/O5).
SCIFI_SCP_POLYPHONE_MAP: tuple[tuple[str, str], ...] = (
    # mó yīn vs mú yīn disambiguation (exact 2nd tone homophone 摩)
    ("超模因", "超摩因"),
    ("逆模因", "逆摩因"),
    ("模因", "摩因"),
    # SCP & O5 hyphenated designations -> crisp Mainland Mandarin readouts
    ("SCP-055", "SCP零五五"),
    ("SCP-001", "SCP零零一"),
    ("SCP-013", "SCP零一三"),
    ("SCP-033", "SCP零三三"),
    ("SCP-666", "SCP六六六"),
    ("SCP-1425", "SCP一四二五"),
    ("SCP-2256", "SCP二二五六"),
    ("SCP-3125", "SCP三一二五"),
    ("SCP-4739", "SCP四七三九"),
    ("SCP-4987", "SCP四九八七"),
    ("SCP-7381", "SCP七三八一"),
    ("O5-8", "欧五八"),
    ("O5议会", "欧五议会"),
    ("O5们", "欧五们"),
    ("一名O5", "一名欧五"),
    ("这位O5", "这位欧五"),
    ("那个O5", "那个欧五"),
    ("成为O5", "成为欧五"),
    ("O5", "欧五"),
    # Object classes -> clean Mandarin transliteration in TTS while keeping canonical text in SRT
    ("Keter级", "凯特尔级"),
    ("Keter", "凯特尔"),
    ("Euclid级", "欧几里得级"),
    ("Euclid", "欧几里得"),
    ("Safe级", "安全级"),
    # Modern sci-fi & ordnance polyphones (dàn vs tán, chóng vs zhòng)
    ("核弹头", "核但头"),
    ("氢弹", "氢但"),
    ("核弹", "核但"),
    ("炸弹", "炸但"),
    ("子弹", "子但"),
    ("弹匣", "但匣"),
    ("弹头", "但头"),
    ("重影", "崇影"),
    ("重叠", "崇叠"),
)

# Leading tag + 祠堂 aspiration slip fix observed in eleven_v3 ('[dramatically] 祠堂' -> cū táng)
_LEADING_TAG_CITANG = re.compile(r"^(\s*(?:\[[^\[\]]+\]\s*)+)祠堂")


def apply_xianxia_polyphone_overrides(text: str) -> str:
    """Return phonetic `tts_text` override if `text` contains error-prone polyphones; else return `text`."""
    if not text:
        return text
    out = _LEADING_TAG_CITANG.sub(r"\1磁堂", text)
    for canonical, phonetic in XIANXIA_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    for canonical, phonetic in SCIFI_SCP_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    return out


apply_polyphone_overrides = apply_xianxia_polyphone_overrides


def compute_tts_text_override(canonical_tagged_text: str) -> str:
    """Return non-empty `tts_text` only when phonetic disambiguation differs from `canonical_tagged_text`."""
    overridden = apply_xianxia_polyphone_overrides(canonical_tagged_text)
    return overridden if overridden != canonical_tagged_text else ""
