"""Season 1 Audition Pack + Episodes E001–E003 for《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》.

Flagship 15–17 minute anti-translationese (零翻译腔) historical satirical radio drama adapted directly
from Frédéric Bastiat's 100% globally public-domain 1845–1850 essays (*Ce qu'on voit et ce qu'on ne voit pas*
and *Sophismes économiques*):
- AUDITION_BASTIAT: 1850巴黎讽刺剧核心试听包 (~1.8 min, all 8 roles, ~380 chars)
- E001: 《砸碎玻璃能救经济吗_史上最经典的破窗谬误》
- E002: 《蜡烛匠控告太阳_史上最爆笑的关税保护请愿书》
- E003: 《把铁路挖断能创就业吗_负铁路谬误与机器恐慌》
"""

from __future__ import annotations

from aigc_audio_pipeline.models import EpisodeCueSheet
from drama_helpers import act, dlg, motif, sfx


def build_audition_bastiat() -> EpisodeCueSheet:
    cues = [
        motif("ba01_window", "audition", "broken_shop_window", gap_after_s=0.22),
        dlg("ba02_narr", "audition", "narrator", "历史旁白", "[warmly] 一八五零年巴黎街头，一块值六法郎的面包店玻璃刚被砸碎，经济学史上最辛辣爆笑的议会讽刺大戏便热热闹闹拉开了帷幕。", acoustic_space="dry", gap_after_s=0.22),
        dlg("ba03_baker", "audition", "baker_bonhomme", "老博诺姆", "[earthy] [angry] 熊孩子一石头砸碎我六法郎的大玻璃，街坊还拍手夸我救活了玻璃匠——那我原本打算买新皮鞋的六法郎算谁的？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("ba04_luc", "audition", "apprentice_luc", "吕克", "[excited] 哈哈，我上午刚替大叔装完玻璃赚了六法郎，下午回鞋铺一翻账本才听说——咱鞋铺平白无故丢了一单皮鞋买卖！", acoustic_space="studio_warm", gap_after_s=0.22),
        motif("ba05_gavel", "audition", "parliament_gavel_hall", placement="overlay_next", gap_after_s=0.18),
        dlg("ba06_candle", "audition", "candle_boss", "杜邦会长", "[dramatically] 各位议员！法兰西蜡烛业正惨遭一个卑鄙外国对手零元恶意倾销——它的名字叫太阳！恳请立刻立法钉死全国所有窗户！", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("ba07_mont", "audition", "deputy_mont", "蒙托邦议员", "[condescending] 说得太妙了！最好再下令把通往波尔多的铁路故意挖断一截，客栈、马车夫和搬运工立刻全有活干，全法国一夜暴富！", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("ba08_claire", "audition", "madame_claire", "玛丽夫人", "[sarcastic] [chuckles] 照议员这套高招，我大白天钉死窗户点蜡烛织布多掏的冤枉钱，全是从女工工钱和街坊面包钱里硬抠出来的！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("ba09_su", "audition", "host_su", "苏晚星", "[curious] 巴斯夏议员，一百七十多年过去了，怎么换件现代马甲，当年您骂过的糊涂账今天照样有人拼命鼓掌叫好呢？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("ba10_bastiat", "audition", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [chuckles] 因为坏经济学家只盯眼前的明账，好经济学家才算背后的暗账！欢迎走进一八五零巴黎议会讽刺剧，咱们笑着拆穿一切歪理！", acoustic_space="studio_warm", gap_after_s=0.55),
    ]
    return EpisodeCueSheet(
        episode_id="AUDITION_BASTIAT",
        chapter_number=0,
        title="《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》核心试听包",
        mode="audition_pack",
        head_pad_s=0.35,
        tail_pad_s=1.0,
        acts=[act("audition", "1850巴黎街角与国民议会核心试听", "paris_salon_wit", bgm_duration_s=60.0)],
        cues=cues,
    )


def build_e001_broken_window() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·1850巴黎面包铺一声脆响与“零翻译腔”开场", "broken_window_alley", bgm_duration_s=75.0),
        act("act2", "第二幕·街坊欢呼“砸窗兴邦”：看得见的六法郎", "paris_salon_wit", bgm_duration_s=75.0),
        act("act3", "第三幕·黑板翻出暗账：消失的鞋匠与隐形连锁反应", "paris_salon_wit", bgm_duration_s=75.0),
        act("act4", "第四幕·如果砸玻璃能致富，不如成立“巴黎砸窗协会”", "parliament_satire_march", bgm_duration_s=75.0),
        act("act5", "第五幕·天灾、战争与好经济学家的唯一标尺", "seine_evening_clarity", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Cold open + shattered window + zero-translationese manifesto ---
        motif("b01_01", "act1", "broken_shop_window", gap_after_s=0.20),
        dlg("b01_02", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [angry] 哎哟喂！哪个小兔崽子干的好事！那可是我上个月刚花六法郎装的新玻璃，哗啦一下全成碴子了！", stability=0.0, acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_03", "act1", "narrator", "历史旁白", "[warmly] 欢迎走进《一八五零巴黎议会讽刺剧：看得见的与看不见的》。公元一八五零年七月，巴黎塞纳河畔的法棍香味还没散，老博诺姆的面包杂货铺先响起了一声清脆的破窗声。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b01_04", "act1", "narrator", "历史旁白", "[wryly] 谁也没想到，这个倒霉熊孩子随手砸碎的一块六法郎玻璃，竟然成了人类经济学史上最出名的教学道具，让法国毒舌议员弗雷德里克·巴斯夏足足嘲讽了全欧洲一百七十年。", acoustic_space="dry", gap_after_s=0.24),
        motif("b01_05", "act1", "paris_cafe_salon", gap_after_s=0.20),
        dlg("b01_06", "act1", "host_su", "苏晚星", "[curious] 巴斯夏议员，咱们先说个老实话！不少中国读者早年翻过老式学术译本，第一句“在经济领域中，一种行为所产生的效果并非单一”，听着简直像背条文，差点睡着。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_07", "act1", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 哎哟，千万别把我说得跟念经老学究似的！我当年在巴黎报馆写文章，图的就是让面包房老板、织布女工和咖啡馆酒客一边拍大腿笑喷，一边秒懂政客的鬼把戏！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_08", "act1", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 我开头那段大白话其实就一句：坏经济学家只盯着摆在眼皮底下的明账，好经济学家不光看眼前这一步，还得把藏在后头、没发生的那笔暗账全给你翻出来！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_08b", "act1", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 更扎心的是，很多糊涂政策就像庸医喂的止痛毒糖：眼前先给你一点看得见的小甜头，后头藏着一连串看不见的大苦果；而真良药，往往头一口有点苦，后头才是长久好身板！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_09", "act1", "madame_claire", "玛丽夫人", "[chuckles] [wryly] 这句痛快！明账谁不会看呀，大马路上站着都能瞧见；真正让人吃暗亏的，恰恰是账本背面那几行隐形字！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_10", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [sighs] 别光聊道理了各位，先救救我吧！我家那调皮小子一脚把铁皮球踢进了自家橱窗，我现在心疼得肝儿直颤，偏偏门口围观的街坊还在那儿说风凉话呢！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 2: Crowd cheers "broken glass stimulates economy!" ---
        sfx("b01_11", "act2", "Wooden broom briskly sweeping shattered glass fragments across Paris cobblestone pavement into a metal dustpan, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.20),
        dlg("b01_12", "act2", "deputy_mont", "蒙托邦议员", "[condescending] [warmly] 博诺姆大叔，别板着脸啦！我蒙托邦议员路过这儿，倒要向你道一声恭喜！坏事变好事嘛，这叫天降福星！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_13", "act2", "baker_bonhomme", "老博诺姆", "[earthy] [angry] 恭喜我？！议员老爷您没发烧吧？我好好一块透亮大玻璃碎成渣了，您还恭喜我？！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_14", "act2", "deputy_mont", "蒙托邦议员", "[dramatically] 格局太小了大叔！你想啊，要是谁家玻璃一百年都不碎，那城里装玻璃的师傅喝西北风去呀？大伙儿总得给人家一条活路嘛！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_15", "act2", "candle_boss", "杜邦会长", "[seriously] [warmly] 蒙托邦议员说得在理！玻璃碎了，博诺姆大叔就得掏六法郎请玻璃匠上门换新。这六法郎落进玻璃匠兜里，资金一下就流动起来啦！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_16", "act2", "deputy_mont", "蒙托邦议员", "[excited] 何止六法郎！玻璃匠赚了这六法郎，转头去买蜡烛、喝红酒、雇帮工，一环套一环，全巴黎的商业不就热火朝天转起来了吗？令郎这一脚，简直是拉动内需的小英雄！", acoustic_space="studio_warm", gap_after_s=0.24),
        sfx("b01_17", "act2", "Glass cutter scoring a fresh sheet of window glass crisply followed by putty knife smoothing sealant inside a wooden shop window frame, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.18),
        dlg("b01_18", "act2", "apprentice_luc", "吕克", "[excited] 博诺姆大叔，新玻璃给您嵌严实啦！您瞧多亮堂！不多不少正好六法郎，谢大叔关照，我这就高高兴兴揣进兜里喽！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_19", "act2", "baker_bonhomme", "老博诺姆", "[earthy] [sighs] 哎呀，听议员和杜邦会长这么一忽悠，我怎么觉得掏这六法郎还有点光荣呢？吕克笑得合不拢嘴，街坊都在夸，难不成我真做了一件造福法兰西的大善事？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_20", "act2", "host_su", "苏晚星", "[curious] 停停停！听完蒙托邦议员这番口才，我都差点跟着点头了！玻璃匠确实赚了六法郎，玻璃行业确实多了六法郎订单，这白纸黑字摆在眼前，到底哪儿不对劲呢？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_21", "act2", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [chuckles] 苏记者，你刚才看到的这一整出喜气洋洋的大戏，就是我说的第一层——“看得见的”！所有人眼睛全黏在吕克手里那六枚亮闪闪的银法郎上！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 3: The Unseen Shoemaker, Chalkboard Accounting & Hidden Ripple ---
        sfx("b01_22", "act3", "Crisp wooden chalk tapping and writing brisk figures across a cafe slate chalkboard beside clinking French silver franc coins on oak table, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("b01_23", "act3", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 别急着鼓掌，大伙儿把黑板翻到背面！我只问老博诺姆一个顶实在的问题：大叔，要不是你家小子砸了玻璃，兜里这六法郎，你原本打算下午拿去买啥？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_24", "act3", "baker_bonhomme", "老博诺姆", "[earthy] 这还用问？我脚上这双老皮鞋底子都快磨穿啦！我原本约好下午去街尾鞋铺，花六法郎定做一双崭新的小牛皮鞋，或者顺道去书摊买本新书解闷儿！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_25", "act3", "apprentice_luc", "吕克", "[gasps] [seriously] 等等大叔！街尾那家鞋铺是我亲表哥开的，我平时下午都在那儿兼职帮工啊！您今天要是把六法郎给了修玻璃的，那这双新皮鞋您还买不买啦？", stability=0.0, acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_26", "act3", "baker_bonhomme", "老博诺姆", "[earthy] [sighs] 买个锤子哟！六法郎已经塞进你修窗的围裙兜里啦！这礼拜我只好继续穿着破底皮鞋硬扛喽！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_27", "act3", "madame_claire", "玛丽夫人", "[wryly] [chuckles] 哎哟，这下全串起来了！玻璃匠这边确实多了六法郎生意，可鞋铺那边平白无故少了一单六法郎买卖！一边加六，一边减六，全巴黎总消费一分钱也没多！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_28", "act3", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 还不止交易额没多，最扎心的是实物财富！咱们把两套结局摆一块儿比一比，连三岁小孩都能一眼看明白！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_29", "act3", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 结局一，窗户没碎：老博诺姆同时拥有一块好玻璃，外加一双崭新的小牛皮鞋！玻璃匠闲着没事还能去给新盖的房子装窗户，鞋匠也赚到了六法郎。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_30", "act3", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 结局二，窗户碎了：老博诺姆只剩一块补好的玻璃，新皮鞋没影儿了！吕克上午修窗赚了六法郎，下午鞋铺丢了六法郎——全社会结结实实永久少了一双皮鞋！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_31", "act3", "apprentice_luc", "吕克", "[sighs] [seriously] 敢情折腾一大圈，我左兜刚进六法郎，右兜就飞了六法郎！外面看热闹的人只夸修窗师傅发财，压根没人替门可罗雀的鞋匠掉一滴眼泪！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_31b", "act3", "deputy_mont", "蒙托邦议员", "[sarcastic] 慢着！那我刚才说的连锁反应呢？玻璃匠拿到六法郎还会去买蜡烛买红酒，这乘数效应你总不能赖掉吧？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_31c", "act3", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 哈哈，议员您又只算了一半！要是鞋匠拿到这六法郎，难道鞋匠就不买牛皮、不买麻线、不去玛丽夫人店里扯布、不请伙计喝红酒吗？连锁反应两边完全抵消！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_32", "act3", "host_su", "苏晚星", "[excited] 太通透了！鞋匠为什么总被人忽略？因为玻璃匠拎着工具箱叮叮当当上门修窗，人人都看得见；可鞋匠丢掉的那笔订单根本没发生过，它是“看不见的”！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 4: Parliament Satire — Let's form the "Paris Window-Smashing Association"! ---
        motif("b01_33", "act4", "parliament_gavel_hall", gap_after_s=0.20),
        dlg("b01_34", "act4", "narrator", "历史旁白", "[wryly] 谁料第二天下午，巴黎国民议会大厅里，蒙托邦议员依然嘴硬不服。巴斯夏干脆使出他最拿手的绝招——顺着对手的歪理一路狂飙，直到把对方送上喜剧的顶峰。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b01_35", "act4", "deputy_mont", "蒙托邦议员", "[condescending] 巴斯夏先生，你光拿一家面包铺钻牛角尖有啥意思？宏观上讲，东西旧了坏了砸了，大家才肯掏钱换新，消费才旺嘛！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b01_36", "act4", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 蒙托邦议员真乃奇才！照您这套“破坏创造财富”的宏论，我当场替您起草一项振奋人心的议案——成立皇家巴黎砸窗协会！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b01_37", "act4", "bastiat", "弗雷德里克·巴斯夏", "[dramatically] 今晚月黑风高，咱们雇五千名壮汉，每人发一根大木棒，沿着香榭丽舍大街把全巴黎的窗户玻璃、瓷碗花瓶和马车轮子挨家挨户砸个稀巴烂！", acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("b01_37b", "act4", "Heavy wooden mallet thumping rhythmically against an oak lectern followed by hurried leather shoes scuffing across marble assembly hall tiles, pure foley, no human voice", duration_seconds=2.3, gap_after_s=0.18),
        dlg("b01_38", "act4", "deputy_mont", "蒙托邦议员", "[angry] 胡说八道！把全城家当都砸烂了，老百姓吃什么住什么？法兰西岂不立刻破产变成乞丐窝？！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("b01_39", "act4", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [chuckles] 哟呵！砸十万块玻璃让您吓得跳脚，怎么刚才砸老博诺姆一块玻璃，您还拍手大喊“拉动经济”呢？难道一桩蠢事做一次叫救经济，做一万次才算败家？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b01_40", "act4", "madame_claire", "玛丽夫人", "[chuckles] [sarcastic] 哈哈！问得蒙托邦议员脸都绿了！要是砸玻璃真能发财，杜邦会长今晚先把自家蜡烛厂大门玻璃全敲碎，明天岂不直接登顶法国首富？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b01_41", "act4", "candle_boss", "杜邦会长", "[angry] 玛丽夫人你少拿我开涮！我那玻璃镶着金边呢，砸了我上哪儿哭去！", acoustic_space="vast_hall", gap_after_s=0.20),
        dlg("b01_41b", "act4", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 甚至按议员的逻辑，半夜撬门的江洋大盗也该评劳模啦——他们逼着全城百姓花大价钱请锁匠打铁锁、修铁门，多拉动锁匠行业就业呀！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b01_41c", "act4", "apprentice_luc", "吕克", "[chuckles] [excited] 还有咱吃饭别洗碗啦，吃完饭把巴黎酒馆的白瓷盘全摔个稀碎，陶瓷厂明天肯定日夜加班、利润暴涨呢！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b01_42", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] [wryly] 诸位听见了吧？一轮到砸自家窗户、摔自家瓷碗，连最热情的保护派老板也瞬间变成理性经济学家了！因为常识只有一条：破坏永远不会凭空造出财富！", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 5: Earthquakes, Wars, Modern Echoes + Cliffhanger to E002 ---
        sfx("b01_43", "act5", "Gentle evening Paris rain tapping softly on tall cafe glass panes with warm wooden fireplace embers crackling quietly inside, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("b01_44", "act5", "host_su", "苏晚星", "[seriously] 巴斯夏议员，您别说，这个“破窗谬误”放到一百七十多年后的今天，依然天天换着西装在财经新闻里上演！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_45", "act5", "host_su", "苏晚星", "[curious] 比如每次发生大地震、大台风或者战争，总有人发评论说“灾后重建和军火订单能拉动增长”；还有些城市把刚铺好一年的好马路反复刨开重修，您怎么看？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_46", "act5", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [seriously] 全是大号破窗谬误！重建震毁的大桥，账面上看得见建筑队的繁忙订单；可看不见的，是原本能建新学校、造好机器的人力与石料，全被迫拿去填窟窿了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_46b", "act5", "host_su", "苏晚星", "[wryly] 还有打仗造炮弹也一样！炮弹炸完一地废墟，账面上的军工产值冲上了天，可造炮弹的钢铁原本能造出多少火车头、农机和医院病床，全都化作黑烟消失了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_47", "act5", "baker_bonhomme", "老博诺姆", "[earthy] 说白了，灾后重建是拼命把被老天爷砸碎的六法郎玻璃补回原样，咱顶多是努力少亏一点，绝不能把“重新修回原点”错当成“凭空多赚了一笔”！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_47b", "act5", "madame_claire", "玛丽夫人", "[warmly] 还有那些故意把好路挖开重铺的折腾劲儿，真不如省下银子给百姓修一条原本没有的新路！修回原样只是止损，凭空多出新东西才叫增长！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_48", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 博诺姆大叔和玛丽夫人已经完全毕业，可以去议会当教授了！记住我送给全人类的第一把钥匙——遇到任何天花乱坠的政策，先闭眼追问两句。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_49", "act5", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 第一句：钱明面上流进了谁的口袋？第二句：这笔钱原本是从谁兜里掏出来的，他原本打算买什么、造什么？只算第一句的是江湖术士，两句都算清的才叫明白人！", acoustic_space="studio_warm", gap_after_s=0.24),
        motif("b01_50", "act5", "candle_wax_petition", gap_after_s=0.20),
        dlg("b01_51", "act5", "apprentice_luc", "吕克", "[excited] 哎哟各位快看！杜邦会长刚从议会冲出去，带着一帮蜡烛厂老板和养牛户，正红着眼眶给一份盖满红火漆的请愿书按手印呢！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_52", "act5", "host_su", "苏晚星", "[chuckles] [curious] 让我瞄一眼标题——天呐！《蜡烛制造商、灯油商与灯芯厂致法国议会的紧急请愿书》？他们要告谁搞恶性倾销？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b01_53", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 哈哈，他们告的这个头号外国恶霸，每天早上准时从东边翻墙进巴黎，一分钱关税都不交，还免费倾销光明——它的名字叫太阳！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b01_54", "act5", "narrator", "历史旁白", "[warmly] 下一集，《蜡烛匠控告太阳：史上最爆笑的关税保护请愿书》。一场载入人类讽刺史册的巴黎议会庭审大戏，马上开庭！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E001",
        chapter_number=1,
        title="砸碎玻璃能救经济吗_史上最经典的破窗谬误",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e002_candlemakers_petition() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·一纸震惊巴黎议会的奇葩请愿书", "candle_makers_petition", bgm_duration_s=75.0),
        act("act2", "第二幕·庭审高潮：杜邦会长声泪俱下控告太阳“零元倾销”", "candle_makers_petition", bgm_duration_s=75.0),
        act("act3", "第三幕·巴斯夏归谬三连击：不如立法捆住全国人民的右手！", "parliament_satire_march", bgm_duration_s=75.0),
        act("act4", "第四幕·富足还是稀缺？玛丽夫人算清关税隐形暗账", "paris_salon_wit", bgm_duration_s=75.0),
        act("act5", "第五幕·花钱修铁路又在边境建高墙，与沉船顺差奇案", "seine_evening_clarity", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Dramatic parliamentary opening of the Candlemakers' Petition ---
        motif("b02_01", "act1", "parliament_gavel_hall", gap_after_s=0.20),
        dlg("b02_02", "act1", "narrator", "历史旁白", "[warmly] 第二夜，巴黎波旁宫国民议会大厅座无虚席。如果有人问，古往今来哪篇文章最能把“贸易保护主义”剥得只剩裤衩、笑得满堂前仰后合？答案只有一篇——巴斯夏的《蜡烛匠请愿书》。", acoustic_space="dry", gap_after_s=0.24),
        motif("b02_03", "act1", "candle_wax_petition", gap_after_s=0.20),
        dlg("b02_04", "act1", "candle_boss", "杜邦会长", "[dramatically] 尊敬的议长先生，尊敬的各位议员！今天，我代表全法兰西的蜡烛厂、煤油灯商、灯芯纺织匠、火柴厂和捕鲸船队，含泪递交这份生死存亡的紧急请愿书！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_05", "act1", "deputy_mont", "蒙托邦议员", "[seriously] [warmly] 杜邦会长请讲！咱们议会一贯旗帜鲜明：凡是外国便宜货欺负本国厂商，咱们绝对寸步不让，坚决加满关税、竖起高墙！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_06", "act1", "candle_boss", "杜邦会长", "[angry] [dramatically] 太好了！我们照明行业正惨遭一个极其无耻的外国劲敌恶意打击！它在生产光明这件事上拥有得天独厚的作弊优势，每天往巴黎街头疯狂倾销低价光明！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_07", "act1", "host_su", "苏晚星", "[curious] 哎呀，旁听席都伸长脖子了！是英国的煤气灯商，还是比利时的走私蜡烛帮？这外国恶霸到底叫啥名号？", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("b02_08", "act1", "candle_boss", "杜邦会长", "[dramatically] [shouting] 各位擦亮眼睛！只要它每天清晨一露脸，我们的蜡烛销量立刻暴跌到零！这个搞零元恶意倾销、不交一分海关税的罪魁祸首——就是天上的太阳！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("b02_09", "act1", "Heavy wooden parliamentary bench creaking abruptly followed by a porcelain inkwell rattling across an oak desk in a grand stone hall, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("b02_10", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 噗哈哈！我刚喝进嘴的一口咖啡全喷桌上了！杜邦会长，您老大半辈子造蜡烛熏糊涂了吧？您居然上议会写诉状，把老天爷挂在头顶的大太阳给告了？！", acoustic_space="vast_hall", gap_after_s=0.24),
        # --- ACT 2: Dupont's deadpan case & Montauban's hilarious backing ---
        dlg("b02_11", "act2", "candle_boss", "杜邦会长", "[seriously] 博诺姆你别笑！我句句严丝合缝！你们议会前天刚给英国铁锭、德国纺织品和瑞士奶酪加了重税，理由不就是“外国货太便宜，会抢走本国工人的饭碗”吗？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_12", "act2", "candle_boss", "杜邦会长", "[dramatically] 那我请问：英国铁锭再便宜好歹还要几法郎，太阳光呢？分文不取、免费白给！这不是世上最凶残的恶性倾销是什么？我恳请议会立刻颁布《强制封窗遮光法》！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_13", "act2", "apprentice_luc", "吕克", "[curious] 封窗遮光法？具体咋个封法呀？", acoustic_space="vast_hall", gap_after_s=0.20),
        dlg("b02_14", "act2", "candle_boss", "杜邦会长", "[dramatically] 下令全法兰西所有房子，把窗户、天窗、门缝、百叶窗、墙窟窿全拿厚木板和黑布钉死！凡是阳光能钻进来的缝隙一律查封！大伙儿从早到晚全点国产蜡烛！", acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("b02_15", "act2", "Heavy carpenter hammer driving iron nails crisply into thick oak boards sealing a wooden window frame shut one plank after another, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.18),
        dlg("b02_16", "act2", "madame_claire", "玛丽夫人", "[angry] [sarcastic] 哎哟我的妈呀！大白天好好的阳光不让晒，非逼着全巴黎躲在黑屋子里熏牛油蜡烛烟？杜邦会长，您这脑子是不是让蜡油糊住了？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_17", "act2", "deputy_mont", "蒙托邦议员", "[condescending] 玛丽夫人先别急着骂！我刚才仔细一琢磨，杜邦会长的产业链推演，居然跟咱们保护派财政部的报告一模一样，简直滴水不漏啊！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_18", "act2", "deputy_mont", "蒙托邦议员", "[excited] 诸位听这笔大账！全国白昼点蜡烛，牛油和羊油需求暴涨十倍！牧场立刻扩群多养几百万头牛羊！肉价跌了、牧草旺了、皮革多了、羊毛丰了，全法国畜牧业一飞冲天！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_19", "act2", "candle_boss", "杜邦会长", "[excited] [warmly] 还没完呢！做灯油要种海量油菜花和橄榄树，连南方的荒山都开垦成良田！做高级鲸油灯还得打造几百艘远洋捕鲸巨轮，顺手把法兰西海军水手全练出来了！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_20", "act2", "deputy_mont", "蒙托邦议员", "[dramatically] 还有巴黎的镀金烛台匠、水晶吊灯师傅、火柴工和钉窗户的木匠！光凭一条遮光法，从农田到大海、从手工作坊到高档商店，全法国人人有活干，家家数钞票！", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 3: Bastiat's deadly deadpan applause & Right-Hand Petition ---
        dlg("b02_21", "act3", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 啪啪啪！太精彩了！我巴斯夏今天破例要替杜邦会长鼓掌！各位听见没？他刚才那套话术，跟我平时在议会听到的所有“关税护国论”，连标点符号都不带改的！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_22", "act3", "deputy_mont", "蒙托邦议员", "[angry] 巴斯夏！你少阴阳怪气！给英国煤铁加关税是严肃国策，跟堵太阳哪能混为一谈？太阳光是大自然免费赏的，不一样！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_23", "act3", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [seriously] 哦？蒙托邦议员，您这句“不一样”，恰恰把自己推下了悬崖！葡萄牙阳光充足，种香橙一半靠天赐免费阳光，一半靠人工，所以卖得比巴黎温室便宜一半。", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_24", "act3", "bastiat", "弗雷德里克·巴斯夏", "[sarcastic] 您说葡萄牙香橙有一半靠免费阳光，属于不公平竞争，必须加税拦在国门外。那头顶的太阳百分之百免费，岂不是比葡萄牙香橙还要卑鄙一倍？！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_25", "act3", "host_su", "苏晚星", "[chuckles] [excited] 哈哈，绝杀！按照保护派的公式，外国货便宜一半该收五成关税，便宜九成该收九成关税，便宜百分之百的太阳光，那当然应该彻底查禁嘛！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_25b", "act3", "candle_boss", "杜邦会长", "[dramatically] 哎呀各位别误会，我杜邦也是大慈大悲的人！要是怕穷苦人家点不起蜡烛，咱们法律可以开恩——给每家屋顶偷偷留一条指头宽的缝嘛！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_25c", "act3", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 千万别留缝呀杜邦会长！您一旦心软给屋顶留了缝，太阳光不就又免费钻进来抢走您三分之一销量吗？要保护就彻底钉死，连钥匙孔都拿蜡油封住！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_26", "act3", "candle_boss", "杜邦会长", "[angry] 我不管！反正你们要是不封窗，买蜡烛的人就少，我们工人就没活干！国家发财靠的不就是大家拼命干活、增加劳动量吗？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_27", "act3", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [chuckles] 终于等来这句核心谬论啦！杜邦会长把“手段”和“目的”彻底搞反了！请问大伙儿，咱们活在世上，是为了享受光明温暖，还是为了流大汗去搓蜡烛？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_28", "act3", "bastiat", "弗雷德里克·巴斯夏", "[sarcastic] 要是“干活越费劲、用工越多”就等于国家越富，那封窗户格局也太小啦！我立刻再送议会一条更伟大的法案——请把全法国老百姓的右手全捆在背后！", acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("b02_29", "act3", "Coarse hemp rope pulling taut and knotting briskly beside a wooden tailor shears clacking clumsily on an oak table, pure foley, no human voice", duration_seconds=2.3, gap_after_s=0.18),
        dlg("b02_30", "act3", "apprentice_luc", "吕克", "[chuckles] [excited] 哈哈，把右手捆起来只准用左手干活？我左手钉鞋底慢三倍，原来我一个人干的活，现在得雇三个人！全法国失业率瞬间归零啦！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b02_31", "act3", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 没错！左手锯木头、左手烤面包、左手织棉布，人人忙得腰酸背痛、产量掉三分之二、大伙儿全都吃不饱穿不暖——按“就业至上论”，咱们岂不成了全世界最富裕的天堂？", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 4: Abundance vs Scarcity + Madame Claire's Unseen Bill ---
        motif("b02_32", "act4", "paris_cafe_salon", gap_after_s=0.20),
        dlg("b02_33", "act4", "narrator", "历史旁白", "[warmly] 哄笑声渐渐落定，玛丽夫人抱着一摞织布坊账本起身走到台前。她要帮所有普通老百姓算清杜邦会长刻意藏起来的那一半暗账。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b02_34", "act4", "madame_claire", "玛丽夫人", "[seriously] 杜邦会长，你只算了钉死窗户后，养牛户和蜡烛厂多赚了多少银子。可你有没有算过，我买这几百根蜡烛的钱是从天上掉下来的吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_35", "act4", "madame_claire", "玛丽夫人", "[angry] 我开织布坊，原本借着免费阳光织布，一年照明只要二十法郎。你把窗户钉死，我一年得多掏二百法郎买你的高价蜡烛！这多出来的二百法郎，全得从别处硬抠！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_36", "act4", "baker_bonhomme", "老博诺姆", "[earthy] 对呀！玛丽夫人多花二百法郎买蜡烛，她原本打算买我店里的新鲜黄油面包、请吕克给女工做新皮鞋、请裁缝给闺女做花裙子的钱，立马全砍没了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_37", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 精辟！杜邦会长手里那条热热闹闹的“蜡烛牛油产业链”，全是看得见的；而面包房、鞋铺、书店、裁缝店平白萎缩掉的等额订单，全是看不见的！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_38", "act4", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 更惨的是结果：用太阳光时，玛丽夫人既有光明又有新裙子；封窗点蜡烛后，大家白白耗费成千上万人的体力去造蜡烛，换回来的竟然只是老天爷原本白送的光明！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_38b", "act4", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 我在《经济谬论》里问过一个直击灵魂的问题：一个国家到底是小麦越多、布匹越多、鞋帽越多才算富，还是东西越稀缺、越贵才算富？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_38c", "act4", "madame_claire", "玛丽夫人", "[chuckles] 站在卖家的私心，每个行会老板都巴不得唯独自己卖的货全城稀缺涨价；可站在消费者的立场，全天下老百姓都盼着东西丰盛又实惠！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_38d", "act4", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 按杜邦会长的私心，明天水车行会是不是还要联名写请愿书，要求议会禁止老天下雨，好让全法国农民都高价买他们抽的井水呀？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_38e", "act4", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [warmly] 哈哈，博诺姆大叔已经青出于蓝！禁止太阳、禁止下雨、禁止便宜的外国煤铁——背后藏的都是同一套算盘：人为制造稀缺，让全体百姓替少数特权老板掏高价！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_39", "act4", "host_su", "苏晚星", "[warmly] 关税保护的秘密被彻底扒光了！它就是拿少数卖家的私心绑架全国消费者，逼大家花一百块买五十块的货，肥了一家厂，抽干了亿万百姓的钱包！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 5: The Franco-Belgian Railway Wall + Sinking Ship Trade Paradox + E003 Hook ---
        sfx("b02_39b", "act5", "Heavy wooden customs border barrier gate slamming shut with an iron padlock snapping tightly beside distant steam train wheels braking, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b02_39c", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 还有件更逗的真事！法国和比利时刚花了上亿法郎穿山架桥修铁路，就为了让两国煤铁和棉布省运费、快通商。结果铁路一通，蒙托邦他们赶紧在边境盖起高关税海关！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_39d", "act5", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哈哈，前脚花上亿把运费压低十法郎，后脚在国境线上加十法郎关税把价钱涨回去！那您老干嘛修铁路呀，留着荒山野岭不省钱多了？", acoustic_space="studio_warm", gap_after_s=0.24),
        sfx("b02_40", "act5", "Heavy ocean waves crashing against a wooden merchant hull with creaking masts and heavy timber cargo crates sliding across wet deck planks, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("b02_41", "act5", "deputy_mont", "蒙托邦议员", "[sarcastic] 哼，巴斯夏，就算太阳这局我认栽！可国际贸易上，出口多、进口少，叫“贸易顺差”，那总归是法国大赚特赚吧？要是进口货比出口货值钱，咱们不就吃大亏了吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_42", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 蒙托邦议员又送来一道送分题！波尔多商人装了一船值五万法郎的法国红酒运去美国，卖出七万法郎，再买回一船棉花，运回法国卖了九万法郎。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_43", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 海关账本一记：出口五万，进口九万——按您的算法，这叫四万法郎巨额“逆差”，咱们亏惨了对吧？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b02_44", "act5", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哪儿亏了呀！商人拿五万块红酒换回九万块棉花，净赚四万法郎，乐得晚上睡觉都要笑醒！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b02_45", "act5", "bastiat", "弗雷德里克·巴斯夏", "[sarcastic] [chuckles] 可您瞧另一艘船！同样装了五万法郎红酒驶出港口，刚进英吉利海峡就撞上暗礁，连船带酒咕嘟咕嘟全沉海里了！海关账本一记：出口五万，进口零蛋！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_46", "act5", "madame_claire", "玛丽夫人", "[chuckles] [sarcastic] 哎哟天呐！出口五万进口为零，按照“顺差等于发财”的算盘，这艘沉到海底喂鱼的倒霉商船，居然给法兰西创造了整整五万法郎的超级顺差？！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_47", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [solemn] 哈哈，要是送出去才算赚、买进来算吃亏，干脆货船一离港就凿沉得了！做买卖的目的从来不是白白送货，而是用咱们的长处，换回百姓更划算的好日子！", acoustic_space="studio_warm", gap_after_s=0.24),
        motif("b02_48", "act5", "rail_track_pickaxe", gap_after_s=0.20),
        dlg("b02_49", "act5", "apprentice_luc", "吕克", "[curious] 咦？外面怎么叮叮当当响起铁镐砸铁轨的声音了？法国不是正在热火朝天修巴黎通往波尔多和马德里的大铁路吗？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b02_50", "act5", "deputy_mont", "蒙托邦议员", "[condescending] 没错！我刚向议会交了一份天才提案——到了波尔多，故意把铁轨挖断一截！顺便再把玛丽夫人厂里那台抢饭碗的新织布机给砸了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b02_51", "act5", "narrator", "历史旁白", "[warmly] 下一集，《把铁路挖断能创就业吗：负铁路谬误与机器恐慌》。把路修通居然不如把路挖断？巴斯夏再掀爆笑狂潮，咱们下回见！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E002",
        chapter_number=2,
        title="蜡烛匠控告太阳_史上最爆笑的关税保护请愿书",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e003_negative_railroad_machines() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·波尔多“断头铁路”奇案：故意添堵真能发财？", "parliament_satire_march", bgm_duration_s=75.0),
        act("act2", "第二幕·巴斯夏献策“负铁路”与鲁滨逊扔掉钢锯的笑话", "broken_window_alley", bgm_duration_s=75.0),
        act("act3", "第三幕·织布坊风暴：新织布机来了，吕克和工匠慌了神", "paris_salon_wit", bgm_duration_s=75.0),
        act("act4", "第四幕·省下一千法郎去哪了？机器抢饭碗的隐形暗账", "paris_salon_wit", bgm_duration_s=75.0),
        act("act5", "第五幕·用茶匙舀沙子、AI 焦虑与转行阵痛的温度", "seine_evening_clarity", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: The Bordeaux railroad break proposal ---
        motif("b03_01", "act1", "rail_track_pickaxe", gap_after_s=0.20),
        dlg("b03_02", "act1", "narrator", "历史旁白", "[warmly] 第三夜，十九世纪中叶的法国正迎来蒸汽铁路时代。巴黎通往波尔多、直抵西班牙马德里的铁轨正在一寸寸铺开。可就在法国议会里，竟然真有人一本正经提出了一个让人下巴掉地的提案。", acoustic_space="dry", gap_after_s=0.24),
        motif("b03_03", "act1", "parliament_gavel_hall", gap_after_s=0.20),
        dlg("b03_04", "act1", "deputy_mont", "蒙托邦议员", "[dramatically] 诸位同仁！这条巴黎到西班牙的大铁路，修到波尔多城外时，千万不能直接接通！我郑重提议：咱们得在波尔多故意留一段断轨，让南北两段铁轨尺寸不一样！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_05", "act1", "host_su", "苏晚星", "[gasps] [curious] 哎哟！这可不是编段子吧？历史上法国议会里居然真有人提议故意把自家铁路修断？！议员先生，您图啥呀？", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_06", "act1", "deputy_mont", "蒙托邦议员", "[condescending] 苏记者你太嫩啦！你想想，如果火车呼啸一声直接穿城而过，波尔多老百姓能捞着半个铜板吗？留一段断轨就不一样啦！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_07", "act1", "deputy_mont", "蒙托邦议员", "[excited] 火车一到波尔多停下，乘客得下车住客栈、吃大餐；成吨货物得卸下来，雇搬运工扛肩上、雇马车夫拉到城南车站再重新装车！搬运工、旅店老板、马夫、车轮匠全发财！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_08", "act1", "candle_boss", "杜邦会长", "[warmly] 高明！实在是高明！波尔多旅店晚上点蜡烛，我这蜡烛销量又能蹭蹭往上涨！这叫盘活地方服务业！", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("b03_09", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [wryly] 哎哟喂，听着怎么这么耳熟呢？这不就是把砸我家玻璃的法子，升级成砸全国铁轨了吗？！", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("b03_09b", "act1", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [chuckles] 大叔眼尖！蒙托邦议员这叫“把受罪当功劳”！一个人赶大马车一小时运一百袋面粉，另一个人倒着爬一天扛一袋，照议员的算法，倒着爬那位才该颁勋章呢！", acoustic_space="vast_hall", gap_after_s=0.24),
        # --- ACT 2: Bastiat invents "The Negative Railroad" & Robinson Crusoe's Saw ---
        dlg("b03_10", "act2", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 蒙托邦议员，您还是太保守、太抠门了！只在波尔多挖断一次铁轨，才养活几个搬运工和马夫？格局没打开啊！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_11", "act2", "deputy_mont", "蒙托邦议员", "[curious] 哦？巴斯夏难得赞同我一回！那依你的高见，该怎么改？", acoustic_space="vast_hall", gap_after_s=0.20),
        dlg("b03_12", "act2", "bastiat", "弗雷德里克·巴斯夏", "[dramatically] [sarcastic] 干脆在奥尔良挖断一次，图尔再挖断一次，普瓦捷、昂古莱姆统统挖断！甚至每隔十公里就故意把铁轨拆成烂泥坑！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_13", "act2", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 这样每一趟客货都得上下折腾五十回，沿途每个小村子都能盖满客栈、养满搬运工！我给这项伟大工程起个学名——就叫“负铁路”！", acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("b03_14", "act2", "Wooden carriage wheels jolting noisily through thick muddy potholes and rocky gravel ruts with wooden crates clattering heavily, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b03_15", "act2", "madame_claire", "玛丽夫人", "[chuckles] [sarcastic] 噗哈哈！“负铁路”——别人修铁路是为了省时间、省运费、扫清障碍；议员您修铁路是专门为了给人添堵、制造障碍！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_16", "act2", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 话糙理不糙！咱们往深处剥一层：波尔多搬运工多挣的每一法郎运费，全是从旅客和货主钱包里生生挤出来的！货价一涨，全法国买酒买布的百姓都变穷了！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_17", "act2", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 更荒唐的是，要是故意制造麻烦真能创造财富，那咱们修什么大路、架什么石桥？干脆把塞纳河上的桥全炸了，大伙儿天天雇船夫划桨摆渡，岂不创造十倍就业？", acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("b03_17b", "act2", "Crisp steel hand saw slicing cleanly through a sturdy pine plank beside gentle ocean surf lapping on a sandy island shore, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b03_17c", "act2", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 我给大伙儿讲个鲁滨逊的笑话！荒岛上的鲁滨逊，原来拿小石刀削一块木板得苦干整整十五天。忽然海浪冲上来一把好钢锯，两小时就能锯出一块平整木板！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_17d", "act2", "bastiat", "弗雷德里克·巴斯夏", "[sarcastic] 请问蒙托邦议员，要是您漂流到那座荒岛，会一把抢过鲁滨逊的钢锯扔回大海，大喊“千万别用锯子，它会抢走你整整十四天的宝贵工作时间”吗？！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_17e", "act2", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哈哈哈哈！鲁滨逊肯定拿木板把他撵海里去！省下十四天工夫，鲁滨逊能多盖间茅屋、多编张渔网、多抓十条大鱼呀！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_17f", "act2", "deputy_mont", "蒙托邦议员", "[angry] 哼，荒岛上只有鲁滨逊孤家寡人一个，咱们法兰西有几千万人口，哪能拿孤岛打比方！", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("b03_17g", "act2", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 社会说穿了，不就是几千万个互相换东西的鲁滨逊吗？一个人把钢锯扔海里叫犯傻，难道几千万人一块儿把钢锯和火车全扔海里，就变成高深国策啦？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b03_18", "act2", "host_su", "苏晚星", "[warmly] 哈哈，瞬间看穿一切故意设卡、层层盖章、人为添堵的奇葩规矩！每多设一道没必要的门槛，眼前养活了几个收费的，背后拖垮的是整个社会的活力！", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 3: Machine Panic at Madame Claire's Weaving Shop ---
        sfx("b03_19", "act3", "Crisp fast mechanical wooden flying-shuttle power loom clacking smoothly and rapidly inside a bright 1850 Parisian textile workshop, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("b03_20", "act3", "narrator", "历史旁白", "[warmly] 离开喧闹的议会，众人来到玛丽夫人的织布坊。作坊正中刚搬进一台叮当作响的新式省力织布机，门口却剑拔弩张——这正是十九世纪席卷全欧洲的“机器恐慌”。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b03_21", "act3", "apprentice_luc", "吕克", "[angry] [sighs] 玛丽夫人，巴斯夏先生，铁路我算服了，可这台铁疙瘩机器我实在怕得慌！我邻居皮埃尔原本靠手工织布养家，现在这机器一个人顶俩，他下个月就要失业了呀！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_22", "act3", "candle_boss", "杜邦会长", "[dramatically] 看见没有！机器就是吃人的铁怪兽！今天机器抢织布工的饭碗，明天机器抢鞋匠的饭碗，后天抢面包师的饭碗！赶紧立法砸机器、禁机器，保住大伙儿工作！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_23", "act3", "madame_claire", "玛丽夫人", "[wryly] [seriously] 杜邦会长别光站着喊口号！以前织十匹好布，我得雇两个人忙活一个月，光工钱就两千法郎，布价贵得街坊买不起；换了新机器，一个人就能织出同样十匹好布！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_23b", "act3", "deputy_mont", "蒙托邦议员", "[condescending] 瞧！你亲口承认少雇了一个人！假如全法国所有行业都用上省力机器，一半工人岂不全得流落街头讨饭吃？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_24", "act3", "host_su", "苏晚星", "[pushback] 等等巴斯夏议员！我替今天担心人工智能和自动化抢饭碗的听众问一句实在话：吕克邻居皮埃尔失业了，这是千真万确的吧？机器省下人力，难道不会让越来越多人没饭吃吗？", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 4: The Unseen 1,000 Francs — Where do new jobs come from? ---
        sfx("b03_25", "act4", "Heavy crisp scissors slicing through smooth woven cotton cloth followed by silver franc coins clinking neatly into two separate piles on an oak counter, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b03_26", "act4", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [seriously] 这个问题问到灵魂深处了！来，咱们把老规矩拿出来——盯着“看得见的”，更要追踪“看不见的”那一千法郎去了哪儿！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_27", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 假设老博诺姆每年要买一大批布给伙计做围裙，过去手织贵得要命，他得掏两千法郎养活两名织布工。如今玛丽夫人用上新机器，只要雇一名工人就能织出同样多的布。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_28", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 同行们也纷纷用上机器，布价嗖地降了一半！老博诺姆今年买同样多的布，只花了以前一半的钱——他兜里平白省下整整一千法郎！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_29", "act4", "baker_bonhomme", "老博诺姆", "[earthy] [excited] 哎哟，兜里白多出一千法郎！那我肯定不会拿火柴把它烧了取暖呀！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b03_30", "act4", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 问得好！大叔，你拿着买布省下来的这一千法郎，会拿去干啥？", acoustic_space="studio_warm", gap_after_s=0.20),
        dlg("b03_31", "act4", "baker_bonhomme", "老博诺姆", "[earthy] 给全家每人添两双吕克做的好皮鞋、找木匠把面包房柜台翻新、再买两排好书架、顺便多买些鲜牛奶和水果！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_32", "act4", "apprentice_luc", "吕克", "[gasps] [excited] 慢着！我脑子嗡地亮了！老博诺姆把买布省下的一千法郎，全花在了鞋铺、木匠铺和奶农手里！那边订单暴涨，立马就要多招新伙计！", stability=0.0, acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_32b", "act4", "deputy_mont", "蒙托邦议员", "[sarcastic] 哼！那要是玛丽夫人刚开始咬死不降布价，把省下的一千法郎自己揣进腰包呢？老博诺姆一分钱也没省下来呀！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_32c", "act4", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [warmly] 问得好！就算头半年玛丽夫人暂时多赚了一千法郎利润，她照样会把钱拿去扩厂房、买新机、请木匠或者存银行！这笔钱同样流回市场雇人——而且同行很快跟进竞争，最后红利稳稳落进全城百姓兜里！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_33", "act4", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [seriously] 完全正确！织布坊裁下来那名工人是“看得见的”，可省下的一千法郎在鞋匠、木匠、印刷工和造机器工厂里催生出来的新需求和新岗位，是“看不见的”！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_34", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 账面上劳动总量并没消失，只是挪了窝；而最神奇的是结果——以前全社会忙活两份工，只换来十匹布；现在同样两份工，换来了十匹布，外加新皮鞋、新柜台和新鲜牛奶！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_35", "act4", "madame_claire", "玛丽夫人", "[excited] 还不止呢！因为布价便宜了一半，以前穿不起新棉衣的穷苦人家，现在人人买得起三件新衣裳！织布总销量翻了三倍，我明年反而得再多招五个女工呢！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_35b", "act4", "baker_bonhomme", "老博诺姆", "[earthy] 对呀！还有造这台新织布机的铁匠、铜匠、画图纸的技师和每天上门保养的维修工——机器自己可不会从石头缝里蹦出来，光伺候机器就养活了一大片新行当！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_36", "act4", "host_su", "苏晚星", "[warmly] 就像当年印刷机淘汰了手工抄书匠，结果书价大跌，识字读书的人暴涨百倍，后来出版、报业和书店养活的人，比从前的抄书匠多出一百倍还不止！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 5: Digging with Teaspoons + AI Echo + Honest Compassion for Transition Pain ---
        sfx("b03_37", "act5", "Tiny metal teaspoon scraping comically against dry coarse gravel and dirt beside a sturdy iron shovel slicing cleanly into soil, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("b03_38", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 咱们再把反对机器的歪理推到头试试！如果省力气的织布机该砸，那省力气的铁犁是不是也该砸？铁锹也该砸？干脆发给全国人民一人一把小茶匙去刨地挖运河吧！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_39", "act5", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哈哈！拿小茶匙挖运河，那连七十岁老太太都得下地干活，十万年也挖不通！全巴黎人人忙得吐血，结果连个黑面包都吃不上！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_40", "act5", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 所以记住这条颠扑不破的常识：人类干活不是为了受累，而是为了过上好日子。用更少汗水造出更多好东西，这叫文明进步，绝不叫灾难！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_40b", "act5", "host_su", "苏晚星", "[warmly] 一百七十年后的今天，从拖拉机、电脑到人工智能，大家每逢新技术照样提心吊胆。可人类从来没把欲望满足完——旧苦力省出来的人手，全流向了教育、医疗、影音、设计和无数全新行业！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_41", "act5", "apprentice_luc", "吕克", "[sighs] [softly] 巴斯夏先生，大道理我都服气了。可我还是心疼邻居皮埃尔——他织了二十年手工布，突然被机器顶掉，短时间里他一家老小怎么熬过换行的难关呢？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_42", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [solemn] 吕克，你有这份热心肠，才是真君子！我从来不否认技术换代会给老手艺人带来真实的短期阵痛。咱们该做的，是帮皮埃尔学新机器操作、学新行当，帮他平稳渡过难关。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_43", "act5", "bastiat", "弗雷德里克·巴斯夏", "[solemn] 咱们要救助的是转行的人，绝不是去保卫落后的旧铁锤！为了照顾一个人继续手工抄书，就砸掉全人类的印刷机，那是拿全世界的贫困做陪葬！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_44", "act5", "madame_claire", "玛丽夫人", "[warmly] 吕克放心！皮埃尔懂纱线、懂布纹，我下周正缺个照看新织布机调线的领班，工钱比他从前还涨两成，你这就叫他来报到！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_44b", "act5", "apprentice_luc", "吕克", "[excited] [warmly] 真的吗玛丽夫人？！那我这就飞奔去给皮埃尔报喜，顺便让大伙儿瞧瞧，新机器根本不是抢饭碗的怪兽，是帮大伙儿少弯腰、多挣钱的好帮手！", acoustic_space="studio_warm", gap_after_s=0.24),
        motif("b03_45", "act5", "seine_quill_clock", gap_after_s=0.20),
        dlg("b03_46", "act5", "deputy_mont", "蒙托邦议员", "[sarcastic] 哼，算你们今天嘴皮子利索！可明天议会要表决裁减十万冗兵冗员、砍掉大剧院财政补贴——这下全巴黎少了一亿法郎公家大单，我看你巴斯夏还怎么圆！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_47", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 哟，蒙托邦议员总算亮出压箱底的大招了——“政府花钱救市场”！明晚咱们就拎个大水桶，当众拆穿“从水桶左边舀水倒进右边”的财政魔术！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b03_48", "act5", "narrator", "历史旁白", "[warmly] 下一集，《裁军与铁饭碗：政府养闲人为什么没增加总需求》。强盗抢钱请客算不算拉动消费？敬请期待！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E003",
        chapter_number=3,
        title="把铁路挖断能创就业吗_负铁路谬误与机器恐慌",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )
