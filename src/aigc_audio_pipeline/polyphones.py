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


# Classical Chinese supernatural / Liaozhai folk-horror polyphone overrides.
# Extends classical pronunciation fixes with ghost-tale vocabulary (e.g. 兰若寺 lán rě sì,
# 稽首 qǐ shǒu, 屏息 bǐng xī, 打更 dǎ gēng) while keeping canonical literary text in .srt.
LIAOZHAI_POLYPHONE_MAP: tuple[tuple[str, str], ...] = (
    # Famous Liaozhai proper nouns & Buddhist/Daoist vocabulary
    ("兰若寺", "兰惹寺"),
    ("兰若古寺", "兰惹古寺"),
    ("稽首", "启首"),
    ("长揖", "长伊"),
    ("道行", "道衡"),
    ("女冠", "女观"),
    ("行脚僧", "形脚僧"),
    # Night watches & classical timekeeping (gēng vs gèng)
    ("打更", "打羹"),
    ("更鼓", "羹鼓"),
    ("更夫", "羹夫"),
    ("更漏", "羹漏"),
    ("三更半夜", "三羹半夜"),
    ("三更时分", "三羹时分"),
    ("三更天", "三羹天"),
    ("三更梆子", "三羹梆子"),
    ("三更", "三羹"),
    ("五更天", "五羹天"),
    ("五更", "五羹"),
    # Breath, fear, and supernatural horror verbs/nouns
    ("屏息凝神", "丙息凝神"),
    ("屏住呼吸", "丙住呼吸"),
    ("屏气凝神", "丙气凝神"),
    ("屏息", "丙息"),
    ("躯壳", "躯咳"),
    ("血泊", "血坡"),
    ("龟裂", "均裂"),
    ("佝偻", "沟楼"),
    ("模样", "磨样"),
    ("憎恶", "增雾"),
    ("颤栗", "占栗"),
    ("战栗", "占栗"),
    ("重门", "崇门"),
    ("重重", "崇崇"),
    ("一乘轿子", "一胜轿子"),
    ("背回", "杯回"),
    ("背着", "杯着"),
    ("背起", "杯起"),
    ("拾级而上", "涉级而上"),
    ("拾级", "涉级"),
    ("降临", "酱临"),
    ("吐血", "兔血"),
    ("埋怨", "蛮怨"),
    ("老行当", "老航当"),
)


# Cosmic-horror / Lovecraftian investigative drama polyphone & transliteration smoothing.
# Strips interpunct '·' in Western names only inside tts_text so Speech flows cleanly
# while .srt subtitles preserve canonical typographic '·'.
COSMIC_HORROR_POLYPHONE_MAP: tuple[tuple[str, str], ...] = (
    # Suspense & forensic/expedition polyphones
    ("屏息凝神", "丙息凝神"),
    ("屏住呼吸", "丙住呼吸"),
    ("屏息", "丙息"),
    ("龟裂", "均裂"),
    ("躯壳", "躯咳"),
    ("血泊", "血坡"),
    ("拓印", "踏印"),
    ("拓片", "踏片"),
    ("船舷", "船咸"),
    ("舷窗", "咸窗"),
    ("重重迷雾", "崇崇迷雾"),
    ("重重冰山", "崇崇冰山"),
    ("重重封锁", "崇崇封锁"),
    ("重重", "崇崇"),
    ("埋怨", "蛮怨"),
    ("模样", "磨样"),
    ("颤栗", "占栗"),
    ("战栗", "占栗"),
    ("憎恶", "增雾"),
    ("着陆", "桌陆"),
    ("着魔", "招魔"),
    ("行踪", "形踪"),
    ("一行人", "一形人"),
    ("老行当", "老航当"),
    ("调频", "条频"),
    ("调谐", "条谐"),
    ("降临", "酱临"),
    ("背负", "杯负"),
    ("背起", "杯起"),
    # Smooth Western name interpuncts for TTS fluency (canonical '·' kept in .srt)
    ("弗朗西斯·瑟斯顿", "弗朗西斯瑟斯顿"),
    ("乔治·安吉尔", "乔治安吉尔"),
    ("亨利·威尔科克斯", "亨利威尔科克斯"),
    ("约翰·勒格拉斯", "约翰勒格拉斯"),
    ("古斯塔夫·约翰森", "古斯塔夫约翰森"),
    ("罗伯特·奥姆斯特德", "罗伯特奥姆斯特德"),
    ("扎多克·艾伦", "扎多克艾伦"),
    ("奥贝德·马什", "奥贝德马什"),
    ("阿米·皮尔斯", "阿米皮尔斯"),
    ("纳胡姆·加德纳", "纳胡姆加德纳"),
    ("阿尔伯特·威尔马斯", "阿尔伯特威尔马斯"),
    ("亨利·阿克利", "亨利阿克利"),
    ("亨利·阿米蒂奇", "亨利阿米蒂奇"),
    ("威尔伯·沃特雷", "威尔伯沃特雷"),
    ("拉维妮娅·沃特雷", "拉维妮娅沃特雷"),
    ("威廉·戴尔", "威廉戴尔"),
    ("犹格·索托斯", "犹格索托斯"),
    ("米·戈", "米戈"),
    ("阿卜杜勒·阿尔哈兹莱德", "阿卜杜勒阿尔哈兹莱德"),
)


