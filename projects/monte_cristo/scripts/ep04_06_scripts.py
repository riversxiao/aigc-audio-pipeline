"""Season 1 Episodes E004–E006 for《基督山伯爵·伊夫堡复仇广播剧》.

Flagship 15–20 minute cinematic radio drama full editions (~3,100–3,500 CJK chars, ~62–76 cues each):
- E004: 《巴黎假面盛宴_奥特伊毒屋与海黛公主血证》
- E005: 《玫瑰毒影与金融风暴_维尔福崩塌与唐格拉尔破产》
- E006: 《罗马地窟天价烤鸡与尾声_等待和希望》
"""

from __future__ import annotations

from aigc_audio_pipeline.models import EpisodeCueSheet
from drama_helpers import act, dlg, motif, sfx


def build_e004_paris_mask_haydee() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·惊马救美立威与莫尔塞夫沙龙重逢", "paris_venetian_revenge", bgm_duration_s=75.0),
        act("act2", "第二幕·奥特伊毒屋夜宴与栗树坑惊魂", "conspiracy_tavern_shadow", bgm_duration_s=75.0),
        act("act3", "第三幕·贵族院公开审判与海黛泣血铁证", "paris_venetian_revenge", bgm_duration_s=75.0),
        act("act4", "第四幕·梅尔塞苔丝深夜泣求与决斗场醒悟", "wait_and_hope_epilogue", bgm_duration_s=75.0),
        act("act5", "第五幕·书房卸面现真名与费尔南举枪自尽", "chateau_dif_abyss", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Dazzling Paris Entrance + Runaway Horses + Morcerf Salon Ball ---
        sfx("m04_01", "act1", "Wild panicked carriage horses neighing and galloping out of control down cobblestone Paris avenue suddenly halted cleanly by a firm rein pull and cheering crowd, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.20),
        dlg("m04_02", "act1", "narrator", "史诗旁白", "踏入巴黎的第一周，基督山伯爵便用两手神来之笔震动了整个上流社会。他高价买走唐格拉尔夫人最心爱的两匹骏马，又故意在维尔福宅邸门前惊马救下维尔福夫人母子，随后将名马拱手回赠。", gap_after_s=0.26),
        dlg("m04_03", "act1", "danglars", "唐格拉尔男爵", "[sarcastic] [angry] 真是疯子！花三万二千法郎买走我太太的马，转手披着钻石马衣又送回我家门前！这位东方伯爵到底有多少家底，能这样把金子当沙子撒？", gap_after_s=0.24),
        motif("m04_04", "act1", "paris_salon_clock_glass", gap_after_s=0.22),
        dlg("m04_05", "act1", "narrator", "史诗旁白", "盛夏之夜，莫尔塞夫伯爵府花园灯火通明。水晶吊灯照亮了半个法国的勋贵，而当身穿纯黑礼服的基督山伯爵踏入大厅时，满场喧嚣瞬间低了下去。", gap_after_s=0.24),
        dlg("m04_06", "act1", "fernand", "莫尔塞夫伯爵", "[warmly] [condescending] 基督山伯爵！感谢您在罗马救了犬子阿尔贝！鄙人费尔南·德·莫尔塞夫，能请您光临寒舍，真是蓬荜生辉！", gap_after_s=0.24),
        dlg("m04_07", "act1", "monte_cristo", "基督山伯爵", "[calmly] [coldly] 莫尔塞夫将军太客气了。您的勋章闪得让人睁不开眼，尤其是那枚约阿尼纳战役的紫星勋章——听说您当年在希腊立过汗马功劳？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("m04_08", "act1", "fernand", "莫尔塞夫伯爵", "[sarcastic] 呵呵，陈年往事罢了，都是替法国和盟友效劳。来，让我引见拙荆——莫尔塞夫伯爵夫人。", gap_after_s=0.22),
        sfx("m04_09", "act1", "Delicate silk gown rustling across parquet floor as a crystal champagne goblet trembles slightly and stops mid-air in hushed tension, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("m04_10", "act1", "mercedes", "梅尔塞苔丝", "[gasps] [trembling] 伯爵先生……您的声音……为什么听上去像隔着二十多年的海风传过来的？请原谅，我忽然觉得有些头晕。", stability=0.0, gap_after_s=0.24),
        dlg("m04_11", "act1", "monte_cristo", "基督山伯爵", "[coldly] [calmly] 夫人过奖了，世上相像的嗓音很多。不过我向来遵守东方规矩——在别人府上，我绝不沾一滴水、不吃一口面包。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("m04_12", "act1", "mercedes", "梅尔塞苔丝", "[whispers] [crying] 不沾水、不吃面包……阿拉伯人的老规矩，不吃仇人的盐和面包，才好拔剑复仇。伯爵先生，请您至少摘下一颗我亲手摘的桃子吧？", stability=0.0, gap_after_s=0.24),
        dlg("m04_13", "act1", "monte_cristo", "基督山伯爵", "[coldly] 夫人，我怕这满园华贵的果子底下，埋着的都是腐烂的根。恕我失陪，明天晚上我在奥特伊别墅设宴，还望各位贵客务必赏光。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m04_14", "act1", "narrator", "史诗旁白", "伯爵转身走入夜色。梅尔塞苔丝紧紧扶住大理石廊柱，指节发白——十四年过去，那张苍白冷峻的脸或许变了模样，可他冷笑时眼底燃着的幽火，全世界只有一个人拥有。", gap_after_s=0.32),
        # --- ACT 2: Auteuil Villa Dinner — Exposing Villefort's Buried Infant Secret ---
        sfx("m04_15", "act2", "Distant rolling summer thunder over a quiet wooded Parisian country estate at night with fine silver cutlery clinking on porcelain plates inside a candlelit dining hall, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m04_16", "act2", "narrator", "史诗旁白", "奥特伊别墅的烛光晚宴，是一场精心排演的心理凌迟。长桌两旁，首席检察官维尔福与唐格拉尔夫人并肩而坐，却发现这座房子的每一块砖瓦都在向他们冷笑。", gap_after_s=0.24),
        dlg("m04_17", "act2", "monte_cristo", "基督山伯爵", "[calmly] 维尔福先生，唐格拉尔夫人，听说这栋老宅当年是圣梅朗侯爵的别院。我刚买下它，就忍不住请两位来参观一间最耐人寻味的房间——请随我上二楼。", acoustic_space="vintage_study", gap_after_s=0.26),
        sfx("m04_18", "act2", "Heavy mahogany bedroom door creaking open onto a dusty silent room with crimson damask curtains fluttering lightly in night wind, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("m04_19", "act2", "paris_villain", "唐格拉尔夫人", "[gasps] [terrified] 啊！这间挂着红缎帷幔的卧室……一模一样！二十年前的那张大床，还有通往后花园的那道暗门楼梯！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.22),
        dlg("m04_20", "act2", "villefort", "热拉尔·德·维尔福", "[coldly] [trembling] 伯爵先生，您这是什么意思？一间普通的空卧室罢了，何必故意把灯光调得这么阴森？", acoustic_space="vintage_study", gap_after_s=0.22),
        dlg("m04_21", "act2", "monte_cristo", "基督山伯爵", "[calmly] [eerie] 别急，检察官大人。请两位朝窗外看——看见花园围墙边那三棵老栗树了吗？前几天园丁翻土种花，在树根下挖出一只腐朽的小木箱，里面铺着绣有贵族徽章的亚麻襁褓。", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m04_22", "act2", "monte_cristo", "基督山伯爵", "[coldly] [whispers] 我真好奇，究竟是哪位体面君子，会在一个暴雨夜里偷偷走下这道暗梯，把一个还在呼吸的新生私生子亲手埋进花泥里？而且……就在埋下去的那一刻，被人从背后捅了一刀？", acoustic_space="vintage_study", gap_after_s=0.28),
        dlg("m04_23", "act2", "paris_villain", "唐格拉尔夫人", "[crying] [terrified] 救命！我的孩子……维尔福，你当年骗我说他是死胎！你竟然把他活埋了！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.22),
        dlg("m04_24", "act2", "villefort", "热拉尔·德·维尔福", "[hoarsely] [angry] 闭嘴！夫人你喝醉了！伯爵先生，您的恶作剧到此为止——如果真有尸骨，为什么不报官？", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("m04_25", "act2", "monte_cristo", "基督山伯爵", "[chuckles] [coldly] 奇妙就在这儿，检察官大人。木箱里是空的。那个婴儿被路过的仇家救活了，如今已经长大成人，而且……听说他前几天刚拿着巨额汇票进了巴黎城。", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m04_26", "act2", "narrator", "史诗旁白", "维尔福浑身冰凉，手里的银叉当啷砸在瓷盘上。他以为埋在二十年泥土底下的罪孽，已被一只看不见的巨手从坟墓里重新掘了出来。", gap_after_s=0.34),
        # --- ACT 3: Newspaper Scandal + Chamber of Peers Trial + Haydee's Testimony ---
        sfx("m04_27", "act3", "Grand stone chamber doors opening into a murmuring Parisian parliamentary hall followed by a heavy wooden presidential gavel striking three times for silence, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.22),
        dlg("m04_28", "act3", "narrator", "史诗旁白", "正当维尔福焦头烂额之际，第一道雷霆已经狠狠劈在了费尔南头顶。《公正报》头版惊爆猛料：大名鼎鼎的莫尔塞夫伯爵，当年在希腊约阿尼纳靠出卖恩主阿里帕夏换取了万贯赃款！", gap_after_s=0.26),
        dlg("m04_29", "act3", "morrel", "贵族院议长", "[solemn] 肃静！法国贵族院特别调查会现在开庭。莫尔塞夫伯爵，报端指控你一八二三年私通敌军、献出要塞、杀害庇护你的阿里帕夏，你可认罪？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m04_30", "act3", "fernand", "莫尔塞夫伯爵", "[angry] [shouting] 荒谬绝伦的污蔑！议长大人，阿里帕夏被围城时我曾浴血死战！如今死无对证，哪个卑鄙小人敢躲在阴沟里往法兰西将军脸上泼脏水！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m04_31", "act3", "morrel", "贵族院议长", "[seriously] 莫尔塞夫伯爵，这里恰恰有一位亲历约阿尼纳屠城的活人证人请求出庭。传证人——阿里帕夏之女，海黛公主！", acoustic_space="vast_hall", gap_after_s=0.20),
        sfx("m04_32", "act3", "Light resolute silk slippers stepping steadily across marble courtroom tiles as stunned whispers ripple through a large domed chamber, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m04_33", "act3", "fernand", "莫尔塞夫伯爵", "[gasps] [terrified] 不……不可能！她早就死在君士坦丁堡的奴隶船上了！怎么会站在巴黎贵族院里？！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("m04_34", "act3", "haydee", "海黛公主", "[solemn] [fiercely] 我没有死，费尔南·蒙代戈！各位贵族院的大人请睁开眼，看看他右手虎口那道弯月刀疤——那是我父王临死前扑上去咬出的印记！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m04_35", "act3", "haydee", "海黛公主", "[crying] [fiercely] 那天夜里，我父王把满城兵权和妻女托付给这个法国军官。可他收了敌军两千袋金币，亲手打开城门放屠夫冲进王宫，割下我父亲的头颅去领赏！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m04_36", "act3", "haydee", "海黛公主", "[hoarsely] [fiercely] 第二天清晨，他把我母亲气死在铁链上，又把年仅四岁的我卖给奴隶贩子换了最后一把金洋！这是当年土耳其商人的卖身契原件，上面清清楚楚签着他的大名——费尔南·蒙代戈！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.26),
        sfx("m04_37", "act3", "Uproarious shock erupting across wooden parliamentary benches as papers slam down and heavy gavel pounds repeatedly in chaos, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m04_38", "act3", "morrel", "贵族院议长", "[dramatically] [solemn] 笔迹、印章、人证俱全！本院全体一致裁定：莫尔塞夫伯爵叛国卖主、通敌谋利罪名成立！剥夺其一切贵族席位与军功荣誉！", acoustic_space="vast_hall", gap_after_s=0.28),
        sfx("m04_39", "act3", "Velvet opera box door flinging open sharply during an intermission hush as a leather white glove slaps hard against a mahogany railing, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.20),
        dlg("m04_40", "act3", "albert_max", "阿尔贝·德·莫尔塞夫", "[shouting] [angry] 基督山伯爵！我查到了——报社的线人是从你府上领的赏银，海黛也是你带进巴黎的！你在罗马救过我，今天却毁了我全家！明早八点文森森林，咱们用手枪了断！", stability=0.0, gap_after_s=0.26),
        dlg("m04_41", "act3", "monte_cristo", "基督山伯爵", "[coldly] 既然莫尔塞夫子爵执意要用子弹捍卫父亲的污名，明早八点，我奉陪到底。", acoustic_space="studio_warm", gap_after_s=0.34),
        # --- ACT 4: Midnight Plea from Mercedes + Dawn Duel Apology ---
        sfx("m04_42", "act4", "Late midnight rain tapping softly against tall French study windows as a quiet side door opens and heavy velvet footsteps approach a desk, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m04_43", "act4", "narrator", "史诗旁白", "决斗前夜凌晨一点。基督山伯爵正擦拭着那对百步穿杨的决斗手枪，书房暗门却被人推开——披着黑色头纱的梅尔塞苔丝站在烛火边缘，瘦得像一缕随时会散去的轻烟。", gap_after_s=0.26),
        dlg("m04_44", "act4", "monte_cristo", "基督山伯爵", "[coldly] 莫尔塞夫夫人，您深夜闯进明天要枪杀您儿子的仇人府上，未免太不合巴黎礼数了吧？", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("m04_45", "act4", "mercedes", "梅尔塞苔丝", "[crying] [softly] 别再装了……爱德蒙。从你在花园拒吃我摘的桃子那一刻，我就知道你回来了。你二十步外能一枪打穿一张红桃扑克，明天早上八点，我的阿尔贝必死无疑！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m04_46", "act4", "monte_cristo", "基督山伯爵", "[angry] [coldly] 梅尔塞苔丝！你凭什么替费尔南的儿子求情？！当年我在伊夫堡啃发霉面包、听着我父亲活活饿死的消息时，你在哪儿？你在戴着他的钻石戒指当伯爵夫人！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m04_47", "act4", "mercedes", "梅尔塞苔丝", "[crying] [desperately] 爱德蒙，你把那封害死你的黑信拍在桌上看清楚吧——我发誓我到今天才知道是费尔南陷害了你！如果我知道真相，宁愿跳进马赛海里淹死也不会嫁给他！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m04_48", "act4", "mercedes", "梅尔塞苔丝", "[crying] [whispers] 可阿尔贝是无辜的啊！他连当年发生了什么都不知道！爱德蒙，看在我们当年在加泰罗尼亚海风里定情的份上，我跪下来求你——放过我的儿子，把枪口对准我吧！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.28),
        dlg("m04_49", "act4", "narrator", "史诗旁白", "那声呼唤像一把滚烫的利刃，劈开了伯爵冰封了二十三年的心脏。他缓缓扶起泪流满面的梅尔塞苔丝，第一次在复仇路上低下了高傲的头。", gap_after_s=0.26),
        dlg("m04_50", "act4", "monte_cristo", "基督山伯爵", "[hoarsely] [softly] 起来吧，梅尔塞苔丝……你的眼泪赢了。明天早晨在文森森林，阿尔贝会毫发无伤地活着回家。至于我……我会站着不动，接下他射向我胸口的子弹。", acoustic_space="vintage_study", gap_after_s=0.30),
        sfx("m04_51", "act4", "Crisp chilly Parisian dawn forest breeze rustling damp autumn leaves with boots crunching gravel and a brass pistol case snapping open, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m04_52", "act4", "narrator", "史诗旁白", "然而次日清晨八点，文森森林的薄雾里却没有响起枪声。听完母亲哭诉全部真相的阿尔贝大步跨过草地，把决斗手枪重重放回木盒，当着全巴黎见证人的面向伯爵深深鞠躬。", gap_after_s=0.26),
        dlg("m04_53", "act4", "albert_max", "阿尔贝·德·莫尔塞夫", "[seriously] [solemn] 基督山伯爵，昨夜母亲告诉我二十三年前您所受的全部冤屈。我的父亲是个卑鄙的叛徒和告密者，您复仇得光明磊落——我当众向您道歉！", gap_after_s=0.24),
        dlg("m04_54", "act4", "albert_max", "阿尔贝·德·莫尔塞夫", "[solemn] 从今天起，我放弃莫尔塞夫这个肮脏的姓氏，不带走府里一枚脏金币，只带着母亲净身出户，靠我自己的双手重新做人！", gap_after_s=0.26),
        dlg("m04_55", "act4", "monte_cristo", "基督山伯爵", "[warmly] [solemn] 阿尔贝，你比你的父亲高贵一万倍。你今天不仅保住了自己的性命，也救赎了我的灵魂。", gap_after_s=0.32),
        # --- ACT 5: Fernand Confronts Dantes and Shoots Himself ---
        sfx("m04_56", "act5", "Furious boots kicking open an ornate Parisian study door followed by frantic heavy breathing and steel sword cane tapping stone floor, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.18),
        dlg("m04_57", "act5", "narrator", "史诗旁白", "一个小时后，彻底众叛亲离的费尔南像一头困兽冲进伯爵府书房。妻子带着儿子拖着一只旧布箱离开了豪宅，他满眼血丝，拔出手枪指着冷静端坐的伯爵。", gap_after_s=0.24),
        dlg("m04_58", "act5", "fernand", "莫尔塞夫伯爵", "[shouting] [maniacal] 畜生！你毁了我的荣誉、抢走了我的妻儿，现在连决斗都不敢跟我儿子打！你到底是谁？我跟你无冤无仇，你为什么要把我逼进绝路！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("m04_59", "act5", "monte_cristo", "基督山伯爵", "[coldly] [calmly] 无冤无仇？莫尔塞夫将军，把你沾满希腊鲜血的手放低一点。你听听这个名字——一八一五年，马赛港，加泰罗尼亚村，法老号大副，爱德蒙·唐泰斯。", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m04_60", "act5", "fernand", "莫尔塞夫伯爵", "[gasps] [terrified] 爱……爱德蒙·唐泰斯？！不！你早就死在伊夫堡海底了！你是鬼魂——你是从地狱爬回来索命的魔鬼！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("m04_61", "act5", "monte_cristo", "基督山伯爵", "[coldly] [solemn] 费尔南，你当年在卡德鲁斯酒馆亲手把那封黑信塞进邮筒时，可曾想过十四年黑牢里我会活着回来？滚吧，我不杀你——去空荡荡的豪宅里，听你自己的良心审判你。", acoustic_space="vintage_study", gap_after_s=0.26),
        motif("m04_62", "act5", "duel_pistol_cock", gap_after_s=0.16),
        sfx("m04_63", "act5", "Stumbling frantic footsteps fleeing down stone hallway steps, heavy study door slamming shut, followed by a single echoing 19th-century pistol gunshot ringing across an empty mansion", duration_seconds=3.4, gap_after_s=0.24),
        dlg("m04_64", "act5", "narrator", "史诗旁白", "[solemn] 午后三点，莫尔塞夫伯爵府二楼书房传来一声沉闷的枪响。三大仇人中的第一位，就此伏诛。基督山伯爵在怀表记事本上轻轻划掉第一个名字——而此刻，维尔福府里的毒药，与唐格拉尔银行的百亿风暴，已同时引爆！下一集，《玫瑰毒影与金融风暴》！", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E004",
        chapter_number=4,
        title="巴黎假面盛宴_奥特伊毒屋与海黛公主血证",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e005_poison_court_bankruptcy() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·番木鳖碱毒理暗局与假死秘药救女", "conspiracy_tavern_shadow", bgm_duration_s=75.0),
        act("act2", "第二幕·买通电报员做空公债与五百万挤兑", "paris_venetian_revenge", bgm_duration_s=75.0),
        act("act3", "第三幕·巴黎重罪法庭活埋亲子惊天铁证", "paris_venetian_revenge", bgm_duration_s=75.0),
        act("act4", "第四幕·毒妇携幼子双亡与维尔福花园发疯", "chateau_dif_abyss", bgm_duration_s=75.0),
        act("act5", "第五幕·伯爵战栗自省与唐格拉尔连夜潜逃", "chateau_dif_abyss", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Count's Toxicology Lecture + Poisoning Spree + Saving Valentine ---
        motif("m05_01", "act1", "paris_salon_clock_glass", gap_after_s=0.20),
        dlg("m05_02", "act1", "narrator", "史诗旁白", "维尔福家的惨剧，竟是从贪婪的内部腐烂开始的。几周前，伯爵在花园温室里闲聊植物毒理学时，便敏锐察觉维尔福夫人眼里闪动着一条毒蛇的光芒。", gap_after_s=0.26),
        dlg("m05_03", "act1", "paris_villain", "维尔福夫人", "[softly] [seductive] 伯爵先生真是博学。您方才说，东方有一种从番木鳖提炼的绿药水，滴一滴可以救治瘫痪老人，滴三滴就能让人在睡梦里无声无息离开——不知这药真有这么神奇？", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m05_04", "act1", "monte_cristo", "基督山伯爵", "[calmly] [coldly] 毒药和良药本来就只隔着一线剂量，夫人。就像正义和贪欲一样，全看握着药瓶的人心里装着什么念头。", acoustic_space="vintage_study", gap_after_s=0.24),
        sfx("m05_05", "act1", "Tiny glass apothecary vial stopper unsealing quietly in midnight silence followed by three faint liquid drops splashing into a bedside crystal water carafe, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m05_06", "act1", "narrator", "史诗旁白", "不久后，死神便在维尔福宅邸接连敲门。为了让自己亲生的幼子爱德华独吞整座豪门百万遗产，维尔福夫人接连毒死了岳父圣梅朗侯爵、侯爵夫人与老仆巴鲁瓦，最后把毒手伸向了继女瓦朗蒂娜。", gap_after_s=0.28),
        dlg("m05_06b", "act1", "narrator", "史诗旁白", "更令毒妇抓狂的是，维尔福那位全身瘫痪、只剩一双眼睛能眨动的波拿巴派老父亲诺瓦蒂埃，竟硬生生用眨眼暗号立下公证遗嘱：只要瓦朗蒂娜敢听父亲的话嫁给别人，就把九十万法郎全部捐给穷人！", gap_after_s=0.26),
        dlg("m05_06c", "act1", "villefort", "热拉尔·德·维尔福", "[angry] [coldly] 父亲，您连一根手指都动不了，却用眨眼拆散了我替女儿安排的贵族婚事！公证员已经签字，若瓦朗蒂娜真和莫雷尔那个小军官私定终身，我这首席检察官的脸往哪儿搁！", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m05_07", "act1", "paris_villain", "维尔福夫人", "[whispers] [coldly] 瓦朗蒂娜啊，别怪继母心狠。外祖父和祖父把九十万法郎全写在你名下，只要今晚这杯柠檬水喝下去，明早整个维尔福府的所有金子，就全都是我宝贝儿子爱德华的了。", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m05_08", "act1", "narrator", "史诗旁白", "可她绝没想到，黑暗的壁炉暗门后，一直站着洞察一切的基督山伯爵。得知瓦朗蒂娜深爱的恋人竟是恩人摩莱尔的儿子马克西米利安，伯爵决意在死神手里抢回这条无辜性命。", gap_after_s=0.26),
        sfx("m05_09", "act1", "Soft secret wooden wall panel sliding silently aside in a dark candlelit bedroom with gentle measured footsteps approaching a sickbed, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.18),
        dlg("m05_10", "act1", "haydee", "瓦朗蒂娜·德·维尔福", "[hoarsely] [terrified] 谁……谁在暗门里？我喉咙好烫，全身像灌了铅一样动不了……刚才继母进来过……", stability=0.0, gap_after_s=0.24),
        dlg("m05_11", "act1", "monte_cristo", "基督山伯爵", "[softly] [warmly] 别怕，好姑娘，我是马克西米利安最好的朋友。你瘫痪的祖父诺瓦蒂埃老先生极聪明，早已暗中每天让你服微量番木鳖产生抗药性。现在把这颗绿色药丸含在舌下。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m05_12", "act1", "haydee", "瓦朗蒂娜·德·维尔福", "[trembling] [softly] 这……这是什么药？我吃了会死吗？马克西米利安要是以为我死了，一定会发疯的……", gap_after_s=0.24),
        dlg("m05_13", "act1", "monte_cristo", "基督山伯爵", "[warmly] [whispers] 这是一粒让你假死三十六小时的东方秘药。明天医生会宣布你离世，毒妇便不会再对你下手；入夜后我会亲手把你从墓室接出来，送到安全的地方。闭上眼，相信我。", acoustic_space="studio_warm", gap_after_s=0.28),
        sfx("m05_13b", "act1", "Solemn distant Parisian church funeral bells tolling slowly over rain-slicked cemetery cypress trees and wet marble gravel footsteps, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m05_13c", "act1", "albert_max", "马克西米利安·莫雷尔", "[crying] [desperately] 伯爵先生，您放开我！瓦朗蒂娜死了，我活着还有什么意思？让我现在就开枪陪她去吧！", stability=0.0, gap_after_s=0.24),
        dlg("m05_13d", "act1", "monte_cristo", "基督山伯爵", "[solemn] [warmly] 马克西米利安，听着——你父亲皮埃尔·摩莱尔临终前，是不是反复呼唤过一个名字？爱德蒙·唐泰斯！我就是那个水手，也是当年派新法老号救你们全家的辛巴达！", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m05_13e", "act1", "monte_cristo", "基督山伯爵", "[warmly] 孩子，看在你父亲的份上，答应我活过这三十天。如果十月五日那天你依然心如死灰，我亲手给你一勺无痛的解脱——但现在，你必须相信奇迹！", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m05_14", "act1", "narrator", "史诗旁白", "安顿好崩溃的马克西米利安并暗中把苏醒的瓦朗蒂娜送上开往基督山岛的游艇后，伯爵缓缓收起柔情，将冷酷的目光投向了第二个目标——不可一世的巴黎头号金融大鳄，唐格拉尔男爵。", gap_after_s=0.34),
        # --- ACT 2: Telegraph Bribery, Bond Manipulation & 5-Million-Franc Bank Run on Danglars ---
        sfx("m05_15", "act2", "Clattering wooden semaphore telegraph levers clicking rhythmically on a windswept hillside tower with rustling crisp gold banknotes counting out slowly, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.20),
        dlg("m05_16", "act2", "narrator", "史诗旁白", "打击一个爱钱如命的银行家，最好的武器从来不是匕首，而是他最迷信的杠杆和贪欲。伯爵悄悄来到巴黎郊外的蒙莱里信号塔，用两万五千法郎买通了沉迷种花的信号塔电报员。", gap_after_s=0.26),
        dlg("m05_17", "act2", "caderousse", "电报员", "[whispers] [earthy] 先生，两万五千法郎够我买一整座玫瑰园退休养老了！您要我把臂板多摆那三个字母——“唐卡洛斯率叛军攻陷马德里”——好，发过去了，巴黎交易所半小时内就会翻天！", gap_after_s=0.26),
        sfx("m05_18", "act2", "Chaotic Parisian stock exchange brass bell clanging rapidly amidst frantic shuffling of bond certificates and chairs banging in panic, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m05_19", "act2", "danglars", "唐格拉尔男爵", "[terrified] [shouting] 什么？！西班牙公债一天暴跌三十个点？快抛！把我手里两百万西班牙债券全部割肉抛掉——什么？第二天电报局辟谣说是假消息，债价又暴涨回去了？！我平白赔了整整一百万法郎！", stability=0.0, gap_after_s=0.26),
        dlg("m05_20", "act2", "narrator", "史诗旁白", "屋漏偏逢连夜雨。紧接着，伯爵又暗中抽干唐格拉尔在希腊、罗马和铁路公司里的全部抵押信用，更在订婚夜让假冒意大利王子的女婿贝内代托涉案逃亡，令银行信用雪崩。", gap_after_s=0.26),
        sfx("m05_21", "act2", "Heavy gilded bank office door opening with brisk footsteps and a folded parchment letter of unlimited credit slapped neatly onto a leather desk blotter, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.20),
        dlg("m05_22", "act2", "monte_cristo", "基督山伯爵", "[calmly] [chuckles] 早安，唐格拉尔男爵。听说贵行最近手头颇为周转不灵？真不巧，我刚在巴黎看中几座城堡，今天想从我那份无上限信用账户里，一次提取五百万法郎现金。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m05_23", "act2", "danglars", "唐格拉尔男爵", "[gasps] [desperately] 五……五百万法郎现金？！伯爵先生您开什么玩笑！我行金库里全部现钞加上慈善医院存在我这儿的五百万信托准备金，加起来也就这么多——您这不是要我的命吗！", stability=0.0, gap_after_s=0.26),
        dlg("m05_24", "act2", "monte_cristo", "基督山伯爵", "[coldly] [sarcastic] 怎么，堂堂巴黎第一银行家连罗马同行背书的五百万信用证都兑不出来？那我只好请法兰西银行和全巴黎储户明天一起来帮您算算账了。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m05_25", "act2", "danglars", "唐格拉尔男爵", "[hoarsely] [trembling] 别！千万别声张！拿去……我这就开法兰西银行见票即付支票！五百万现金归您，可明天慈善医院来提款我彻底完了……我只能今晚带着最后一张五百万汇票偷渡去罗马！", stability=0.0, gap_after_s=0.34),
        # --- ACT 3: Paris Assize Court — Benedetto Destroys Villefort ---
        sfx("m05_26", "act3", "Crowded 19th-century Paris criminal courtroom hubbub hushed by three resonant wooden gavel strikes and heavy iron prisoner chains clanking at the witness stand, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.20),
        dlg("m05_27", "act3", "narrator", "史诗旁白", "同一天下午，巴黎重罪法庭座无虚席。首席检察官维尔福强忍着家中刚办完丧事的剧痛，身穿大红法袍坐上公诉席，亲自审理伪装意大利王子、谋杀卡德鲁斯的惯犯贝内代托。", gap_after_s=0.26),
        dlg("m05_28", "act3", "villefort", "热拉尔·德·维尔福", "[solemn] [coldly] 法官大人、陪审团诸位！被告贝内代托出身卑贱、恶贯满盈，妄图混入贵族圈骗婚谋财，罪证确凿，请法庭立刻判处其死刑！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m05_29", "act3", "morrel", "法庭庭长", "[calmly] 被告贝内代托，按律例询问你的身份与来历。你可知道自己的亲生父母是谁？", acoustic_space="vast_hall", gap_after_s=0.20),
        dlg("m05_30", "act3", "jailer_bandit", "贝内代托", "[laughs] [sarcastic] 哈哈哈！庭长大人，昨天之前我一直以为自己是没人要的野种！直到一位好心的神秘人把这份绣着贵族徽章的亚麻襁褓和日记送进我的囚室——我现在清清楚楚知道我父亲是谁！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m05_31", "act3", "villefort", "热拉尔·德·维尔福", "[gasps] [shouting] 庭长大人！被告在当庭胡言乱语扰乱秩序！我请求立刻堵住他的嘴把他押下去！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("m05_32", "act3", "jailer_bandit", "贝内代托", "[shouting] [fiercely] 你们看他抖成什么样了！二十一年前九月二十七日深夜，在奥特伊花园栗树底下，一个男人把刚生下来的我塞进木箱亲手活埋！救我出来的老走私犯亲眼看清了他的脸！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m05_33", "act3", "jailer_bandit", "贝内代托", "[shouting] [maniacal] 各位睁大眼睛瞧瞧吧！那个活埋亲骨肉的伪君子、我的亲生父亲——就是此刻穿着大红法袍、大义凛然要送我上断头台的首席检察官热拉尔·德·维尔福！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        sfx("m05_34", "act3", "Deafening gasps and uproar sweeping a packed stone courthouse as wooden benches scrape wildly and a prosecutor's velvet cap tumbles onto the desk, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m05_35", "act3", "morrel", "法庭庭长", "[seriously] [solemn] 维尔福先生！全巴黎都在看着您——您难道不打算站起来反驳这骇人听闻的指控吗？！", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("m05_36", "act3", "villefort", "热拉尔·德·维尔福", "[hoarsely] [trembling] 不……不必反驳了。他说的……每一个字都是真的。我是个罪人。我脱下这身法袍，交给你们审判——但请放我先回家一趟，家里还有一只毒蛇等着我清算！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.34),
        # --- ACT 4: Wife & Child Dead + Villefort Goes Mad + Count's Crisis of Conscience ---
        sfx("m05_37", "act4", "Hurried heavy carriage wheels halting sharply outside iron mansion gates, frantic footsteps racing up marble stairs and bursting into a dark quiet bedroom, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m05_38", "act4", "narrator", "史诗旁白", "维尔福像疯狗般冲回宅邸。出门前他已查明下毒真凶正是妻子，逼她在他散庭回来之前自行了断以保全家族最后一点体面。可推开卧室门的一刻，眼前的景象把他的灵魂彻底撕碎了。", gap_after_s=0.26),
        dlg("m05_39", "act4", "villefort", "热拉尔·德·维尔福", "[terrified] [crying] 埃洛伊丝！你喝了毒药……可为什么——为什么我的小儿子爱德华也躺在沙发上没有呼吸？！你把九岁的孩子一起毒死了？！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m05_40", "act4", "narrator", "史诗旁白", "桌上留着毒妇临死的血书：“好母亲绝不独留爱子在世受辱。”就在维尔福瘫软在地之际，暗处走出了浑身黑衣的基督山伯爵。", gap_after_s=0.24),
        dlg("m05_41", "act4", "monte_cristo", "基督山伯爵", "[coldly] 维尔福先生，当年你为了一纸前程，把清白的爱德蒙·唐泰斯活埋进伊夫堡，害他老父活活饿死。今日天网恢恢，你的报应终于——", acoustic_space="vintage_study", gap_after_s=0.18),
        dlg("m05_42", "act4", "villefort", "热拉尔·德·维尔福", "[maniacal] [crying] 爱德蒙·唐泰斯！哈哈哈哈！你过来看看吧！看看沙发上这个才九岁的孩子！他当年甚至还没出生！你的仇报够了吗？你的心满意足了吗？！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("m05_43", "act4", "monte_cristo", "基督山伯爵", "[gasps] [terrified] 孩子……爱德华？！不！我从没想过害一个九岁的孩子！快让我看看他的脉搏——拿我的红药水来！滴下去，怎么没有反应？！", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        sfx("m05_44", "act4", "Wild crazed footsteps dashing out into a rain-soaked garden followed by frantic bare hands clawing and digging wildly into wet earth and mud, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m05_45", "act4", "villefort", "热拉尔·德·维尔福", "[maniacal] [laughs] 哈哈哈哈！快挖啊！儿子没死，儿子藏在花园泥土下面！你看，铁锹呢？我用手指头也能把我的小儿子挖出来！", stability=0.0, gap_after_s=0.26),
        # --- ACT 5: Count Questions Vengeance + Cliffhanger to Rome ---
        dlg("m05_46", "act5", "narrator", "史诗旁白", "大雨倾盆而下，曾经高不可攀的法兰西首席检察官，彻底疯癫地跪在泥水里徒手刨土。而第一次，那个自诩替天行道的复仇之神，在雨夜里感到了刺骨的寒意。", gap_after_s=0.26),
        dlg("m05_47", "act5", "monte_cristo", "基督山伯爵", "[hoarsely] [trembling] 上帝啊……我是不是走得太远了？法利亚神父临终前告诫过我，千万别伤及无辜。费尔南死了，维尔福疯了，可一个九岁的孩子也葬送在这场风暴里……", stability=0.0, acoustic_space="studio_warm", gap_after_s=0.28),
        dlg("m05_48", "act5", "monte_cristo", "基督山伯爵", "[solemn] [calmly] 够了。凡人终究不是上帝，这把复仇的利剑必须收鞘了。最后一个仇人唐格拉尔已经卷着慈善医院的五百万逃往罗马——这一次，我不再索他的命。我要在罗马地窟里，给他上一堂终生难忘的宽恕课。", acoustic_space="studio_warm", gap_after_s=0.28),
        dlg("m05_49", "act5", "narrator", "史诗旁白", "[dramatically] 大仇将尽，执念将消。大结局《罗马地窟天价烤鸡与尾声》——贪婪银行家面对十万法郎一只的烤鸡如何彻底崩溃？瓦朗蒂娜能否在基督山岛与恋人奇迹重逢？敬请收听最终章！", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E005",
        chapter_number=5,
        title="玫瑰毒影与金融风暴_维尔福崩塌与唐格拉尔破产",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e006_roman_feast_wait_hope() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·罗马地窟十万法郎天价烤鸡", "conspiracy_tavern_shadow", bgm_duration_s=75.0),
        act("act2", "第二幕·报真名宽恕仇敌与一夜白头", "paris_venetian_revenge", bgm_duration_s=75.0),
        act("act3", "第三幕·重返伊夫堡空牢与梅尔塞苔丝释怀", "marseille_sunlit_harbor", bgm_duration_s=75.0),
        act("act4", "第四幕·基督山岛夕阳假死奇迹重逢", "treasure_rebirth_overture", bgm_duration_s=75.0),
        act("act5", "第五幕·白帆远航地中海与等待和希望", "wait_and_hope_epilogue", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Danglars's Arrogant Flight to Rome + 3-Day 100,000-Franc Roast Chicken Torment ---
        sfx("m06_00a", "act1", "Hurried horse-drawn Roman stagecoach galloping down dusty Appian Way road abruptly halted by armed brigands grabbing the bridles and wrenching open the carriage door, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("m06_00b", "act1", "narrator", "史诗旁白", "两周前，卷走巴黎慈善医院五百万法郎信托款的唐格拉尔连夜逃抵罗马。刚在托洛尼亚银行把汇票换成厚厚一叠见票即付支票，他还在马车里沾沾自喜地冷笑。", gap_after_s=0.26),
        dlg("m06_00c", "act1", "danglars", "唐格拉尔男爵", "[chuckles] [sarcastic] 嘿嘿，巴黎那群蠢货储户和维尔福爱怎么闹怎么闹去！只要老子怀里揣着这五百万法郎现金票据，到了威尼斯一样东山再起，当我的百万富翁——喂！车夫怎么突然停车了？！", gap_after_s=0.26),
        sfx("m06_01", "act1", "Echoing subterranean Roman limestone catacomb water droplets with crackling iron wall torches and a silver banquet cloche lifted dramatically from a steaming platter, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.22),
        dlg("m06_02", "act1", "narrator", "史诗旁白", "半小时后，美梦彻底碎成了噩梦。罗马强盗首领路易吉·万帕把这位自以为聪明的银行家，直接蒙眼扔进了圣塞巴斯蒂安古墓地窟。此时他已被活活饿了整整两天。", gap_after_s=0.26),
        dlg("m06_03", "act1", "danglars", "唐格拉尔男爵", "[hoarsely] [desperately] 喂！强盗头子！我快饿死了！你们抓我不是为了赎金吗？为什么不开口要价，连块硬面包、连口冷水都不给我吃？！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m06_04", "act1", "jailer_bandit", "路易吉·万帕", "[sarcastic] [chuckles] 哎呀，男爵大人别动气！我们这儿可不兴绑票，我们是全罗马最讲究的五星级洞穴饭馆，什么山珍海味都有——只要您付得起饭钱！来人，端一只香喷喷的烤鸡来！", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_05", "act1", "danglars", "唐格拉尔男爵", "[excited] [rushed] 烤鸡！太好了，闻着都香得要命，快端过来！多少钱？二十法郎？五十法郎？我全付！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("m06_06", "act1", "jailer_bandit", "路易吉·万帕", "[coldly] [sarcastic] 五十法郎？男爵大人真会开玩笑。我们洞里物价公道，童叟无欺——一口价，一只烤鸡十万法郎！附送一杯清水，另收五万法郎！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m06_07", "act1", "danglars", "唐格拉尔男爵", "[shouting] [angry] 十万法郎一只烤鸡？！你们这帮强盗抢钱也没有这么抢的！我宁可饿死也不签这笔荒唐账！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m06_08", "act1", "narrator", "史诗旁白", "强盗冷笑一声，盖上银盖转身离去。可烤鸡的油脂香气仍在漆黑潮湿的地牢里飘荡。又挨过三十六个小时，胃里烧得像吞了炭火的银行家，终于哆嗦着抓起了鹅毛笔。", gap_after_s=0.26),
        sfx("m06_09", "act1", "Trembling quill pen scribbling frantically across a crisp bank draft note followed by ravenous clinking silverware on a stone table, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m06_10", "act1", "danglars", "唐格拉尔男爵", "[hoarsely] [desperately] 拿回来！我签！我签十万法郎支票买这只烤鸡！再给我一杯水——什么，还要五万？签，我也签！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m06_11", "act1", "narrator", "史诗旁白", "第一天十万，第二天二十万，第三天一瓶普通红酒开价一百万。贪财如命的银行家眼睁睁看着自己一辈子巧取豪夺的五百万巨款，变成了一顿顿果腹的冷饭，心理防线彻底崩溃。", gap_after_s=0.26),
        dlg("m06_12", "act1", "danglars", "唐格拉尔男爵", "[crying] [desperately] 别拿走了……三天吃掉了我四百九十五万法郎！我只剩最后五万法郎了！我破产了，我一无所有了……求求你们，饶了我一条狗命吧！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.28),
        # --- ACT 2: Count Reveals True Name & Grants Mercy ---
        sfx("m06_13", "act2", "Slow steady footsteps emerging from deep dark stone arches as a cloak rustles calmly beside flickering torch flames, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("m06_14", "act2", "monte_cristo", "基督山伯爵", "[calmly] [coldly] 饿肚子的滋味不好受吧，唐格拉尔先生？你只挨了三天饿，就痛哭流涕交出了五百万；那你可曾想过，当年一位马赛老父亲在阁楼里活活饿死前，挨了多少天饿？", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_15", "act2", "danglars", "唐格拉尔男爵", "[terrified] [trembling] 这声音……你是谁？！你不是罗马强盗！你到底想把我怎么样？", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("m06_16", "act2", "monte_cristo", "基督山伯爵", "[solemn] [coldly] 抬起头看清楚我的眼睛。二十三年前，在马赛港法老号甲板上，你用左手写了一封匿名黑信，把我推进了十四年的伊夫堡水牢——我是爱德蒙·唐泰斯。", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_17", "act2", "danglars", "唐格拉尔男爵", "[gasps] [crying] 爱德蒙·唐泰斯？！求你别杀我！我把慈善医院的钱全赔给他们，我给你磕头——千万别杀我！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("m06_18", "act2", "monte_cristo", "基督山伯爵", "[calmly] [softly] 你放心，我不杀你。你吞下的那五百万慈善款，我已经替你原封不动还给了巴黎孤儿院。至于你口袋里剩下的最后五万法郎，我留给你保命。", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_19", "act2", "monte_cristo", "基督山伯爵", "[solemn] 万帕，给他一顿饱饭，天亮后放他自由。唐格拉尔，你活着吧——像个彻底破产的穷老头一样，在良心与悔恨里，走完你的余生。", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_20", "act2", "narrator", "史诗旁白", "次日清晨，获释的唐格拉尔扑到罗马郊外清澈的溪水边痛饮冷水。当他无意瞥见水中的倒影时，发出一声绝望的哀嚎——短短一夜之间，他满头黑发已全部雪白。", gap_after_s=0.34),
        # --- ACT 3: Returning to Chateau d'If Tour Guide Scene & Marseille Farewell with Mercedes ---
        motif("m06_21", "act3", "marseille_harbor_bell", gap_after_s=0.22, director_note="重返马赛港，海风依旧，物是人非"),
        dlg("m06_22", "act3", "narrator", "史诗旁白", "深秋，基督山伯爵独自回到阔别二十四年的马赛城。他租了一叶小舟重登已被改为古迹的伊夫堡，随着拎着灯笼的老向导，一步步走回了那间潮湿冰冷的三十四号空牢房。", gap_after_s=0.26),
        sfx("m06_22b", "act3", "Echoing slow footsteps inside an empty hollow medieval stone prison cell with a rusty tin lantern creaking gently in sea draft, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("m06_22c", "act3", "caderousse", "伊夫堡老向导", "[earthy] 贵客您瞧这块翘起来的石板！十几年前这儿关过一个意大利疯神父和一个年轻海员，俩人硬拿铁勺挖穿了石墙！后来老神父死了，那小子居然钻进裹尸袋跳海逃了，大伙儿都说他淹死在浪里啦！", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_22d", "act3", "monte_cristo", "基督山伯爵", "[softly] [warmly] 向导先生，这是十枚路易金币——请你把当年那位神父写在衬衣布条上的旧手稿卖给我，然后让我一个人在这里静静待十分钟。", acoustic_space="vast_hall", gap_after_s=0.26),
        dlg("m06_23", "act3", "monte_cristo", "基督山伯爵", "[softly] [solemn] 恩师，我又回来看您了。我抚摸着您当年刻在墙上的拉丁文，心里终于没有了灼烧的恨火——谢谢您，我今天才算真正走出了伊夫堡。", acoustic_space="vast_hall", gap_after_s=0.26),
        sfx("m06_24", "act3", "Gentle coastal autumn wind rustling garden grapevine leaves with soft hesitant footsteps pausing beside a weathered wooden gate, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("m06_25", "act3", "narrator", "史诗旁白", "离开海岛后，他走进了马赛城郊那间带葡萄架的小院——那是当年老父亲住过的旧屋，也是梅尔塞苔丝放弃豪门富贵后的归宿。", gap_after_s=0.24),
        dlg("m06_26", "act3", "mercedes", "梅尔塞苔丝", "[softly] [warmly] 爱德蒙……你终于来看我了。阿尔贝已经去非洲当了一名光荣的普通士兵，他说要靠自己的双手挣回清白的名声。而我，搬回了这个你当年最想给我买下的小院。", gap_after_s=0.26),
        dlg("m06_27", "act3", "monte_cristo", "基督山伯爵", "[softly] [warmly] 梅尔塞苔丝，这间屋子的地契和院角埋着的那笔清白积蓄，都是我当年当水手时为你存下的，里面没有一分沾着复仇的阴影。收下它，安度余生吧。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m06_28", "act3", "mercedes", "梅尔塞苔丝", "[crying] [softly] 爱德蒙，你真的……不会再恨我了吗？我们真的回不到一八一五年那个订婚的早晨了吗？", stability=0.0, gap_after_s=0.24),
        dlg("m06_29", "act3", "monte_cristo", "基督山伯爵", "[sighs] [softly] 我早就原谅你了，梅尔塞苔丝。只是那个十九岁的爱德蒙已经死在伊夫堡的海水里，而你我之间隔着整整二十四年的沧桑。别回头看，往前走，愿上帝保佑你和阿尔贝。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m06_30", "act3", "mercedes", "梅尔塞苔丝", "[softly] 再见了，爱德蒙。愿你也能找到真正属于你的幸福。", gap_after_s=0.34),
        # --- ACT 4: Monte Cristo Island — Maximilian & Valentine's Miraculous Reunion ---
        sfx("m06_31", "act4", "Warm golden Mediterranean sunset waves washing gently over smooth coastal pebbles beneath rocky cliffs with soft warm evening breeze, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.22),
        dlg("m06_32", "act4", "narrator", "史诗旁白", "十月五日傍晚，地中海基督山岛悬崖边。深信瓦朗蒂娜已死、痛不欲生的马克西米利安，如约来到伯爵面前。一个月前，伯爵曾与他定下约定：若三十天后仍想死，由伯爵亲手送他上路。", gap_after_s=0.26),
        dlg("m06_33", "act4", "albert_max", "马克西米利安·莫雷尔", "[crying] [hoarsely] 伯爵先生，三十天到了。这三十个日日夜夜，我盯着马赛的海平线，可没有瓦朗蒂娜的世界对我来说只是一片荒漠。请您履行承诺，把那勺让人无痛离去的东方药膏给我吧。", stability=0.0, gap_after_s=0.24),
        dlg("m06_34", "act4", "monte_cristo", "基督山伯爵", "[warmly] [calmly] 孩子，你父亲摩莱尔当年救过我的魂，今天我来还你一条命。吃下这一小匙翡翠绿膏，闭上眼睛，让温柔的海风带你去见你最想见的人。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m06_34b", "act4", "narrator", "史诗旁白", "马克西米利安含泪咽下那勺散发着薄荷清香的绿膏，渐渐靠在石椅上沉沉睡去。伯爵转身望向岩洞深处，轻轻一挥手——夕阳如金色的纱幔，漫过雪白的石阶。", gap_after_s=0.26),
        dlg("m06_35", "act4", "albert_max", "马克西米利安·莫雷尔", "[softly] 谢谢您，伯爵……我听见海浪声越来越远……奇怪，天堂里怎么会有地中海咸咸的风，还好像听见瓦朗蒂娜在喊我的名字……", gap_after_s=0.32),
        sfx("m06_36", "act4", "Light eager footsteps running softly across warm sand and smooth sea stone toward the edge of a sunlit cavern terrace with rustling white linen dress, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("m06_37", "act4", "haydee", "瓦朗蒂娜·德·维尔福", "[crying] [excited] 马克西米利安！醒一醒！这不是天堂，也不是梦——你摸摸我的手，它是暖的！是伯爵用假死药从毒妇手里救了我，把我悄悄送来这座岛上等你！", stability=0.0, gap_after_s=0.26),
        dlg("m06_38", "act4", "albert_max", "马克西米利安·莫雷尔", "[gasps] [crying] 瓦朗蒂娜？！你还活着？！我的天啊——你的心跳是真的，你的眼泪是滚烫的！伯爵先生，您在哪儿？快让我和瓦朗蒂娜跪谢您的大恩！", stability=0.0, gap_after_s=0.26),
        dlg("m06_38b", "act4", "haydee", "瓦朗蒂娜·德·维尔福", "[crying] [warmly] 别找了，马克西米利安……你看海湾外面那片金光，伯爵早就悄悄登船离开了。他把这座岛的钥匙、巴黎香榭丽舍的豪宅，还有这封信，全都留给了我们！", stability=0.0, gap_after_s=0.28),
        # --- ACT 5: Sailing Away with Haydee + "Wait and Hope" Epilogue ---
        sfx("m06_39", "act5", "White linen sails billowing briskly in fresh open Mediterranean sea wind with gentle wooden yacht prow slicing serene evening waves and distant gulls, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.22),
        dlg("m06_40", "act5", "narrator", "史诗旁白", "海湾深处，那艘洁白的快艇正迎着落日余晖破浪远行。甲板上，二十四年来第一次卸下所有冷酷伪装的伯爵，望着渐渐远去的荒岛，终于吐出了一口沉甸甸的浊气。", gap_after_s=0.28),
        dlg("m06_41", "act5", "haydee", "海黛公主", "[softly] [warmly] 主人，他们重逢了。您把半生寻回的宝藏和巴黎府邸都送给了那对年轻人，如今您不复仇了，我们这艘船要驶向哪里去呢？", gap_after_s=0.24),
        dlg("m06_41b", "act5", "monte_cristo", "基督山伯爵", "[sighs] [softly] 海黛，在维尔福府看见那个无辜孩子死去的一刻，我才真正明白法利亚神父的话——人可以追求公道，却永远不能代替上帝执掌生死。恨意烧了十四年，今天终于燃尽了。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m06_42", "act5", "monte_cristo", "基督山伯爵", "[warmly] [softly] 从今往后，别再叫我主人了，叫我爱德蒙吧。只要你愿意留在甲板上陪我吹风，前面这片无边无际的大海，就是我们的新家园。", acoustic_space="studio_warm", gap_after_s=0.26),
        dlg("m06_43", "act5", "haydee", "海黛公主", "[warmly] [crying] 爱德蒙……只要你在哪儿，光就在哪儿。无论去东方还是西方，我愿陪你走过余生的每一程风浪。", stability=0.0, gap_after_s=0.28),
        dlg("m06_44", "act5", "narrator", "史诗旁白", "而在金色悬崖之上，瓦朗蒂娜与马克西米利安紧紧相拥，含泪展开了基督山伯爵留下的最后那封信。海风拂过信纸，仿佛把那位历经地狱归来、最终学会爱与宽恕的灵魂的声音，永远留在了地中海的波涛之间——", gap_after_s=0.24),
        dlg("m06_45", "act5", "monte_cristo", "基督山伯爵", "[solemn] [softly] 亲爱的马克西米利安，请永远记住：这世上既无所谓永恒的幸福，也无所谓永恒的不幸，有的只是境况与境况的对比。", acoustic_space="memory_echo", gap_after_s=0.26),
        dlg("m06_46", "act5", "monte_cristo", "基督山伯爵", "[warmly] [solemn] 只有亲身经历过最深沉的绝望，才懂得品尝至高无上的喜悦。好好活下去，相爱吧，我的孩子们——", acoustic_space="memory_echo", gap_after_s=0.24),
        dlg("m06_47", "act5", "monte_cristo", "基督山伯爵", "[solemn] [softly] 永远不要忘记：在上帝向人类揭示未来真相的那一天到来之前，人类全部的智慧，都包含在这五个字里——等待，和希望。", acoustic_space="memory_echo", gap_after_s=0.45),
        dlg("m06_48", "act5", "narrator", "史诗旁白", "[dramatically] 《基督山伯爵·伊夫堡复仇广播剧》第一季全六集，到此圆满落幕。感谢您的倾听——愿你我穿越风浪之时，心头永怀等待与希望。", gap_after_s=0.80),
    ]
    return EpisodeCueSheet(
        episode_id="E006",
        chapter_number=6,
        title="罗马地窟天价烤鸡与尾声_等待和希望",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.4,
        acts=acts,
        cues=cues,
    )
