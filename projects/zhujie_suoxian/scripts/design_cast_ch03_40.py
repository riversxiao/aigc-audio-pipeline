from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, "/home/antigravity/riversxiao/aigc-audio-pipeline/src")
from aigc_audio_pipeline.elevenlabs_client import ElevenLabsClient

OUT_DIR = Path("/shared/user/.gemini/config/zhujie_suoxian_audio/01_声线试听小样/voice_design_ch03_40_candidates")
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = Path("/shared/user/.gemini/config/zhujie_suoxian_audio/.cache")

DESIGN_SPECS = [
    {
        "role_id": "chu_xiazi",
        "voice_name": "诸界锁仙_褚瞎子_黑市盲眼怪医",
        "description": "中国大陆标准普通话老年性格男声，六十岁古风江湖老药师，嗓音干瘦沙哑、略带市井世故与深藏不露的沧桑通透感，语速慢条斯理，咬字地道自然，极具古装广播剧辨识度，严禁外国口音或港台腔。",
        "sample_text": "嘿，客人脾气倒不小。老山白芨、陈年血竭、三钱铁线草，原本全是寻常药铺里的普通草药，可里头这一丝清润如初雪的药引子，当真是三百年罕见的古法手笔！拿着这块九字乌木牌，往后初一十五直接走后巷找老头子便是。"
    },
    {
        "role_id": "qin_lie",
        "voice_name": "诸界锁仙_秦烈_铁血独眼老将",
        "description": "中国大陆标准普通话中年硬汉男中低音，四十五岁上下，久经沙场的边军老将军与重刀客，嗓音粗粝豪迈、中气十足、金石铿锵，带着风雪烈酒的粗豪豪气与重情重义的真性情，纯正大陆影视配音质感。",
        "sample_text": "像，太像了！方才校场上那记叠浪回腕刀，我隔着五十丈一眼就认出来了，除了陆擎苍那位豪杰，北渊城没人使得出这么干净利落的刀法！这把重达六十四斤的断岳宝刀我替你爹守了整整三年，今日总算物归原主了！"
    },
    {
        "role_id": "lu_qingcang",
        "voice_name": "诸界锁仙_陆擎苍_沧桑威严慈父",
        "description": "中国大陆标准普通话醇厚威严中年男低音，四十二岁，北渊第一重刀宗师兼慈父，声线深沉稳重如高山磐石，既有孤身远行的悲壮决绝，又饱含对独子深沉内敛的慈爱嘱托，纯正大陆古装电影级配音。",
        "sample_text": "烬儿，当你打开这只铁匣时，说明你凭自己的毅力走出了真正的古修之路，为父总算没白挂心这十五年。这羊皮图上标着极北天渊外围黑风最薄的一道裂口，你若有一日修成气候，切记守心闭识，莫信虚妄幻象！"
    },
    {
        "role_id": "hongxiu_louzhu",
        "voice_name": "诸界锁仙_红袖楼主_慵懒锋芒御姐",
        "description": "中国大陆标准普通话成熟古风女中音，三十二岁左右，仙侠剧商会女楼主，嗓音慵懒磁性、雍容华贵、胸有城府，轻笑间从容大气又暗藏果决威严，严禁甜腻音色与任何外国口音，纯正大陆影视级女声。",
        "sample_text": "不必麻烦了，这两瓶上品凝髓散，本座替鬼樊楼全收了，账房多支二十枚灵石给这位先生交个朋友。持此玄客令入楼，买卖抽成减半，先生往后若还有这等清润古药，尽管来找本楼，守信重诺四个字我们还是担得起的。"
    },
    {
        "role_id": "shi_meng",
        "voice_name": "诸界锁仙_石猛_憨直蛮力铁匠少年",
        "description": "中国大陆标准普通话粗犷浑厚青年男声，二十岁高大铁匠青年，嗓音瓮声瓮气、实在憨厚、充满千斤气力与滚烫赤诚，说话直爽洪亮、中气充沛，地道大陆北方质朴青年戏剧配音质感，严禁文弱书生腔。",
        "sample_text": "恩公大恩大德，俺石猛这辈子都记在心里！俺从小跟着爹在铁匠铺拉风箱抡大锤，别的巧心思没有，就是有一把子使不完的力气！白鹤药庄和福爷爷交给俺守着，俺一定日夜苦练这门锻骨劲，等恩公将来从北边平安归来！"
    },
    {
        "role_id": "chiyang_laozu",
        "voice_name": "诸界锁仙_赤阳老祖_枯朽阴森尸煞老怪",
        "description": "中国大陆标准普通话苍老低沉反派男低音，七十五岁古典仙侠剧闭关老祖角色，嗓音沙哑枯槁、低频共鸣深重威严，透着阴冷沧桑与居高临下的压迫感，字正腔圆，纯正大陆顶级古装仙侠戏剧配音。",
        "sample_text": "好浓郁的太古本源气息，区区筑基小辈，竟能接下本座隔空一掌而不退半步！大苍九州修行三千载，紫府圆满便是凡俗极境，尔等井底之蛙又岂知金丹大道的艰难险阻！天渊古路已开，谁也休想拦住本座问鼎仙途！"
    },
    {
        "role_id": "li_cang",
        "voice_name": "诸界锁仙_厉苍_铁血冷酷刑堂执事",
        "description": "中国大陆标准普通话冷峻威严中年男中低音，四十五岁古典武侠仙侠剧宗门戒律堂执事，声音低沉硬朗、严肃冷酷、气场凌厉，带着审视与威慑感，咬字清晰有力，地道大陆古装正剧男配音。",
        "sample_text": "苏二长老，这便是你说卧病不起的陆家后人？看你院中这座玄磁古阵布置得严丝合缝，令尊当年从极北带回来的秘卷果然留在祠堂之中。本执事奉宗门法旨前来查验，识时务者速速撤去阵法，莫要自误前程！"
    },
    {
        "role_id": "zhao_kui",
        "voice_name": "诸界锁仙_赵魁_阴鸷低哑暗桩死士",
        "description": "中国大陆标准普通话低哑冷冽中年男声，三十八岁古典武侠剧夜行密探角色，嗓音压抑粗糙、气息深沉短促、带着几分冷笑与机警试探感，地道大陆影视剧性格男配音，严禁朗诵腔与外国口音。",
        "sample_text": "西城这座老宅子静得有些反常，三更梆子刚响，廊下连半点灯火气都没有。上面交代下来要亲自验看清楚虚实才能回禀复命，这屏风后头的呼吸声不对劲，莫非是在这灵堂里设下了什么诱敌入瓮的障眼法不成？"
    },
    {
        "role_id": "su_mu",
        "voice_name": "诸界锁仙_苏牧_势利刻薄世家官僚",
        "description": "中国大陆标准普通话傲慢清冷青年男声，二十六岁古装剧世家公子兼衙门统领角色，嗓音清亮却带着官威傲气与讥诮疏离感，居高临下、言辞犀利，纯正大陆古装权谋剧青年男配音。",
        "sample_text": "镇渊司乃朝廷选拔精锐的重地，讲究的是真才实学与沙场刀法！镇渊司大律写得明明白白，三刀之内能在青刚试力石上留痕三寸者方入甲等。来人，把校场内那块测试军校气力的两千斤黑铁重碑抬上来验看！"
    },
    {
        "role_id": "a_mang",
        "voice_name": "诸界锁仙_阿盲_凄楚坚韧盲眼少女",
        "description": "中国大陆标准普通话清澈柔韧青年女声，二十岁专业女性配音演员演绎古风清纯坚韧的寒门女子，嗓音干净空灵、微带凄楚颤音却充满守护家人的倔强骨气，情感细腻动人，纯正大陆古风广播剧女声。",
        "sample_text": "多谢恩公大德，救下我们全族老小！阿爷常说山谷上面只有令人畏惧的暗红乌云，可今夜落在咱们脸庞上的漫天星辉，却是这样清凉柔和、干干净净的！恩公此去北方路途遥远，还请收下这块平安石，一路珍重！"
    },
    {
        "role_id": "sect_elder_antagonist",
        "voice_name": "诸界锁仙_宗门长老_跋扈苍劲老修",
        "description": "中国大陆标准普通话威严苍劲老年男低音，六十二岁古典仙侠剧名门大长老角色，嗓音洪亮雄浑、盛气凌人、老成持重又刚烈暴躁，发号施令时气势如虹，地道大陆仙侠剧高阶长老声线。",
        "sample_text": "大胆狂徒，竟敢声东击西惊扰后山重地！区区一座迷雾困阵也想拦住老夫的二阶青芒飞剑么？众内门弟子听令，速速依方位结成伏魔剑阵稳住阵脚，随老夫一鼓作气破开西林迷雾，务必在子时之前查明底细！"
    },
    {
        "role_id": "snobbish_steward_npc",
        "voice_name": "诸界锁仙_世家管事_油滑市侩中年",
        "description": "中国大陆标准普通话圆滑世故中年男声，四十八岁古装剧大宅门总管事与远房亲戚角色，嗓音活泛有戏感，说话慢条斯理、皮笑肉不笑、前倨后恭极富戏剧张力，地道大陆古装性格配角声线。",
        "sample_text": "哎呀呀，大侄子气色看着可比外头传言的好太多了！自家人关起门来说句亮话，明日正午便是府上老太爷六十整寿，前厅特意留了一张席面，我今天专程过来送这张烫金寿帖，这礼数可是一分都没落下呀！"
    },
    {
        "role_id": "weathered_elder_npc",
        "voice_name": "诸界锁仙_沧桑老丈_古道边塞老者",
        "description": "中国大陆标准普通话沧桑朴实老年男声，六十五岁边塞守碑老兵与民间老掌柜，嗓音温和厚道却带着岁月风霜与沙砾质感，语气诚恳悲悯、真实自然，严禁与哭腔撞音，纯正大陆老戏骨配音感。",
        "sample_text": "当年陆爷在北渊城里是何等光明磊落的人物，快把麻布拿回去罢，几文铜板下个月再结也不迟。老汉我在这北境古道守了四十年界碑，三年前风雪夜也见过那位背重刀的壮士歇脚，后生，前路风急，千万保重啊！"
    },
]