# Intellectual history / political economy audio-drama polyphone & Western economist name smoothing.
HAYEK_ECONOMICS_POLYPHONE_MAP: tuple[tuple[str, str], ...] = (
    ("老行当", "老航当"),
    ("这行当", "这航当"),
    ("各行各业", "各航各业"),
    ("同行们", "同航们"),
    ("内行人", "内航人"),
    ("外行人", "外航人"),
    ("调控", "条控"),
    ("调节", "条节"),
    ("调配", "条配"),
    ("重重审批", "崇崇审批"),
    ("重重关卡", "崇崇关卡"),
    ("重重", "崇崇"),
    ("埋怨", "蛮怨"),
    ("屏息", "丙息"),
    ("降临", "酱临"),
    ("背负", "杯负"),
    ("弗里德里希·哈耶克", "弗里德里希哈耶克"),
    ("约翰·梅纳德·凯恩斯", "约翰梅纳德凯恩斯"),
    ("亚当·斯密", "亚当斯密"),
    ("威廉·贝弗里奇", "威廉贝弗里奇"),
    ("路德维希·冯·米塞斯", "路德维希冯米塞斯"),
    ("阿莱克西·德·托克维尔", "阿莱克西德托克维尔"),
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


def apply_liaozhai_polyphone_overrides(text: str) -> str:
    """Return phonetic `tts_text` override for classical Liaozhai supernatural radio-drama lines."""
    if not text:
        return text
    out = _LEADING_TAG_CITANG.sub(r"\1磁堂", text)
    for canonical, phonetic in LIAOZHAI_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    return out


def apply_cosmic_horror_polyphone_overrides(text: str) -> str:
    """Return phonetic `tts_text` override for Lovecraftian cosmic-horror Mandarin radio-drama lines."""
    if not text:
        return text
    out = text
    for canonical, phonetic in COSMIC_HORROR_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    return out


def apply_hayek_economics_polyphone_overrides(text: str) -> str:
    """Return phonetic `tts_text` override for 1944 Cambridge economics intellectual drama lines."""
    if not text:
        return text
    out = text
    for canonical, phonetic in HAYEK_ECONOMICS_POLYPHONE_MAP:
        if canonical in out:
            out = out.replace(canonical, phonetic)
    return out


def apply_domain_polyphone_overrides(text: str, domain: str = "xianxia") -> str:
    """Apply domain-appropriate Mandarin polyphone overrides."""
    if not text or domain == "none":
        return text
    if domain == "finance_podcast":
        return apply_finance_polyphone_overrides(text)
    if domain == "liaozhai_horror":
        return apply_liaozhai_polyphone_overrides(text)
    if domain == "cosmic_horror":
        return apply_cosmic_horror_polyphone_overrides(text)
    if domain == "hayek_economics":
        return apply_hayek_economics_polyphone_overrides(text)
    return apply_xianxia_polyphone_overrides(text)


def compute_tts_text_override(canonical_tagged_text: str, domain: str = "xianxia") -> str:
    """Return non-empty `tts_text` only when phonetic disambiguation differs from `canonical_tagged_text`."""
    overridden = apply_domain_polyphone_overrides(canonical_tagged_text, domain=domain)
    return overridden if overridden != canonical_tagged_text else ""
