"""Season 1 Episodes E004–E006 for《1776爱丁堡夜话：〈国富论〉商业思想剧场》.

Flagship 15–18 minute anti-translationese (零翻译腔) historical intellectual radio drama adapted directly
from Adam Smith's 100% globally public-domain 1776 English original *The Wealth of Nations*:
- E004: 《看不见的手真相_资本流向与纸币空中公路》 (Book II & Book IV Ch. 2, ~3,150 CJK chars)
- E005: 《黄金不是财富_重商主义关税战与东印度公司毒药》 (Book IV, ~3,150 CJK chars)
- E006: 《守夜人的三张账单_政府边界与1776告别信》 (Book V & Smith–Hume 1776 Historical Farewell, ~3,150 CJK chars)
"""

from __future__ import annotations

from aigc_audio_pipeline.models import EpisodeCueSheet
from drama_helpers import act, dlg, motif, sfx


def build_e004_invisible_hand_capital() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·节俭实干者vs挥霍阔少：资本与人力资本真相", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
        act("act2", "第二幕·纸币是修在空中的高速公路与苏格兰信用透支", "market_ledger_debate", bgm_duration_s=75.0),
        act("act3", "第三幕·拨乱反正：原著里“看不见的手”到底在说什么", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
        act("act4", "第四幕·为什么官员替百姓拍板投资必然拍坏脑袋", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act5", "第五幕·1772苏格兰艾尔银行崩盘与金融防火墙铁律", "monopoly_trade_storm", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Capital accumulation + Fixed vs Circulating Capital + Human Capital ---
        motif("w04_01", "act1", "edinburgh_tavern_hearth", gap_after_s=0.20),
        dlg("w04_02", "act1", "narrator", "历史旁白", "[warmly] 第四夜，爱丁堡细雨敲窗。很多人读经济学最怕听见“固定资本”“流通资本”“资本积累”这些冷冰冰的译名。今晚，亚当·斯密只用两个邻居的故事，三分钟就把第二篇讲透。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_03", "act1", "host_su", "苏清禾", "[curious] 斯密教授，社会上老有两种针锋相对的说法：一种说大家拼命吃喝挥霍才能拉动消费，另一种说节俭攒钱买机器才能让国家富强。您到底站哪边？", gap_after_s=0.24),
        dlg("w04_04", "act1", "adam_smith", "亚当·斯密", "[warmly] 咱们看两个继承了同样一万英镑家产的苏格兰年轻人。第一个叫挥霍阔少，每天摆流水席、养五十个伺候他的闲仆、放烟花赌赛马，不到五年把一万镑败光，家里只剩一堆碎酒瓶。", gap_after_s=0.24),
        dlg("w04_05", "act1", "adam_smith", "亚当·斯密", "[calmly] 第二个叫节俭实干者，自己穿得朴素，省下八千英镑买织布机、修水车、雇熟练工匠织出源源不断的好呢绒。请注意——他省下的钱没锁进地窖发霉，而是立刻变成了工人的工资和会下蛋的金母鸡！", gap_after_s=0.24),
        sfx("w04_06", "act1", "Crisp wooden waterwheel turning rhythmically beside weaving looms clacking steadily in a thriving 18th-century Scottish textile mill, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("w04_07", "act1", "boss_macaulay", "老麦考利", "[earthy] 这账我一听就门儿清！阔少把钱花在一次性挥霍上，花完就没了，明年那五十个仆人都得失业；实干家把钱投进厂房和机器，今年养活五十个工人，明年赚了利润添机器，能养活一百个！", gap_after_s=0.24),
        dlg("w04_08", "act1", "adam_smith", "亚当·斯密", "[warmly] [solemn] 所以我说，每一个节俭攒本钱投入生产的人，都是全社会的恩人；而每一个挥霍祖产的败家子——哪怕自以为花钱大气——其实都在掏空国家的家底。", gap_after_s=0.24),
        dlg("w04_09", "act1", "host_su", "苏清禾", "[curious] 那您在书里把资本分成“固定资本”和“流通资本”，用老麦考利工厂打比方，到底指什么？", gap_after_s=0.22),
        dlg("w04_10", "act1", "adam_smith", "亚当·斯密", "[warmly] 简单极了！留在厂里帮着生钱的家当叫固定资本——比如厂房、水车、机器，还有极容易被忽视的一项：工匠和工程师苦学练就的一身真本事！这叫“人的资本”，走到哪儿都能生财！", gap_after_s=0.24),
        dlg("w04_11", "act1", "boss_macaulay", "老麦考利", "[earthy] 那周转流出去才能赚回来的——比如账上现金、库房里的铜条、货架上待卖的扣针盒——就是流通资本！固定资本没流通资本喂料转不起来，流通资本没固定资本又造不出效率！", gap_after_s=0.24),
        sfx("w04_11b", "act1", "Solo violin playing a brief bright classical flourish fading into quiet room applause and wooden chair creaking warmly, pure foley, no human voice", duration_seconds=2.3, gap_after_s=0.18),
        dlg("w04_11c", "act1", "david_hume", "大卫·休谟", "[chuckles] [wryly] 等等亚当，咱们丑话说前头！你在书里把干活的人分成“生产性劳动”和“非生产性劳动”，居然把国王、法官、歌剧名角，还有咱俩这样的哲学教授全划进了“非生产性”！你这不是骂咱们白吃饭吗？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_11d", "act1", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 哈哈，大卫别曲解我！“非生产性”绝不是说没用或不体面——好法官守护公道，好音乐抚慰人心，怎么会没用？", gap_after_s=0.22),
        dlg("w04_11e", "act1", "adam_smith", "亚当·斯密", "[calmly] 我只是从算家底的角度划一条线：铁匠打完锄头，明早锄头还在货架上能接着生财；可演说家和提琴手一收尾，声音当场就散在空气里，留不下明天可以复利滚雪球的实物资本。", gap_after_s=0.24),
        dlg("w04_11f", "act1", "adam_smith", "亚当·斯密", "[seriously] 所以国家必须掌握分寸：法官、军人、老师得养，可如果皇宫里养十万个吃闲饭的仪仗随从，却把种地造机器的实干人抽干了税，这个国家一定越过越穷！", gap_after_s=0.24),
        dlg("w04_12", "act1", "david_hume", "大卫·休谟", "[wryly] [chuckles] 说透了！民间百姓辛辛苦苦省下来、添砖加瓦攒出的社会家底，最怕碰上好大喜功、乱花民脂民膏的王室和官府！民间拼命挣，庙堂拼命造，才是国家衰败的头号病根。", acoustic_space="dry", gap_after_s=0.28),
        # --- ACT 2: Money as the Wheel of Circulation + Paper Money "Waggon-way through the Air" ---
        motif("w04_13", "act2", "brass_balance_coins", gap_after_s=0.20),
        dlg("w04_14", "act2", "apprentice_tom", "学徒汤姆", "[curious] 教授，既然资本这么重要，那是不是国家印的钱越多、街上流通的金币越多，咱们国家就越富呢？", acoustic_space="dry", gap_after_s=0.22),
        dlg("w04_15", "act2", "adam_smith", "亚当·斯密", "[calmly] 汤姆，千万别把“运货的车轮”当成“车上的货物”！周一我花一先令买老麦考利的扣针，周二他拿这枚先令买面包，周三面包师拿它买面粉——钱只是流转的大车轮，真正养活人的是面包和衣裳！", gap_after_s=0.24),
        dlg("w04_16", "act2", "host_su", "苏清禾", "[curious] 说到这儿，我就想起您书里对银行纸币打过一个美极了的比方，叫什么“修在天上的高速公路”？", gap_after_s=0.22),
        dlg("w04_17", "act2", "adam_smith", "亚当·斯密", "[warmly] 哈哈，对！一个国家光靠沉甸甸的金银币在市面上流通，就像修了一条宽阔的马车大道：路本身不长一粒麦子，却占了一大片好农田，每年买金银、磨损金银花钱极多。", gap_after_s=0.24),
        dlg("w04_18", "act2", "adam_smith", "亚当·斯密", "[calmly] 如果信誉极好的银行发行随时能兑现的纸币来代替绝大部分金币，就等于在半空中架起了一条高架大路！底下省出来的真金白银，可以拿去国外换回机器、原料和粮食，马路全变良田了！", gap_after_s=0.24),
        sfx("w04_19", "act2", "Crisp cotton bank notes counting briskly across a mahogany Scottish bank counter with ink stamp thumping softly, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w04_20", "act2", "james_watt", "詹姆斯·瓦特", "[excited] 这正是我们苏格兰近三十年突飞猛进的秘诀！格拉斯哥的商业银行推出“信用透支账户”，肯给守信用的小老板按需放款、随借随还！我造第一批蒸汽机样品没被资金卡死，全靠它周转！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_21", "act2", "adam_smith", "亚当·斯密", "[seriously] [coldly] 但是别高兴太早！空中公路固然省地，可一旦银行贪心乱印空头纸币、超出了社会真正需要的流通量，就像在风暴里绑着蜡做的翅膀飞上天——摔下来一定粉身碎骨！", gap_after_s=0.28),
        # --- ACT 3: The Real Meaning of the "Invisible Hand" ---
        sfx("w04_22", "act3", "Crisp leather-bound book pages turning calmly beside a crackling fireplace and gentle antique pocket watch ticking on an oak desk, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("w04_23", "act3", "narrator", "历史旁白", "话题转入整本《国富论》最家喻户晓、也最常被断章取义的四个字——“看不见的手”。其实整部近千页的《国富论》里，这个词只出现过短短一次，却照亮了人类社会运转最深邃的奇迹。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_24", "act3", "host_su", "苏清禾", "[curious] 斯密教授，现在一提起“看不见的手”，有人把它吹成万能魔法，也有人骂它鼓励坑蒙拐骗、弱肉强食。您原书里写下这句话时，到底在讨论什么场景？", gap_after_s=0.24),
        dlg("w04_25", "act3", "adam_smith", "亚当·斯密", "[warmly] [seriously] 先把前提钉死：我说的市场，永远建立在公平法治、守信用、不许偷抢欺诈的底线之上！谁敢造假坑人，那是警官和法官该抓的罪犯，跟我说的市场半毛钱关系没有。", gap_after_s=0.24),
        dlg("w04_26", "act3", "adam_smith", "亚当·斯密", "[calmly] 守住规矩之后，神奇的事发生了：每个生意人拿着自己的血汗钱，天天绞尽脑汁琢磨把钱投在哪儿最安全、最值钱、最受顾客欢迎。他心里想的并不是“我要拯救全人类”，他只想把自家生意做红火。", gap_after_s=0.24),
        dlg("w04_27", "act3", "adam_smith", "亚当·斯密", "[warmly] 可在公平竞争下，你想多赚钱，唯一出路就是造出质量更好、价钱更实在、老百姓最急需的好货！于是他就像被一只“看不见的手”牵着，本意只顾自家饭碗，结果却比成天喊口号多帮了社会十倍的忙！", gap_after_s=0.24),
        dlg("w04_28", "act3", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 哎哟，太贴切了！我倒最怕那种天天高喊“我做生意不为赚钱、全是为了做公益”的滑头家伙——我活了半辈子见过，嘴上全是仁义道德的大商人，背地里坑起人来最狠！", gap_after_s=0.24),
        dlg("w04_29", "act3", "adam_smith", "亚当·斯密", "[chuckles] [wryly] 你抢了我原书里的原话！我在《国富论》里白纸黑字写过：“我从来没见过那些假装为了公众利益而做生意的人，真的干出过什么好事！”", gap_after_s=0.28),
        # --- ACT 4: Why bureaucrats cannot direct private capital ---
        sfx("w04_30", "act4", "Heavy brass wax seal stamping solemnly onto thick official parchment decree on a cavernous government mahogany table, pure foley, no human voice", duration_seconds=2.3, gap_after_s=0.18),
        dlg("w04_31", "act4", "merchant_lord", "东印度商董", "[condescending] 教授，就算普通人懂自己家一亩三分地，可国家大事格局太大！难道不该由伦敦议会最有远见的政治家，统一规定老百姓的钱该投农业、该投造船，还是该投纺织吗？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_32", "act4", "adam_smith", "亚当·斯密", "[coldly] [seriously] 商董，这是全书最危险的幻想！坐在伦敦办公桌前的大臣，能比格拉斯哥每天摸着棉纱和账本的老麦考利，更懂哪块地适合建厂、哪款布料今年好卖吗？", gap_after_s=0.24),
        dlg("w04_33", "act4", "adam_smith", "亚当·斯密", "[solemn] 哪位政治家如果胆敢替千千万万老百姓决定怎么花自己的本钱，第一是瞎忙活、管根本管不过来的细账；第二是揽下极其危险的权力——这权力交到任何一个人、哪怕一个委员会手里，都绝不安全！", gap_after_s=0.24),
        dlg("w04_34", "act4", "david_hume", "大卫·休谟", "[solemn] 而且把权力交给那些自以为聪明绝顶、觉得自己有资格替天下人做主的狂妄之徒，简直是灾难请柬！老麦考利投错了赔的是自己家底，所以夜里反复核账；大臣拍错脑袋，赔的全是纳税人的钱！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_34b", "act4", "merchant_lord", "东印度商董", "[curious] 等等，那利息高低总跟国家白银多少有关吧？西班牙抢来那么多白银，按理说银子多到溢出来，借钱利息就该便宜得像白送呀？", acoustic_space="dry", gap_after_s=0.22),
        dlg("w04_34c", "act4", "david_hume", "大卫·休谟", "[chuckles] [warmly] 这问题我在二十年前就专门写论文戳穿过，亚当也彻底赞同！印钞票或抢白银只会让物价跟着水涨船高，根本降不下真实利息！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_34d", "act4", "adam_smith", "亚当·斯密", "[calmly] 真实利息怎么降下来？全靠全社会日积月累攒出雄厚的真实资本——厂房多了、资金充裕了、借钱放贷的银行互相竞争，利息自然走低，像荷兰阿姆斯特丹那样借钱只需两三厘！", gap_after_s=0.24),
        dlg("w04_34e", "act4", "boss_macaulay", "老麦考利", "[earthy] 懂了！利息低是一个国家实业家底厚的“结果”，不是印钞机狂印钞票变出来的“魔术”！", gap_after_s=0.24),
        dlg("w04_35", "act4", "host_su", "苏清禾", "[warmly] 听完这段我瞬间串起来了！原来两百年后哈耶克写《通往奴役之路》，核心思想火种早就埋在斯密教授一七七六年这一页里啦！", gap_after_s=0.28),
        # --- ACT 5: The Ayr Bank Collapse Warning (1772 Real Financial Crisis!) + Firewall Metaphor ---
        sfx("w04_36", "act5", "Heavy angry pounding on bolted wooden bank doors in rain-swept 1772 Edinburgh street with hurried footsteps and rustling worthless paper bank notes, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.20),
        dlg("w04_37", "act5", "narrator", "历史旁白", "谈到金融失控，屋里所有苏格兰人都脸色一沉——就在四年前的一七七二年，轰动全英的苏格兰“艾尔银行”一夜崩盘，差点把半个苏格兰贵族拉进破产深渊，连斯密本人都被请去救急善后。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_38", "act5", "boss_macaulay", "老麦考利", "[sighs] [earthy] 别提那场大祸了！艾尔银行当年胆子大破天，谁来借钱炒地皮、玩空手套白狼，它就闭着眼睛疯狂印钞票放贷！", gap_after_s=0.24),
        dlg("w04_39", "act5", "james_watt", "詹姆斯·瓦特", "[angry] 最荒唐的是他们自己玩“左手倒右手”循环开空头汇票！拿伦敦新债还爱丁堡旧债，利息滚利息，空转了不到三年，挤兑潮一来直接关门大吉，好多老实办厂的朋友跟着破产！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w04_40", "act5", "host_su", "苏清禾", "[pushback] 那您刚才反对官员管投资，碰到银行乱加杠杆、搞空头金融泡沫，您赞成政府定规矩管一管吗？", gap_after_s=0.22),
        dlg("w04_41", "act5", "adam_smith", "亚当·斯密", "[seriously] 百分之百赞成！自由市场绝不等于放任银行胡乱印钞！我主张禁止银行随便印超小面额纸币坑害底层穷人，并且必须守住随时足额兑现的铁律！", gap_after_s=0.24),
        dlg("w04_42", "act5", "adam_smith", "亚当·斯密", "[solemn] [warmly] 有人骂这是限制自由，我说：城里盖房子，法律强制要求每栋楼之间必须砌一道结实的防火墙！这是限制盖房自由吗？不，是防止一家失火烧光整条街！金融监管，就是现代商业的防火墙！", gap_after_s=0.26),
        dlg("w04_43", "act5", "host_su", "苏清禾", "[warmly] 原来斯密教授既反官僚瞎指挥，又反金融瞎印钱！不过今天东印度商董一直憋着大招呢——明天晚上，咱们正面硬刚全书火力最猛的一章：重商主义、贸易顺差和关税大战！", gap_after_s=0.24),
        dlg("w04_44", "act5", "narrator", "历史旁白", "[warmly] 下一集，《黄金不是财富：重商主义、关税战与东印度公司毒药》。两百五十年前的这场贸易交锋，今天听来依然字字惊心！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E004",
        chapter_number=4,
        title="看不见的手真相_资本流向与纸币空中公路",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e005_gold_illusion_trade_wars() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·西班牙白银越抢越穷：戳破重商主义大谎", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act2", "第二幕·苏格兰玻璃暖房种葡萄：关税战的荒唐账", "market_ledger_debate", bgm_duration_s=75.0),
        act("act3", "第三幕·消费是唯一目的与出口补贴如何扒老百姓两层皮", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act4", "第四幕·东印度公司毒药与“花别人的钱”的官僚病", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act5", "第五幕·1776北美战火预言：与其养昂贵帝国不如自由通商", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Attacking Mercantilism — Gold is NOT wealth! ---
        motif("w05_01", "act1", "merchant_port_harbor", gap_after_s=0.22),
        dlg("w05_02", "act1", "narrator", "历史旁白", "[dramatically] 第五夜，爱丁堡风大浪急。今晚交锋的主角，是统治欧洲足足两百年的主流经济国策——“重商主义”。东印度商董拍案而起，和斯密、休谟展开了一场跨越两百五十年不过时的贸易激辩。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_03", "act1", "merchant_lord", "东印度商董", "[condescending] 各位！做国际贸易就像打仗，一方赢必然有一方输！英国要想强盛，就必须拼命多卖货、少买外国货，把全世界的黄金白银全赚进伦敦国库！绝不能让外国丝绸和红酒把咱们的金子换走！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_04", "act1", "david_hume", "大卫·休谟", "[chuckles] [sarcastic] 商董这番话，听着就像个只认死钱的守财奴！照你这么说，全欧洲黄金白银囤得最多的是西班牙和葡萄牙——他们从美洲抢了满船满船的银山回来，怎么如今反而成了欧洲最穷的国家？", acoustic_space="dry", gap_after_s=0.24),
        sfx("w05_05", "act1", "Heavy wooden treasure chest lid slamming open with dull clatter of piled silver ingots inside a cold stone vault, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w05_06", "act1", "adam_smith", "亚当·斯密", "[calmly] [seriously] 因为他们把“饭票”当成了“饭菜”！黄金白银充其量只是买东西的工具，就像厨房里的锅碗瓢盆。一个家庭变富，难道是因为家里堆了一万口空锅，还是因为锅里每天煮着香喷喷的饭菜？", gap_after_s=0.24),
        dlg("w05_07", "act1", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 哎哟，这比方绝了！要是你把英国所有出口换来的全锁成金条不准买外国货，国内物价蹭蹭暴涨，最后老百姓揣着一大把金子却买不着便宜好衣裳，那不是发财，那是抱着金砖挨饿！", gap_after_s=0.24),
        dlg("w05_08", "act1", "host_su", "苏清禾", "[curious] 这么一想，“贸易逆差吃亏论”也很滑稽呀！我每天去楼下菜市场买菜，我只付钱、菜贩只给菜，我跟菜市场天天都是“贸易逆差”，难道是我每天都在被菜贩剥削吗？", gap_after_s=0.24),
        dlg("w05_09", "act1", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 妙极了！清禾一眼看穿了本质！贸易不是零和搏杀，而是双向共赢：你拿你多出来的钱换走了更想要的鲜菜，菜贩拿走了进货钱，两个人都比交易前过得更好！", gap_after_s=0.24),
        dlg("w05_09b", "act1", "david_hume", "大卫·休谟", "[wryly] [chuckles] 更滑稽的是西班牙国王下死命令禁止白银出口，抓到就杀头！结果呢？白银体积小价值高，商人们照样用双层木箱偷偷运出去，只不过多付了一笔走私风险费，把自家老实商人坑惨了！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_10", "act1", "adam_smith", "亚当·斯密", "[warmly] 拦住金银就像筑一道矮墙想挡住洪水——只要院外有更便宜的好货，银子早晚从墙缝渗出去！真正衡量国家富不富，从来不是国库锁了多少吨金子，而是老百姓每年能享用到多少衣食住行！", gap_after_s=0.28),
        # --- ACT 2: Scottish Greenhouse Grapes + Tariffs & Trade War Nuance ---
        sfx("w05_11", "act2", "Cold howling Scottish winter wind tapping against glass conservatory panes while cork pops cleanly from a fine French wine bottle inside a warm parlor, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("w05_12", "act2", "merchant_lord", "东印度商董", "[angry] 一派胡言！如果我们不对法国葡萄酒、中国茶叶和国外纺织品加高额关税，咱们本土的手工作坊岂不都要被外国便宜货冲垮？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_13", "act2", "adam_smith", "亚当·斯密", "[wryly] [chuckles] 商董，我问你个最简单的家常问题：任何一个精明过日子的家长，都会遵循一条常识——如果外面买一样东西比自己在家费劲巴拉造便宜得多，千万别傻到自己硬造！", gap_after_s=0.24),
        dlg("w05_14", "act2", "adam_smith", "亚当·斯密", "[warmly] 裁缝不自己做皮鞋，去鞋匠那儿买；鞋匠不自己缝大衣，去裁缝那儿买；大伙儿把力气花在自己最拿手的活计上，拿赚来的钱互相买对方最好的货——小家庭如此，大国通商难道不是同一个道理？", gap_after_s=0.24),
        dlg("w05_15", "act2", "adam_smith", "亚当·斯密", "[chuckles] [sarcastic] 咱们苏格兰又冷又湿，按商董的关税逻辑，咱们完全可以禁止进口法国红酒，然后在爱丁堡冰天雪地里花天价盖玻璃暖房、烧煤取暖种葡萄，酿出极酸的苏格兰红酒——成本是法国货的三十倍！", gap_after_s=0.26),
        dlg("w05_16", "act2", "host_su", "苏清禾", "[chuckles] [curious] 哈哈，拿三十倍价钱在苏格兰暖房里种酸葡萄！为了保住几个暖房老板的生意，逼全英国老百姓花三十倍冤枉钱喝酸酒，这也太荒唐了吧！", gap_after_s=0.24),
        dlg("w05_17", "act2", "adam_smith", "亚当·斯密", "[seriously] 可各国议会每天都在批的保护性关税，干的不正是“苏格兰暖房种葡萄”的蠢事吗？关税壁垒没让国家多出一分钱总财富，只是硬把原本能干高效产业的资金工人，赶进低效温室里吃补贴！", gap_after_s=0.24),
        dlg("w05_18", "act2", "james_watt", "詹姆斯·瓦特", "[curious] 教授，那您对关税是一刀切全盘反对吗？如果事关国防安全，比如战时必须有自己的商船队和海军水手，或者别国先对咱们加税呢？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_19", "act2", "adam_smith", "亚当·斯密", "[solemn] 我从不是书呆子！国防安全永远比发财更重要，所以保护本土水手和国防关键产业的法令，我点点头认可。至于关税报复战？只有确实能逼对方拆关税时才值得一试，否则只是把自家百姓再罚一道税！", gap_after_s=0.24),
        dlg("w05_20", "act2", "david_hume", "大卫·休谟", "[warmly] [solemn] 邻居变富，绝不是我们的灾难！富邻居才买得起我们的羊毛呢绒和蒸汽机；四周全是穷光蛋，咱们卖货给谁去？所以我一直祈祷法国、德国、西班牙全都能富起来！", acoustic_space="dry", gap_after_s=0.28),
        # --- ACT 3: Consumption is the sole end + Export Bounties double-taxing citizens ---
        sfx("w05_21", "act3", "Heavy burlap grain sacks thudding onto wooden dockside cargo pallets beside bustling British port customs stamp, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w05_22", "act3", "host_su", "苏清禾", "[curious] 教授，既然道理这么清楚，为什么两百年来关税战和垄断法令照样一层叠一层、怎么也拆不掉呢？", gap_after_s=0.22),
        dlg("w05_23", "act3", "adam_smith", "亚当·斯密", "[coldly] [solemn] 因为消费者千千万万、散落在千家万户，谁也不会为了每斤糖贵两分钱专门坐马车去伦敦议会游说；而少数垄断大商人和厂主攥着巨款、住得离议会近、声音响亮，天天往大臣耳朵里灌迷魂汤！", gap_after_s=0.26),
        dlg("w05_24", "act3", "boss_macaulay", "老麦考利", "[angry] [earthy] 最气人的是那个“小麦出口补贴”！大伙儿听听多离谱：英国政府拿咱们交的税钱去补贴粮商，把英国好小麦赔本贱卖给法国人，搞得伦敦穷人买面包反而比法国人还贵！", gap_after_s=0.24),
        dlg("w05_25", "act3", "apprentice_tom", "学徒汤姆", "[gasps] [angry] 啥？！拿咱们的税钱贴补外国人吃便宜面包，再让我们自己高价啃干硬黑面包？！这是图啥呀？", stability=0.0, acoustic_space="dry", gap_after_s=0.22),
        dlg("w05_25b", "act3", "adam_smith", "亚当·斯密", "[coldly] 还有更血腥的！英国呢绒大厂主为了把本土羊毛价格压到泥巴里，竟然游说议会立下恶法：谁敢把活羊或生羊毛卖到国外，初犯剁掉左手钉在集市柱子上，再犯直接判死刑！", gap_after_s=0.24),
        dlg("w05_25c", "act3", "host_su", "苏清禾", "[gasps] [seriously] 我的天，就为了压低原料进价，居然用酷刑堵死牧羊农夫的活路？！难怪您在书里说这些法规简直是用血写成的！", gap_after_s=0.24),
        dlg("w05_26", "act3", "adam_smith", "亚当·斯密", "[solemn] [warmly] 听见老百姓的怒火了吧？请每位听众牢牢记住《国富论》里最振聋发聩的一句话：消费，是一切生产的唯一目的！重商主义偏偏反过来，把全体百姓的钱包当祭品，供养一小撮垄断大鳄！", gap_after_s=0.28),
        # --- ACT 4: Indicting East India Company + "Other People's Money" Principal-Agent Insight ---
        sfx("w05_27", "act4", "Heavy wooden war cannons rumbling distantly across ocean waves followed by harsh brass ledger lock slamming shut in a grand colonial trading house, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("w05_28", "act4", "merchant_lord", "东印度商董", "[angry] [fiercely] 斯密教授！你越界了！我们东印度公司替大英帝国开拓了整个印度贸易，手握皇家特许垄断权，养着自己的舰队和军队，你敢说我们不是帝国功臣？", stability=0.0, acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_29", "act4", "adam_smith", "亚当·斯密", "[coldly] [fiercely] 你们恰恰是全世界最糟糕的怪物——既是垄断贸易的奸商，又手握生杀大权的统治者！当统治者本该盼着老百姓富裕，可当垄断奸商只盼着低价搜刮、高价倒卖！", stability=0.0, gap_after_s=0.24),
        dlg("w05_30", "act4", "adam_smith", "亚当·斯密", "[solemn] 东印度公司在孟加拉干了什么？为了炒高大米和香料价格，竟然强逼农夫毁掉农田、垄断收购，活活酿成惨绝人寰的大饥荒！与此同时，你们公司内部贪腐丛生、连年靠英国纳税人填窟窿——这叫功臣还是寄生虫？", gap_after_s=0.26),
        dlg("w05_31", "act4", "david_hume", "大卫·休谟", "[wryly] [seriously] 亚当还一针见血点破了这类特许巨头烂到根里的病灶：大公司董事管的是千千万万股东的钱，不是自己的钱！管别人钱的人，哪会像私企老板盯自己血汗钱那样精打细算？没了竞争对手，浪费和傲慢必成绝症！", acoustic_space="dry", gap_after_s=0.26),
        dlg("w05_32", "act4", "boss_macaulay", "老麦考利", "[earthy] [angry] 说得太痛快了！一边拿着皇家护身符不准咱们小商人去印度做正经生意，一边亏了钱还要全英国老百姓交税替他们兜底，天下哪有这么占便宜的好事！", gap_after_s=0.24),
        sfx("w05_32b", "act4", "Calm wooden cargo barge gliding smoothly along a wide river canal with gentle lapping water and distant wooden oars dipping steadily, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("w05_32c", "act4", "host_su", "苏清禾", "[curious] 教授，我翻英文原版第四篇时特别惊喜，发现您在一七七六年专门花了不少笔墨写到遥远的东方中国！您当年是怎么评价中国的？", gap_after_s=0.24),
        dlg("w05_32d", "act4", "adam_smith", "亚当·斯密", "[warmly] [solemn] 我对中国的广袤富庶佩服至极！我在书里写得很清楚：中国土地肥沃、百姓勤劳无比、大运河与长江水网纵横交错，光是国内统一大市场，体量就顶得上整个欧洲所有国家加起来！", gap_after_s=0.24),
        dlg("w05_32e", "act4", "adam_smith", "亚当·斯密", "[seriously] 我唯一替中国惋惜的，就是当时朝廷轻视海外远洋通商、关上国门只留一两个口岸。如果如此勤劳聪明的民族能敞开大门、与全世界自由做买卖、互学先进机器和造船术，那股爆发出的财富力量将不可限量！", gap_after_s=0.24),
        dlg("w05_32f", "act4", "host_su", "苏清禾", "[warmly] 两百多年后回头再听您这句忠告，真让人起一身鸡皮疙瘩——您几乎精准预言了改革开放后中国制造业与大市场腾飞的全部密码！", gap_after_s=0.28),
        # --- ACT 5: 1776 Prophetic Warning on American Colonies ---
        sfx("w05_33", "act5", "Distant muffled London street footsteps running past rain-slicked cobblestones with crisp newspaper sheets rustling urgently, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w05_34", "act5", "narrator", "历史旁白", "窗外街巷忽然传来急促的报童脚步声——大西洋彼岸枪声已响。写完这些文字四个月后，一七七六年七月四日，北美发表了《独立宣言》。而斯密早在全面开战前，就在书里写出了最清醒的忠告。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_35", "act5", "adam_smith", "亚当·斯密", "[solemn] 为了死攥住殖民地垄断贸易权，英国花掉的军费和国债远远超过了贸易赚回来的零头。大帝国的虚荣心既昂贵又荒谬——倒不如体体面面放北美自主，签一份平等自由通商条约，少花军费、照做大买卖，两头得利！", gap_after_s=0.24),
        dlg("w05_35b", "act5", "adam_smith", "亚当·斯密", "[seriously] 更险的是，把全国资金硬逼进殖民地这一条垄断独木桥，就像一个人浑身只剩一根畸形粗大的血管！平时看着红光满面，一旦海外战火一断流，整国经济瞬间休克！", gap_after_s=0.24),
        dlg("w05_35c", "act5", "james_watt", "詹姆斯·瓦特", "[warmly] 反过来，如果跟全世界几十个国家平等自由通商，条条血管细密通畅，哪一条偶遇风浪，其余几十条照样活蹦乱跳！多元化市场，才是最硬的抗风险护甲！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_35d", "act5", "david_hume", "大卫·休谟", "[chuckles] [warmly] 亚当这句预言，怕是百年之后各国商界领袖依然得刻在书桌上反复背诵！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w05_36", "act5", "host_su", "苏清禾", "[warmly] 听到这儿我彻底服气了。您把重商主义、垄断行会、官僚瞎指挥批了个底朝天——那听众肯定要问终极问题：既然您这么反对政府乱插手，那政府到底还有啥存在的必要？", gap_after_s=0.24),
        dlg("w05_37", "act5", "adam_smith", "亚当·斯密", "[warmly] 千万别把我当成什么都不要的无政府主义者！明天收官夜，我给政府开出三张绝对推脱不掉的硬账单——再陪我送别一位走完此生的老朋友。", gap_after_s=0.24),
        dlg("w05_38", "act5", "narrator", "历史旁白", "[warmly] 大结局，《守夜人的三张账单：政府边界与1776告别信》。市场如何变富，法治与同情心又如何让世界变暖？敬请收听最终章！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E005",
        chapter_number=5,
        title="黄金不是财富_重商主义关税战与东印度公司毒药",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e006_night_watchman_1776_farewell() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·守夜人的三件必做大事：国防、司法与公共基建", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
        act("act2", "第二幕·斯密的惊人远见：平民基础学堂与牛津教授懒政", "glasgow_workshop_vigor", bgm_duration_s=75.0),
        act("act3", "第三幕·好税法四铁律、荒唐窗户税与国债警示", "market_ledger_debate", bgm_duration_s=75.0),
        act("act4", "第四幕·1776年夏爱丁堡病榻：斯密与休谟最后夜话", "north_sea_farewell_warmth", bgm_duration_s=75.0),
        act("act5", "第五幕·北海晚风终章：国富论与道德情操论的双翼", "north_sea_farewell_warmth", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: The Three Duties of the Sovereign (Book V) ---
        motif("w06_01", "act1", "edinburgh_tavern_hearth", gap_after_s=0.20),
        dlg("w06_02", "act1", "narrator", "历史旁白", "[warmly] 终章之夜。一七七六年夏末，爱丁堡晚风带着北海的咸味。《国富论》已经洛阳纸贵，而最难得的是，斯密在全书最后整整一篇里，亲手画出了政府权力的清晰红线——既不准越界乱管，也不准甩手不管。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_03", "act1", "host_su", "苏清禾", "[curious] 斯密教授，您刚才说政府有三张推脱不掉的硬账单，也就是后世常说的“守夜人”职责。哪三件事，是市场自己干不好、非得公家出手托底不可的？", gap_after_s=0.24),
        dlg("w06_04", "act1", "adam_smith", "亚当·斯密", "[calmly] [seriously] 第一件，保家卫国。一个富得流油却没有精良防务的国家，就像怀里揣满金砖走在强盗林里的富商，迟早招祸。现代战争装备和常备军极烧钱，只能由全社会共同分摊国防开销。", gap_after_s=0.24),
        sfx("w06_05", "act1", "Crisp wooden magistrate gavel tapping firmly once in a quiet stone courtroom with respectful hushed ambience, pure foley, no human voice", duration_seconds=2.2, gap_after_s=0.18),
        dlg("w06_06", "act1", "adam_smith", "亚当·斯密", "[seriously] 第二件，独立公正的司法裁判。市场繁荣全靠产权安稳和契约算数！如果地痞敢抢铺子、权贵敢赖账、法庭听国王脸色判案，那再聪明的生意人也会卷铺盖逃跑。法官必须手握铁饭碗、独立于权贵！", gap_after_s=0.24),
        dlg("w06_07", "act1", "boss_macaulay", "老麦考利", "[earthy] 没错！只要官府帮我守住两条——外头没人来抢、里头欠债必须还钱、告状有青天大老爷讲理，那剩下的怎么做扣针、卖多少钱，就让我们老百姓放开手脚自己拼去！", gap_after_s=0.24),
        dlg("w06_08", "act1", "adam_smith", "亚当·斯密", "[warmly] 别漏了极其关键的第三件——修建并维护那些对全社会功德无量、但单个私人商贩算不过账、无力单独承担的公共工程与公共设施！", gap_after_s=0.24),
        dlg("w06_09", "act1", "james_watt", "詹姆斯·瓦特", "[excited] 比如贯通城乡的大公路、跨河石桥、深水运河和灯塔海港！我造出再好的蒸汽机，要是出门全是齐膝深的泥巴烂路，货根本运不出去！修路搭桥，是给全社会市场扩容的超级底座！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_10", "act1", "adam_smith", "亚当·斯密", "[warmly] 甚至在收费方式上我都有巧思：修桥铺路尽量按过路车马轻重收合理过桥费，让真正用路的商旅分摊修路钱，这样官府就不会为了巴结权贵，把纳税人的钱浪费在荒无人烟的贵族私路上！", gap_after_s=0.24),
        dlg("w06_10b", "act1", "host_su", "苏清禾", "[curious] 那如果是朝廷自己直接下场办商业农场、开国营大商行，您觉得能干过民间商人吗？", gap_after_s=0.22),
        dlg("w06_10c", "act1", "adam_smith", "亚当·斯密", "[wryly] [chuckles] 除了邮政这种流程极其单一、当天收钱当天办事的公用行当，政府下场做正经商业几乎百战百败！英国王室占着大片皇家林地和官办农场，连年亏钱，倒不如拍卖给民间农夫，收的税收比自己硬种高出三倍！", gap_after_s=0.28),
        # --- ACT 2: Public Education for Workers + Oxford vs Scottish Professors Roast ---
        motif("w06_11", "act2", "pin_factory_clatter", gap_after_s=0.20),
        dlg("w06_12", "act2", "host_su", "苏清禾", "[curious] 教授，您书里第五篇还有一段特别让人动容的话——您第一章把扣针厂分工夸上了天，可到了第五篇，您竟然亲自担心起了流水线工人的头脑？", gap_after_s=0.24),
        dlg("w06_13", "act2", "adam_smith", "亚当·斯密", "[solemn] [warmly] 观察得真细！一个人如果一辈子每天十二个小时只重复两个机械动作——比如只把铜丝截断、只敲一下针帽，从来不动脑筋解决新难题，久而久之，他的想象力、判断力和见识就会慢慢锈死麻木。", gap_after_s=0.24),
        dlg("w06_14", "act2", "apprentice_tom", "学徒汤姆", "[sighs] 教授您说到我心坎里了……我表哥在作坊里拧了十年铜帽，现在除了拧帽啥也不懂，连告示上的字都认不全，别人拿假账单骗他他都看不出来。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_15", "act2", "adam_smith", "亚当·斯密", "[solemn] [warmly] 这就是极度分工的隐蔽代价！富家子弟请得起私教，穷孩子八九岁就得进厂。因此政府必须花一小笔公款，在每个教区办平价基础学堂，让所有普通人家的孩子都学会识字、算账和基础几何！", gap_after_s=0.24),
        dlg("w06_16", "act2", "adam_smith", "亚当·斯密", "[warmly] 一个人人识字明理的社会，老百姓既不容易被骗子和狂热分子忽悠煽动，又能把分工红利稳稳接在手里——这笔平民教育投资，是一个国家最划算的买卖！", gap_after_s=0.24),
        sfx("w06_17", "act2", "Chalk writing briskly on a slate classroom board with crisp school bell chiming faintly in a stone Scottish village hall, pure foley, no human voice", duration_seconds=2.3, gap_after_s=0.18),
        dlg("w06_18", "act2", "david_hume", "大卫·休谟", "[chuckles] [wryly] 哈哈，清禾你还不知道吧？亚当在第五篇还顺手把母校牛津大学的教授们狠狠损了一顿！你问问他当年在牛津读书气成啥样！", acoustic_space="dry", gap_after_s=0.22),
        dlg("w06_19", "act2", "adam_smith", "亚当·斯密", "[chuckles] [sarcastic] 哎，牛津教授拿着旱涝保收的丰厚基金铁饭碗，讲得好不好全拿一样的高薪，结果好多人十几年连假装讲课都懒得演！反观咱们苏格兰大学，教授一半收入靠学生掏腰包选课，谁不拼命把课讲精彩？", gap_after_s=0.26),
        dlg("w06_20", "act2", "host_su", "苏清禾", "[chuckles] [warmly] 哈哈，好家伙！哪怕办教育，斯密教授也不忘把“激励机制”设计得明明白白——公家出钱建校舍兜底，老师凭真本事和口碑赢学生！", gap_after_s=0.24),
        dlg("w06_20b", "act2", "adam_smith", "亚当·斯密", "[warmly] 除此之外，我还提倡给普通人多留点体面的娱乐——戏剧演出、音乐会、科普讲座！一个社会如果只剩苦役和枯燥说教，人们心里憋出戾气，就容易轻信极端狂热分子！", gap_after_s=0.24),
        dlg("w06_20c", "act2", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 这话说得太暖心了！干完活儿有书读、有戏看、有酒喝，日子过得热热闹闹，谁还闲着没事去搞极端呀！", gap_after_s=0.28),
        # --- ACT 3: Four Canons of Taxation + Absurd Window Tax + Public Debt Warning ---
        sfx("w06_21", "act3", "Masonry bricks clinking and trowel scraping wet mortar sealing a stone cottage window shut in an 18th-century British lane, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w06_22", "act3", "boss_macaulay", "老麦考利", "[earthy] 既然政府要办国防、司法、修桥铺路、办基础学堂，钱总得从税收来。教授，大伙儿最怕苛捐杂税，怎么收税才算讲规矩、不把生意人逼跑？", gap_after_s=0.24),
        dlg("w06_23", "act3", "adam_smith", "亚当·斯密", "[calmly] 就四条大白话铁律，今天全世界财政部还在照着念！第一条叫“公平”——谁在国家保护下赚得多，谁就按比例多出一份，能力越大责任越大。", gap_after_s=0.24),
        dlg("w06_24", "act3", "adam_smith", "亚当·斯密", "[seriously] 第二条叫“确定”——什么时候交、交多少、怎么交，必须白纸黑字写死公开！税法最怕含糊其辞、让税吏随口乱要价！哪怕税率稍重但规矩透明，危害也远小于糊涂税法任由官吏敲诈！", gap_after_s=0.24),
        dlg("w06_25", "act3", "adam_smith", "亚当·斯密", "[warmly] 第三条叫“便利”，挑老百姓手里刚进账、最方便时收；第四条叫“省心高效”，别雇十万税官吃光半数税银，更别发明像“窗户税”那样蠢到家的税——税吏按窗户数收税，穷人只好拿砖头把窗封死，活在黑屋子里！", gap_after_s=0.24),
        sfx("w06_25b", "act3", "Quiet midnight rowing oars dipping stealthily through coastal cove waves with heavy wooden tea casks clunking softly onto wet shingle beach, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("w06_25c", "act3", "apprentice_tom", "学徒汤姆", "[angry] 还有盐税、肥皂税和蜡烛税！富人吃盐跟咱们穷人吃盐差不多，可给盐和蜡烛加满重税，不等于专掏咱们穷苦人家的裤兜吗？", acoustic_space="dry", gap_after_s=0.22),
        dlg("w06_25d", "act3", "adam_smith", "亚当·斯密", "[solemn] [seriously] 汤姆说出了大公道！对盐、皮靴、肥皂和蜡烛这些生活必需品征重税，是世上最不公的累退税！而对茶叶、白兰地设下天价关税，更会活活造出一大批武装走私帮派！", gap_after_s=0.24),
        dlg("w06_25e", "act3", "david_hume", "大卫·休谟", "[wryly] [seriously] 最讽刺的是，原本本分老实的沿海渔民，被荒唐重税逼成了走私犯；而老百姓买便宜走私茶时非但不恨他们，反而人人替走私贩打掩护——坏税法不仅少收钱，还顺手败坏了全社会的守法风气！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_26", "act3", "merchant_lord", "东印度商董", "[sarcastic] 那要是打仗花钱如流水、税收不够呢？咱们伦敦金融城乐意借给政府巨额国债嘛！", acoustic_space="dry", gap_after_s=0.22),
        dlg("w06_27", "act3", "adam_smith", "亚当·斯密", "[coldly] [solemn] 举债一时爽，债台高筑后，几乎没有哪个大帝国能凭良心实打实还清过巨额国债——最后要么加税压垮实业，要么偷偷让货币贬值赖账。别把今天的挥霍，悄悄甩给还没出生的孙子辈去还！", gap_after_s=0.28),
        # --- ACT 4: August 1776 — Real Letters & Farewell to Dying Best Friend David Hume ---
        sfx("w06_28", "act4", "Soft late-summer Scottish twilight breeze rustling quiet bedroom curtains beside a slow rhythmic wooden clock and faint crackling hearth embers, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.22),
        dlg("w06_29", "act4", "narrator", "历史旁白", "[softly] 一七七六年八月，《国富论》问世仅仅五个月。爱丁堡圣大卫街一间安静的卧房里，亚当·斯密相交二十六年的生死挚友大卫·休谟，走到了生命的最后几天。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_30", "act4", "david_hume", "大卫·休谟", "[hoarsely] [warmly] 亚当，别皱着眉头啦！四月我刚读完你寄来的新书，就在信里大喊“妙极了”！才半年第一版就卖断了货，全伦敦都在聊你那枚小扣针，临走前看见老友巨著问世，我痛快极了。", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("w06_30b", "act4", "david_hume", "大卫·休谟", "[softly] [chuckles] 不过咱们老交情不藏掖——你书里把地租算进商品价格那段，我还是有点不同意见，可惜这辈子没工夫再跟你吵三百回合啦！", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("w06_31", "act4", "adam_smith", "亚当·斯密", "[softly] [crying] 大卫，这十二年我躲在老家写书，每写完一章卡壳时，第一个想寄去听批评的就是你。你走了，以后爱丁堡夜里还有谁能端着酒杯跟我拍桌子较真呢？", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("w06_32", "act4", "david_hume", "大卫·休谟", "[warmly] [chuckles] 哈哈，我刚才还在跟冥河渡船的船夫开玩笑呢——我说老兄慢点开船，让我再多看几年大英帝国和全人类一点点甩掉愚昧和偏见！亚当，记住别让后人只读《国富论》，忘了你十七年前那本《道德情操论》。", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("w06_33", "act4", "adam_smith", "亚当·斯密", "[solemn] [warmly] 我永远不会忘，大卫。我晚年还要亲手修订《道德情操论》——把“盲目崇拜权贵、冷眼轻视穷人”写进人心最大的败坏。那两本书本就是一枚金币的正反两面。", acoustic_space="vintage_study", gap_after_s=0.30),
        # --- ACT 5: North Sea Epilogue — Wealth + Sympathy + 1790 True Legacy ---
        sfx("w06_34", "act5", "Serene gentle North Sea evening waves washing rhythmically over Scottish coastal pebbles with soft distant gulls and warm breeze, pure foley, no human voice", duration_seconds=3.2, gap_after_s=0.22),
        dlg("w06_35", "act5", "narrator", "历史旁白", "一七七六年八月二十五日，大卫·休谟安详辞世。傍晚，亚当·斯密与苏清禾并肩站在爱丁堡海湾的石堤上，望着远方千帆竞发的大海。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_36", "act5", "host_su", "苏清禾", "[softly] [warmly] 斯密教授，这两百五十年来，人们尊称您为“现代经济学之父”。如果让您用最后几句话，给两百多年后的普通中国听众做个总结，您最想留下一句什么叮嘱？", gap_after_s=0.24),
        dlg("w06_37", "act5", "adam_smith", "亚当·斯密", "[warmly] [solemn] 记住两件事就够了。第一，真正的国富，不在金库的金砖里，也不在垄断者的特权里，而在千千万万普通人凭本事分工合作、靠双手体面致富的自由里。", gap_after_s=0.26),
        dlg("w06_38", "act5", "adam_smith", "亚当·斯密", "[softly] [warmly] 第二，永远别把追求财富变成崇拜权贵、冷眼鄙视穷人。我在《道德情操论》里写过：无论人显得多么自私，本性里总有一根弦，会为陌生人的悲欢轻轻颤动。市场让世界变富，而法治与同情心，让世界变暖。", gap_after_s=0.28),
        dlg("w06_38b", "act5", "narrator", "历史旁白", "[softly] 历史留给亚当·斯密最动人的注脚，发生在十四年后的一七九零年。当他平静离世、亲友清点遗产时才震惊发现：这位享誉欧洲、薪俸丰厚的经济学巨匠，屋里几乎没留多少存款！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w06_38c", "act5", "narrator", "历史旁白", "[warmly] 原来他生前几十年，默默把大部分稿费和俸禄，全都悄悄匿名捐给了爱丁堡的穷苦孤寡与失学孩童，连最亲近的朋友都一无所知。写透“自利”的人，一生行的是最深沉的善。", acoustic_space="dry", gap_after_s=0.28),
        dlg("w06_39", "act5", "narrator", "历史旁白", "[warmly] 一七七六年的烛火从未熄灭。从一枚小小的黄铜扣针，到亿万人互联互通的现代商业世界，《1776爱丁堡夜话：〈国富论〉商业思想剧场》第一季全六集，到此圆满收官。感谢陪伴，咱们下一部思想剧场再见！", acoustic_space="dry", gap_after_s=0.80),
    ]
    return EpisodeCueSheet(
        episode_id="E006",
        chapter_number=6,
        title="守夜人的三张账单_政府边界与1776告别信",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.4,
        acts=acts,
        cues=cues,
    )
