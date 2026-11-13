"""Build, validate, render, and archive Batch 5: Episodes E023–E027 (Chapters 23–27)."""

from __future__ import annotations

from pathlib import Path
import sys

SCRATCH_DIR = Path(__file__).resolve().parent
REPO_SRC = Path(__file__).resolve().parents[3] / "src"
for p in (str(REPO_SRC), str(SCRATCH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from aigc_audio_pipeline.models import VoiceCastingRegistry
from batch_runner import BASE_DIR, REGISTRY_PATH, SCRIPTS_DIR, render_and_archive_episode
from episode_compiler import compile_episode_cue_sheet, save_episode_scripts

SOURCE_DIR = BASE_DIR / "source_chapters"


def build_all_batch5() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E023 · 第23章 对手先手，血月投影下的窒息危机 (54 paras, 12 quotes)
    # =========================================================================
    md_23 = SOURCE_DIR / "第23章_对手先手，血月投影下的窒息危机.md"
    s23 = compile_episode_cue_sheet(
        episode_id="E023",
        chapter_number=23,
        source_md_path=md_23,
        source_rel_path=f"02_分章精修正文/{md_23.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_blood_moon_siege_clash",
                "start_p": 1,
                "title": "第一幕 · 锁魂幡压顶，重刀抗双罡",
                "bgm_prompt": "Suffocating intense Chinese xianxia boss-siege soundtrack, roaring crimson sky pressure, pounding war drums and desperate blade-against-sky clash, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_qin_lie_smashes_wall",
                "start_p": 18,
                "title": "第二幕 · 秦烈破墙出，鬼头断双截",
                "bgm_prompt": "Heroic tragic Chinese frontier brotherhood battle score, thunderous brass-like war horn, fierce erhu cry and sacrificial courage, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act3_thunder_pearl_dark_river",
                "start_p": 28,
                "title": "第三幕 · 替草受死掌，天雷炸暗河",
                "bgm_prompt": "Cataclysmic explosion and rushing subterranean river underscore, heavy muffled heartbeat fading into dark roaring underground rapids, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_cavern_resolve_demon_fire",
                "start_p": 45,
                "title": "第四幕 · 血染钟乳滩，向死觊妖火",
                "bgm_prompt": "Bleak dripping underground cavern guqin rising into fierce unyielding dark-gold determination, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        skip_onomatopoeia_paras={1, 13, 19, 25, 32, 36},
        dialogue_specs=[
            {"match": "本公子还纳闷是谁杀了厉苍师叔与孙长老", "role_id": "pei_xuandu", "tags": "[sarcastic] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "裴玄度高空摇引月锁魂幡残忍下令"},
            {"match": "遵少主令！", "role_id": "sect_elder_antagonist", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "大长老莫沧十丈青色剑罡压落"},
            {"match": "挡！", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "note": "陆烬全开基因锁祭玄龟盾与断岳硬抗"},
            {"match": "咦？竟能硬接老夫八成剑罡不死", "role_id": "sect_elder_antagonist", "tags": "[gasps] [coldly]", "stability": 0.0, "note": "莫沧骇然追斩十字剑罡"},
            {"match": "玄剑宗的杂碎！敢动老陆家的种", "role_id": "qin_lie", "tags": "[angry] [shouting]", "stability": 0.0, "note": "独眼老将秦烈撞碎北衙高墙舍命挡剑"},
            {"match": "秦伯父，快退！", "role_id": "lu_jin", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "陆烬目眦欲裂急喝"},
            {"match": "区区镇渊司走狗也敢找死", "role_id": "li_cang", "tags": "[angry] [shouting]", "stability": 0.0, "note": "二长老严刑崩断秦烈鬼头刀直取咽喉"},
            {"match": "自身难保还敢救人，去死吧", "role_id": "sect_elder_antagonist", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "莫沧碎心青冥印狠印陆烬后心"},
            {"match": "秦伯父……别管我，活下去", "role_id": "lu_jin", "tags": "[hoarsely] [shouting]", "stability": 0.0, "note": "浴血陆烬引爆天雷珠坠入地下暗河"},
            {"match": "少主放心，老夫方才那一掌", "role_id": "sect_elder_antagonist", "tags": "[calmly]", "stability": 0.5, "note": "莫沧笃定陆烬心脉已碎必死"},
            {"match": "本公子不见尸首绝不安心", "role_id": "pei_xuandu", "tags": "[coldly]", "stability": 0.0, "note": "裴玄度命锁秦烈吊上赤松岭血坛诱敌"},
            {"match": "莫沧、严刑、裴玄度……还有那面", "role_id": "lu_jin", "tags": "[hoarsely] [coldly]", "stability": 0.0, "note": "溶洞石滩上陆烬擦去黑血燃起决死杀意"},
        ],
        sfx_blueprint=[
            {"p": 1, "pos": "before", "slug": "blood_moon_crush_pavement", "sfx_prompt": "Suffocating crimson energy beam slamming stone street pavement into spiderweb cracks", "duration_seconds": 3.0, "gain_db": 1.5, "note": "轰隆！百丈血月虚影压裂北衙后巷青石地"},
            {"p": 13, "pos": "before", "slug": "turtle_shield_explode_clash", "sfx_prompt": "Deafening spiritual sword explosion shattering a bronze shield into shrapnel and plowing iron boots across stone", "duration_seconds": 3.4, "gain_db": 2.0, "note": "砰咔嚓！青罡玄龟盾炸碎，断岳硬撼双剑罡"},
            {"p": 19, "pos": "before", "slug": "qin_lie_smash_brick_wall", "sfx_prompt": "Massive three-foot brick wall exploding outward as an armored warrior charges roaring into battle", "duration_seconds": 3.0, "gain_db": 2.0, "note": "轰！秦烈撞破北衙高墙杀出"},
            {"p": 25, "pos": "before", "slug": "ghost_sabre_snap_in_two", "sfx_prompt": "Heavy iron broadsword clashing violently against a blazing flying sword and snapping cleanly in half", "duration_seconds": 2.6, "gain_db": 1.5, "note": "铛咔嚓！秦烈百炼鬼头重刀崩断"},
            {"p": 32, "pos": "before", "slug": "heart_shatter_palm_impact", "sfx_prompt": "Sickening heavy martial palm thud slamming into ribs with bone cracking and protective talisman burning", "duration_seconds": 2.6, "gain_db": 1.5, "note": "砰！莫沧碎心青冥印击中后心，九死血替草替死"},
            {"p": 36, "pos": "before", "slug": "thunder_pearl_blast_river_plunge", "sfx_prompt": "Cataclysmic purple lightning thunder-pearl explosion blasting granite street open into a roaring subterranean river splash", "duration_seconds": 4.2, "gain_db": 2.5, "note": "轰隆！破阵天雷珠炸穿地底黑水暗河坠入激流"},
        ],
    )
    j23, m23 = save_episode_scripts(s23, SCRIPTS_DIR, registry)
    built.append(("E023", j23, m23))

    # =========================================================================
    # E024 · 第24章 溶洞炼妖煞，向死而生的反制局 (56 paras, 10 quotes)
    # =========================================================================
    md_24 = SOURCE_DIR / "第24章_溶洞炼妖煞，向死而生的反制局.md"
    s24 = compile_episode_cue_sheet(
        episode_id="E024",
        chapter_number=24,
        source_md_path=md_24,
        source_rel_path=f"02_分章精修正文/{md_24.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_reforge_duanyue_heavy_blade",
                "start_p": 1,
                "title": "第一幕 · 引火出零牌，精血铸断岳",
                "bgm_prompt": "Dark subterranean weapon-forging Chinese xianxia score, dripping cavern echoes, eerie violet-green demon flame hum and resonant heavy iron rebirth, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_swallow_demon_fire_mid_foundation",
                "start_p": 16,
                "title": "第二幕 · 生吞三阶火，二段破筑中",
                "bgm_prompt": "Ferocious agonizing-to-triumphant Chinese martial alchemy score, thunderous double-heartbeat war drums, searing erhu and blazing golden breakthrough, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_thread_burning_finger_alliance",
                "start_p": 30,
                "title": "第三幕 · 悟透焚线指，重返鬼樊楼",
                "bgm_prompt": "Cool razor-sharp ancient Chinese tactical theme, crisp plucked pipa, deep confident bass pulse and awe-struck underground reunion, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_single_blade_ascends_red_pine",
                "start_p": 50,
                "title": "第四幕 · 双雷撕护阵，单刀踏血坛",
                "bgm_prompt": "Monumental epic Chinese xianxia avenger march, twin thunder explosions, heavy unstoppable war drums and lone hero ascending stone steps, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        skip_onomatopoeia_paras={9, 14, 18, 22, 25, 37, 51},
        dialogue_specs=[
            {"match": "成败在此一举，起", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬借零号铭牌引出三分之一焚锁妖煞火"},
            {"match": "给我炼！", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "note": "陆烬生吞三阶紫青妖煞火种以毒攻毒"},
            {"match": "这就是【焚锁妖煞火】……难怪当年", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.5, "note": "陆烬顿悟逆烧血月命线克制之法"},
            {"match": "成了！这一招，便叫【焚线指】", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "试符成功创出焚线指"},
            {"match": "陆、陆丹师！你真没死", "role_id": "chu_xiazi", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "秘密水闸前褚瞎子狂喜惊呼"},
            {"match": "让楼主与褚老久候了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬背负六十四斤断岳重刀踏水而出"},
            {"match": "裴玄度以为我死在暗河里", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "邀鬼樊楼赌最后一把"},
            {"match": "连命都杀不死的人，本座有什么不敢跟", "role_id": "hongxiu_louzhu", "tags": "[dramatically]", "stability": 0.0, "note": "红袖楼主震撼于陆烬筑基中期气机斩钉截铁跟注"},
            {"match": "好。今夜子时二刻，劳烦楼主派死士", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "定计子时二刻双雷破东阵，一人独斩三獠"},
            {"match": "裴玄度，你的刀太钝，阎王殿不收陆某", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬提重刀踏上赤松岭山门传遍夜空索命宣言"},
        ],
        sfx_blueprint=[
            {"p": 9, "pos": "before", "slug": "violet_demon_fire_melt_iron", "sfx_prompt": "Eerie spatial warp sizzle as ancient violet demon flame melts heavy dark-gold broadsword steel", "duration_seconds": 2.8, "gain_db": 1.0, "note": "嗤啦！焚锁妖煞火熔化两截断岳寒铁"},
            {"p": 14, "pos": "before", "slug": "quench_reforged_duanyue", "sfx_prompt": "Molten heavy broadsword plunged into icy underground river water with a massive steam roar and deep resonant dragon-like blade ring", "duration_seconds": 3.8, "gain_db": 2.0, "note": "滋滋嗡！暗河淬火定型，六十四斤二阶极品断岳重现人间"},
            {"p": 18, "pos": "before", "slug": "swallow_flame_double_genelock", "motif_id": "motif_genelock_awaken", "gain_db": 2.0, "note": "轰咔嚓！吞火焚寒毒，开启一阶圆满二段燃血晋筑基中期"},
            {"p": 37, "pos": "before", "slug": "burn_moon_talisman_ghost_fire", "sfx_prompt": "Sharp finger snap igniting a paper talisman from within into a crisp burst of eerie green flame", "duration_seconds": 2.0, "gain_db": 0.5, "note": "噗！紫青妖火顺共鸣线引爆拜月符"},
            {"p": 51, "pos": "before", "slug": "twin_thunder_pearls_tear_barrier", "sfx_prompt": "Two deafening consecutive purple-lightning thunder explosions shattering a massive mountain spiritual barrier into falling glass-like sparks", "duration_seconds": 4.2, "gain_db": 2.5, "note": "轰！轰隆！两枚破阵天雷珠撕裂赤松岭护山大阵"},
        ],
    )
    j24, m24 = save_episode_scripts(s24, SCRIPTS_DIR, registry)
    built.append(("E024", j24, m24))

    # =========================================================================
    # E025 · 第25章 第一层黑幕揭开，所谓仙门皆屠夫 (47 paras, 19 quotes)
    # =========================================================================
    md_25 = SOURCE_DIR / "第25章_第一层黑幕揭开，所谓仙门皆屠夫.md"
    s25 = compile_episode_cue_sheet(
        episode_id="E025",
        chapter_number=25,
        source_md_path=md_25,
        source_rel_path=f"02_分章精修正文/{md_25.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_blood_altar_shock_sword_forest",
                "start_p": 1,
                "title": "第一幕 · 独刀临血坛，八十剑成林",
                "bgm_prompt": "High-mountain wind and taut ominous Chinese war drums, lone dark-clad bladesman facing eighty drawn swords before a crimson altar, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_cleave_altar_expose_skeletons",
                "start_p": 16,
                "title": "第二幕 · 一刀劈白玉，枯骨碎道心",
                "bgm_prompt": "Shattering dramatic Chinese orchestral revelation score, heavy stone collapse followed by horrified trembling strings and mournful xiao, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_slaughterhouse_truth_mutiny",
                "start_p": 31,
                "title": "第三幕 · 字字诛屠夫，剑阵尽崩盘",
                "bgm_prompt": "Blazing righteous Chinese xianxia indictment theme, resonant low bronze gongs, surging strings of awakening and collapsing tyranny, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_mask_torn_twin_elders_pounce",
                "start_p": 40,
                "title": "第四幕 · 假面撕粉碎，双老借月扑",
                "bgm_prompt": "Ferocious demonic xianxia boss-prelude score, screaming blood-banner wind, frantic pipa and overwhelming murderous momentum, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        skip_onomatopoeia_paras={11, 21, 23, 26, 36},
        dialogue_specs=[
            {"match": "老陆家的小子……哈哈哈哈", "role_id": "qin_lie", "tags": "[laughs] [shouting]", "stability": 0.0, "note": "铁柱上秦烈狂笑震响锁链"},
            {"match": "陆烬！救我！阵眼就在裴玄度脚下", "role_id": "su_qinghan", "tags": "[crying] [shouting]", "stability": 0.0, "note": "赤铜血炉内苏清寒绝望哭喊指认阵眼"},
            {"match": "贱婢闭嘴！", "role_id": "pei_xuandu", "tags": "[angry] [shouting]", "stability": 0.0, "note": "裴玄度挥袖封死苏清寒哑穴"},
            {"match": "莫大长老，你前夜不是跟本公子保证", "role_id": "pei_xuandu", "tags": "[coldly]", "stability": 0.0, "note": "裴玄度阴冷质问莫沧"},
            {"match": "此子定是吞服了陆擎苍当年", "role_id": "sect_elder_antagonist", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "莫沧令八十弟子结玄剑伏魔阵"},
            {"match": "大胆魔徒陆烬，竟敢勾结黑市", "role_id": "male_disciple_a", "tags": "[shouting]", "stability": 0.0, "note": "不明真相的前排年轻剑修厉喝"},
            {"match": "正道仙门？", "role_id": "lu_jin", "tags": "[sarcastic] [coldly]", "stability": 0.5, "note": "陆烬冷笑停步"},
            {"match": "你们替裴玄度和山上那个老怪物卖命拔剑之前", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬灵识裹音传遍全场喝令睁眼看白骨"},
            {"match": "大胆！拦住他的刀气！", "role_id": "male_disciple_b", "tags": "[shouting]", "stability": 0.0, "note": "前排弟子举剑合挡"},
            {"match": "这、这块玉牌是三年前被选上山", "role_id": "male_disciple_a", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "弟子认出周师兄命牌骇然变调"},
            {"match": "还有这块！这是寒玉峰四品风灵脉的林师姐", "role_id": "female_maid_npc", "tags": "[crying] [shouting]", "stability": 0.0, "note": "女弟子认出林师姐干尸惨叫"},
            {"match": "假的！这怎么可能！", "role_id": "male_disciple_b", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "伏魔剑阵信仰崩塌大乱"},
            {"match": "哪有什么真传闭关，哪有什么南疆驻守", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬掷账册玉镯揭穿赤阳老祖半化尸煞真相"},
            {"match": "男弟子养熟了埋进祭坛底下抽干骨髓做药渣", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "刀指高坛痛斥牲口屠宰场，字字诛心"},
            {"match": "我不修了！我不要变成干尸药渣", "role_id": "male_disciple_a", "tags": "[crying] [shouting]", "stability": 0.0, "note": "二十余名外门弟子扔剑溃逃"},
            {"match": "谁敢逃半步，格杀勿论！", "role_id": "li_cang", "tags": "[angry] [shouting]", "stability": 0.0, "note": "二长老严刑挥剑斩杀逃跑同门彻底寒透人心"},
            {"match": "一群凡夫俗子，若非本宗赐予功法灵药", "role_id": "pei_xuandu", "tags": "[arrogant] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "裴玄度撕破温润假面狰狞咆哮"},
            {"match": "莫大长老、严二长老，此子能看穿血种底细", "role_id": "pei_xuandu", "tags": "[angry] [shouting]", "stability": 0.0, "note": "裴玄度插锁魂幡暗扣紫府一击血符"},
            {"match": "小畜生，前夜算你命大逃过一劫", "role_id": "sect_elder_antagonist", "tags": "[angry] [shouting]", "stability": 0.0, "note": "莫沧与严刑放开百会穴借血月灵压合扑而下"},
        ],
        sfx_blueprint=[
            {"p": 4, "pos": "before", "slug": "pillar_iron_chains_shake", "sfx_prompt": "Heavy iron torture chains rattling violently against a stone pillar in howling mountain wind", "duration_seconds": 2.4, "gain_db": 0.5, "note": "秦烈狂笑震响刑柱玄铁锁链"},
            {"p": 11, "pos": "before", "slug": "eighty_swords_unsheathe", "sfx_prompt": "Eighty steel longswords unsheathing simultaneously in crisp metallic unison on stone steps", "duration_seconds": 2.6, "gain_db": 1.5, "note": "锵锵锵！八十名剑修齐拔剑结阵"},
            {"p": 21, "pos": "before", "slug": "blade_aura_shatter_marble_altar", "sfx_prompt": "Colossal golden blade wave knocking aside steel swords and blasting open a thick white marble altar wall, spilling rattling bones and jade plaques", "duration_seconds": 4.2, "gain_db": 2.0, "note": "轰咔嚓！断岳刀罡劈塌白玉祭坛底座，三十余具干瘪白骨与命牌滚落"},
            {"p": 37, "pos": "after", "slug": "disciples_drop_swords_flee", "sfx_prompt": "Dozens of steel swords clattering onto stone steps as panicking footsteps scatter into the night", "duration_seconds": 2.8, "gain_db": 1.0, "note": "众弟子信仰崩塌扔剑溃逃"},
            {"p": 47, "pos": "before", "slug": "twin_spirit_weapons_sky_dive", "sfx_prompt": "Twin high-tier flying blades and fiery hooks screaming down through night air with thunderous pressure", "duration_seconds": 3.2, "gain_db": 1.5, "note": "青冥子母双剑与赤火锁魂双钩合扑而下"},
        ],
    )
    j25, m25 = save_episode_scripts(s25, SCRIPTS_DIR, registry)
    built.append(("E025", j25, m25))

    # =========================================================================
    # E026 · 第26章 一阶锁全开，刀斩双长老！ (56 paras, 12 quotes)
    # =========================================================================
    md_26 = SOURCE_DIR / "第26章_一阶锁全开，刀斩双长老！.md"
    s26 = compile_episode_cue_sheet(
        episode_id="E026",
        chapter_number=26,
        source_md_path=md_26,
        source_rel_path=f"02_分章精修正文/{md_26.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_second_gear_blood_burn_yanxing",
                "start_p": 1,
                "title": "第一幕 · 二段燃血开，焚线劈严刑",
                "bgm_prompt": "Blazing high-octane Chinese xianxia combat score, double primal heartbeat drums, screaming violet fire and instantaneous lethal blade strike, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_shatter_mother_sword_mocang",
                "start_p": 26,
                "title": "第二幕 · 重刀破剑墙，五息灭双老",
                "bgm_prompt": "Earth-shaking heroic Chinese martial dominance soundtrack, roaring brass-like suona/horn, thunderous percussion and unstoppable dark-gold broadsword power, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_pei_xuandu_crushes_blood_talisman",
                "start_p": 47,
                "title": "第三幕 · 裴贼胆俱裂，捏碎紫府符",
                "bgm_prompt": "Deadly battlefield silence snapping into apocalyptic zombie-ancestor crimson sky dread, suffocating sub-bass choir-free drone, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act4_zero_plate_opens_xujie_rift",
                "start_p": 52,
                "title": "第四幕 · 十丈尸煞掌，举牌开吞口",
                "bgm_prompt": "Colossal cosmic confrontation climax score, crushing sky-palm rumble met by ancient bronze star-track resonance, instrumental only, no vocals",
                "bgm_duration_s": 80.0,
            },
        ],
        skip_onomatopoeia_paras={7, 24, 26, 37, 43, 51},
        dialogue_specs=[
            {"match": "小子小心！这两个老狗借了天上血祭邪力", "role_id": "qin_lie", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "铁柱上秦烈嘶声示警"},
            {"match": "借血月之力么？借得越多，死得越快", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬冷笑迎击"},
            {"match": "找死！敢弃守硬闯老夫的赤火钩网", "role_id": "li_cang", "tags": "[arrogant] [shouting]", "stability": 0.0, "note": "二长老严刑狞笑收双钩"},
            {"match": "给你送点真火暖暖脑子！", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "陆烬贴耳冷喝使出焚线指"},
            {"match": "啊！我的头！什么鬼火在烧老夫神魂", "role_id": "li_cang", "tags": "[crying] [shouting]", "stability": 0.0, "note": "严刑七窍喷紫青妖火抱头惨嚎"},
            {"match": "严师弟！", "role_id": "sect_elder_antagonist", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "大长老莫沧亡魂皆冒"},
            {"match": "不能让他近身！青冥化盾，子母千刃", "role_id": "sect_elder_antagonist", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "莫沧喷十年精血凝三尺青冥剑墙"},
            {"match": "前夜受你一掌碎心印，陆某说过", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "陆烬腾空两丈紫金半月斩落"},
            {"match": "狂妄！老夫这二阶极品母剑便是半步紫府", "role_id": "sect_elder_antagonist", "tags": "[angry] [shouting]", "stability": 0.0, "note": "莫沧疯狂死顶剑墙"},
            {"match": "不！这不可能！你的灵液怎么会重到这种地步", "role_id": "sect_elder_antagonist", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "青冥母剑被一刀劈断莫沧骇然绝望"},
            {"match": "去死！给本公子去死！这是赤阳老祖亲手封存", "role_id": "pei_xuandu", "tags": "[crying] [shouting]", "stability": 0.0, "note": "崩溃的裴玄度尖叫捏碎紫府一击血符"},
            {"match": "陆烬快躲开！那是真紫府一击", "role_id": "qin_lie", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "秦烈肝胆俱裂嘶吼"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "before", "slug": "stage1_full_double_heartbeat", "motif_id": "motif_genelock_awaken", "gain_db": 2.5, "note": "咚！咚！第一阶基因锁圆满二段燃血全面开启"},
            {"p": 18, "pos": "before", "slug": "flame_finger_reverse_ignite", "sfx_prompt": "Sharp searing ignition hiss as violet demon fire shoots up spiritual threads and explodes inside a skull", "duration_seconds": 2.8, "gain_db": 1.5, "note": "嗤啦！焚线指顺六根命线逆烧泥丸宫"},
            {"p": 24, "pos": "before", "slug": "cleave_yan_xing_in_half", "sfx_prompt": "Sixty-four pound heavy broadsword cleaving straight down through armor and slamming stone steps into dead silence", "duration_seconds": 2.8, "gain_db": 2.0, "note": "噗嗤！一刀将筑基后期严刑劈成两半"},
            {"p": 37, "pos": "before", "slug": "duanyue_shatter_ice_sword_wall", "sfx_prompt": "Deafening mountain-shaking clash of a heavy broadsword shattering a thick ice-crystal sword wall and snapping a master spirit blade in half", "duration_seconds": 3.8, "gain_db": 2.5, "note": "铛咔嚓！断岳正面劈碎三尺剑墙斩断二阶极品青冥母剑"},
            {"p": 43, "pos": "before", "slug": "behead_mo_cang_roll", "sfx_prompt": "Clean horizontal heavy blade sweep severing a head rolling across white marble steps", "duration_seconds": 2.6, "gain_db": 1.5, "note": "嗤啦！横扫枭首莫沧滚落裴玄度靴前"},
            {"p": 51, "pos": "before", "slug": "crush_zifu_blood_talisman_palm", "sfx_prompt": "Jade talisman shattering into a colossal apocalyptic sky roar crushing marble pillars under third-realm pressure", "duration_seconds": 4.0, "gain_db": 2.5, "note": "轰隆隆！紫府一击血符碎裂，十丈尸煞巨掌压塌祭坛"},
        ],
    )
    j26, m26 = save_episode_scripts(s26, SCRIPTS_DIR, registry)
    built.append(("E026", j26, m26))

    # =========================================================================
    # E027 · 第27章 墟界吞血符，断刀枭裴首！ (58 paras, 16 quotes)
    # =========================================================================
    md_27 = SOURCE_DIR / "第27章_墟界吞血符，断刀枭裴首！.md"
    s27 = compile_episode_cue_sheet(
        episode_id="E027",
        chapter_number=27,
        source_md_path=md_27,
        source_rel_path=f"02_分章精修正文/{md_27.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_xujie_swallows_zifu_palm",
                "start_p": 1,
                "title": "第一幕 · 掌开归墟口，鲸吞紫府威",
                "bgm_prompt": "Titan-scale Chinese xianxia miracle soundtrack, abyssal black-hole suction roar dissolving into awe-inspiring heroic silence and rising strings, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_shatter_pei_dantian_revenge",
                "start_p": 20,
                "title": "第二幕 · 以指还彼道，一刀枭裴首",
                "bgm_prompt": "Cold relentless Chinese martial vengeance score, heavy deliberate footsteps, shattering qi-sea impact and cathartic final blade execution, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_rescue_qin_lie_walk_past_su",
                "start_p": 42,
                "title": "第三幕 · 血月虚影散，陌路不回头",
                "bgm_prompt": "Clear post-storm night sky xiao flute and warm cello of brotherhood, contrasted with bleak indifferent footsteps walking past fallen pride, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act4_chiyang_ancestor_bone_transmission",
                "start_p": 51,
                "title": "第四幕 · 骨玉传尸吼，剑指赤阳山",
                "bgm_prompt": "Terrifying ancient corpse-patriarch horror drone clashing with fearless rising dark-gold heroic war drums, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        skip_onomatopoeia_paras={7, 9, 13, 26, 29, 32, 39, 56},
        dialogue_specs=[
            {"match": "死吧！跟本公子斗，下辈子投胎长点眼", "role_id": "pei_xuandu", "tags": "[laughs] [shouting]", "stability": 0.0, "note": "裴玄度癫狂大笑"},
            {"match": "死物不入，纯灵可吞……给我进来", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "note": "陆烬高举零号铭牌张开墟界裂口鲸吞紫府血掌"},
            {"match": "不……不可能！这绝不可能", "role_id": "pei_xuandu", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "裴玄度如见鬼魅尖叫"},
            {"match": "那是赤阳老祖的紫府本命血符", "role_id": "pei_xuandu", "tags": "[crying] [shouting]", "stability": 0.0, "note": "裴玄度崩溃后退语无伦次"},
            {"match": "你用不着知道了", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬擦血欺身贴近"},
            {"match": "护身剑丸，起！", "role_id": "pei_xuandu", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "裴玄度困兽之斗吐玄阴寒光剑"},
            {"match": "别……别杀我！陆师弟，陆爷，饶我一条狗命", "role_id": "pei_xuandu", "tags": "[crying] [shouting]", "stability": 0.0, "note": "丹田被废跪地涕泪求饶"},
            {"match": "我是玄剑宗掌门亲传、赤阳老祖嫡孙", "role_id": "pei_xuandu", "tags": "[crying] [desperately]", "stability": 0.0, "note": "裴玄度磕头献宝抬出老祖威胁"},
            {"match": "二十五天前在西城陆宅，你废我气海抽我心血的时候", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬居高临下冷漠反问"},
            {"match": "你的灵石，我自己会拿。至于你的命", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "扬起断岳重刀宣判死刑"},
            {"match": "秦伯父，幸不辱命，人头取回来了", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬挑断铁钩扶住秦烈奉药"},
            {"match": "好……好小子！你爹在天之灵要是看见今晚这一刀", "role_id": "qin_lie", "tags": "[laughs] [crying]", "stability": 0.0, "note": "秦烈老泪纵横拍肩大笑"},
            {"match": "陆大哥……我的灵脉废了，裴玄度死了", "role_id": "su_qinghan", "tags": "[crying] [whispers]", "stability": 0.0, "note": "灵脉尽废的苏清寒爬在石板哀泣求收留"},
            {"match": "路是苏小姐自己选的，好自为之", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬头也不回从旁走过彻底了断"},
            {"match": "好浓郁的界外本源气息……竟能徒手吞掉本座一记尸煞掌", "role_id": "chiyang_laozu", "tags": "[angry] [hoarsely]", "stability": 0.0, "space": "memory_echo", "note": "惨白传音骨玉内赤阳老祖腐朽咆哮初现！"},
            {"match": "十八年前天渊裂谷坠落的【零号血胎】", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "memory_echo", "note": "赤阳老祖点破零号血胎放话破关活嚼"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "before", "slug": "xujie_abyss_devour_palm", "sfx_prompt": "Ancient spatial rift opening with a colossal black-hole vortex suction roar swallowing a thunderous energy blast into sudden silence", "duration_seconds": 4.2, "gain_db": 2.5, "note": "嗡轰隆！掌心墟界裂口鲸吞九成紫府尸煞血掌"},
            {"p": 26, "pos": "before", "slug": "slap_away_sword_pill", "sfx_prompt": "Heavy broadsword flat-slapping a flying sword whistling into a stone pillar", "duration_seconds": 2.2, "gain_db": 1.5, "note": "铛！断岳横拍砸飞玄阴寒光剑"},
            {"p": 29, "pos": "before", "slug": "shatter_pei_xuandu_qi_sea", "motif_id": "motif_qi_sea_shatter", "gain_db": 2.5, "note": "噗咔嚓！以彼之道还施彼身，一指震碎裴玄度筑基气海！（呼应E001母题）"},
            {"p": 32, "pos": "before", "slug": "pei_kneel_in_blood_pool", "sfx_prompt": "Heavy thud of knees collapsing into a puddle of blood on stone tiles", "duration_seconds": 2.0, "gain_db": 1.0, "note": "扑通！裴玄度重跪血泊求饶"},
            {"p": 39, "pos": "before", "slug": "behead_pei_xuandu_banner_snap", "sfx_prompt": "Razor-sharp heavy broadsword decapitation slash followed by a wooden soul-banner pole snapping and dark sky energy dispersing", "duration_seconds": 3.4, "gain_db": 2.0, "note": "嗤啦！一刀枭首裴玄度，劈断引月锁魂幡"},
            {"p": 52, "pos": "before", "slug": "skull_jade_roll_corpse_roar", "sfx_prompt": "Bone talisman rolling onto stone and igniting with eerie crimson runes and rusty metallic scraping resonance", "duration_seconds": 2.8, "gain_db": 1.0, "note": "传音骨玉滚出亮起猩红血符"},
            {"p": 56, "pos": "before", "slug": "cleave_bone_jade_shatter", "sfx_prompt": "Heavy iron blade smashing a bone talisman into flying dust on stone steps", "duration_seconds": 2.2, "gain_db": 1.5, "note": "咔嚓！反手一刀劈碎赤阳老祖传音骨玉"},
        ],
    )
    j27, m27 = save_episode_scripts(s27, SCRIPTS_DIR, registry)
    built.append(("E027", j27, m27))

    return built


if __name__ == "__main__":
    items = build_all_batch5()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if "--compile-only" not in sys.argv:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=4)