ENSEMBLE_LIB_TESTS = [
    ("ancient_construct_echo", "vBK1ICucZ4f5G7wjYUBd", "WangSong", "[coldly] 检测到母晶受损……锁定十丈禁界闯入活体……执行上使死令，抹杀！", 1.0),
    ("male_guard_captain", "pz7hOfW7kgI9kF818eDS", "Jerry", "[calmly] 气血浑凝，刀走毫厘，三叠寸劲不散。此子虽无丹田灵气，外门刀术已入一流，当评上上甲等！", 0.5),
    ("male_disciple_a", "5s3UifUu3OJ90z17rRMA", "Jun", "[shouting] 周头儿救命！左边黑影里又有噬影夜魔扑上来了，我的骨火符烧不死它！", 0.0),
    ("male_disciple_b", "lkK6X9yp6sIA3vecwS2p", "Hou Xiaohou", "[crying] 我不修了！他们把周师兄和林师姐都抽干骨髓做药渣了，我不要变成干尸！", 0.0),
    ("female_maid_npc", "GE494ib77Hxb5fJC33Ib", "Kathy", "[softly] 周执事尽管放心，我家小姐今早已经搬进寒玉峰城外别院静修了，这株冰髓草是裴公子特意吩咐买的。", 0.5),
    ("eternal_night_whisper", "t5SIDRTVMdbNUqrSAycs", "Linda", "[whispers] 好黑啊……为什么你不点灯……把你的眼珠子抠出来点着吧……留下来陪我们吧……", 0.0),
]

for sp in DESIGN_SPECS:
    if len(sp["sample_text"]) < 108:
        sp["sample_text"] += "此事关系重大，切莫走漏半点风声，咱们按规矩行事便是。"
    assert 20 <= len(sp["description"]) <= 1000, sp["role_id"]
    assert 100 <= len(sp["sample_text"]) <= 1000, f"{sp['role_id']}: {len(sp['sample_text'])}"

client = ElevenLabsClient(cache_dir=CACHE_DIR)

def run_one_design(spec):
    rid = spec["role_id"]
    rdir = OUT_DIR / rid
    meta_cache = rdir / "_design_result.json"
    if meta_cache.is_file():
        return rid, json.loads(meta_cache.read_text(encoding="utf-8"))
    previews, txt = client.design_voice_previews(
        voice_description=spec["description"],
        sample_text=spec["sample_text"],
        output_dir=rdir,
        filename_prefix=rid,
        loudness=0.5,
        guidance_scale=6.5,
    )
    payload = {
        "role_id": rid,
        "voice_name": spec["voice_name"],
        "description": spec["description"],
        "sample_text": txt,
        "candidates": [
            {
                "cand": i + 1,
                "generated_voice_id": p.generated_voice_id,
                "mp3_path": str(p.mp3_path),
                "wav_path": str(p.wav_path),
                "duration_s": p.duration_s,
                "language": p.language,
            }
            for i, p in enumerate(previews)
        ],
    }
    meta_cache.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rid, payload

summary = {"designed": {}, "ensemble_lib": {}}

with ThreadPoolExecutor(max_workers=3) as pool:
    futs = {pool.submit(run_one_design, sp): sp["role_id"] for sp in DESIGN_SPECS}
    for fut in as_completed(futs):
        rid = futs[fut]
        try:
            _, res = fut.result()
            summary["designed"][rid] = res
            print(f"[DESIGNED] {rid}: {len(res['candidates'])} candidates", flush=True)
        except Exception as exc:
            print(f"[ERROR] {rid}: {exc}", flush=True)

ens_dir = OUT_DIR / "_ensemble_lib_tests"
ens_dir.mkdir(parents=True, exist_ok=True)
for rid, vid, vname, text, stab in ENSEMBLE_LIB_TESTS:
    wav_p = ens_dir / f"{rid}_{vname}.wav"
    mp3_p = ens_dir / f"{rid}_{vname}.mp3"
    sr = client.synthesize_dialogue(voice_id=vid, text=text, output_wav=wav_p, stability=stab, similarity_boost=0.85, language_code="zh")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav_p), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3_p)], check=True)
    summary["ensemble_lib"][rid] = {
        "role_id": rid,
        "voice_id": vid,
        "library_voice_name": vname,
        "mp3_path": str(mp3_p),
        "wav_path": str(wav_p),
        "duration_s": round(sr.duration_s, 3),
    }
    print(f"[ENSEMBLE] {rid} ({vname}): {sr.duration_s:.2f}s", flush=True)

manifest_p = OUT_DIR / "ch03_40_casting_candidates_manifest.json"
manifest_p.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Saved manifest to {manifest_p}")
