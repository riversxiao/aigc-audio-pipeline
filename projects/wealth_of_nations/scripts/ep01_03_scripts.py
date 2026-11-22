"""Season 1 Audition Pack + Episodes E001–E003 for《1776爱丁堡夜话：〈国富论〉商业思想剧场》.

Flagship 15–18 minute anti-translationese (零翻译腔) historical intellectual radio drama adapted directly
from Adam Smith's 100% globally public-domain 1776 English original *An Inquiry into the Nature and Causes
of the Wealth of Nations*:
- AUDITION_WEALTH: 1776爱丁堡夜话核心试听包 (~1.8 min)
- E001: 《一枚扣针的奇迹_为什么分工让世界突然变富了》 (Book I Ch. 1–3, ~3,150 CJK chars)
- E002: 《从贝壳到金币_钱是怎么长出来的与水钻悖论》 (Book I Ch. 4–7, ~3,150 CJK chars)
- E003: 《谁在切蛋糕_工资利润地租与为什么同行爱凑堆》 (Book I Ch. 8–11, ~3,150 CJK chars)
"""

from __future__ import annotations

from aigc_audio_pipeline.models import EpisodeCueSheet
from drama_helpers import act, dlg, motif, sfx


def build_audition_wealth() -> EpisodeCueSheet:
    cues = [
        motif("wa01_hearth", "audition", "edinburgh_tavern_hearth", gap_after_s=0.22),
        dlg("wa02_narr", "audition", "narrator", "历史旁白", "[warmly] 一七七六年三月，爱丁堡老城海风微凉。牡蛎俱乐部摇曳的烛光里，一本彻底改写人类财富命运的大书刚刚付印，而书里藏着的，全是普通人挣钱过日子的实在门道。", acoustic_space="dry", gap_after_s=0.24),
        motif("wa03_pins", "audition", "pin_factory_clatter", placement="overlay_next", gap_after_s=0.18),
        dlg("wa04_boss", "audition", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 姑娘你算笔实在账！我厂里十个毛头小伙各盯一道工序，一天能砸出四万八千根亮晶晶的扣针；要是一个人从头干到尾，一天连二十根都凑不齐！", gap_after_s=0.24),
        dlg("wa05_smith", "audition", "adam_smith", "亚当·斯密", "[warmly] [calmly] 所以大伙儿每天端上餐桌的面包和牛肉，靠的从来不是肉铺老板和面包师傅发善心，而是人家也得挣钱养家。你跟他谈慈悲他未必理你，可谈成一笔双赢买卖，天没亮面包就烤好了。", gap_after_s=0.24),
        dlg("wa06_watt", "audition", "james_watt", "詹姆斯·瓦特", "[angry] 格拉斯哥老行会根本不是嫌我手艺差！他们就是怕我改良的蒸汽机抢了老作坊的饭碗，硬拿规矩卡死不让我开店！", stability=0.0, acoustic_space="dry", gap_after_s=0.22),
        dlg("wa07_lord", "audition", "merchant_lord", "东印度商董", "[condescending] 笑话！要是不给大公司特许垄断、不对外国货加满关税，咱们国家的黄金岂不都流进外人腰包了？", acoustic_space="dry", gap_after_s=0.22),
        dlg("wa08_hume", "audition", "david_hume", "大卫·休谟", "[chuckles] [warmly] 照老爷这套算盘，西班牙抢了美洲一船船白银，怎么反倒越抢越穷？金银只是筹码，老百姓手里买得起衣食住行，那才叫真富！", acoustic_space="dry", gap_after_s=0.26),
        dlg("wa09_smith_end", "audition", "adam_smith", "亚当·斯密", "[solemn] [warmly] 欢迎走进《1776爱丁堡夜话》——咱们卸掉晦涩翻译腔，用最接地气的中国话，把《国富论》听成一门活生生的赚钱与看世道学问。", gap_after_s=0.55),
    ]
    return EpisodeCueSheet(
        episode_id="AUDITION_WEALTH",
        chapter_number=0,
        title="《1776爱丁堡夜话：〈国富论〉商业思想剧场》核心试听包",
        mode="audition_pack",
        head_pad_s=0.35,
        tail_pad_s=1.0,
        acts=[act("audition", "爱丁堡牡蛎俱乐部试听", "edinburgh_hearth_enlightenment", bgm_duration_s=60.0)],
        cues=cues,
    )


def build_e001_pin_factory_division() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·1776爱丁堡雨夜与卸掉翻译腔的《国富论》", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
        act("act2", "第二幕·十八道工序、二百四十倍奇迹与种地为何难分工", "glasgow_workshop_vigor", bgm_duration_s=75.0),
        act("act3", "第三幕·狗不换骨头与屠夫面包师的双赢密码", "market_ledger_debate", bgm_duration_s=75.0),
        act("act4", "第四幕·为什么大城出巧匠而深山只有杂货铺", "glasgow_workshop_vigor", bgm_duration_s=75.0),
        act("act5", "第五幕·一件粗羊毛大衣背后的一万双陌生人的手", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Cold open + 1776 context + Anti-translationese manifesto ---
        motif("w01_01", "act1", "quill_printing_press", gap_after_s=0.20),
        dlg("w01_02", "act1", "narrator", "历史旁白", "[warmly] 欢迎走进《1776爱丁堡夜话：〈国富论〉商业思想剧场》。公元一七七六年三月九日，伦敦一家印刷坊里，两卷厚重的硬皮大书刚刚带着油墨香走下木质压印机。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_03", "act1", "narrator", "历史旁白", "那一年，北美十三州正准备敲响独立钟声，瓦特的蒸汽机刚发出第一声轰鸣。而苏格兰人亚当·斯密用十二年写就的这本《国富论》，直截了当回答了一个千古难题：一个国家，到底靠什么才变富？", acoustic_space="dry", gap_after_s=0.26),
        motif("w01_04", "act1", "edinburgh_tavern_hearth", gap_after_s=0.20),
        dlg("w01_05", "act1", "host_su", "苏清禾", "[curious] 斯密教授，我以前啃过老中译本，说实话翻两页就犯困，满纸都是“劳动生产力之最大增进”那种绕口长句。可翻开您一七七六年的英文原版，才发现您说话居然幽默得像老街坊聊天！", gap_after_s=0.24),
        dlg("w01_06", "act1", "david_hume", "大卫·休谟", "[chuckles] [wryly] 哈哈，清禾姑娘念两句那个拗口译本听听？如果连我这个写哲学书的老头都听打瞌睡，那可真冤枉亚当了！", acoustic_space="dry", gap_after_s=0.22),
        dlg("w01_07", "act1", "host_su", "苏清禾", "[wryly] 您听这句：“劳动生产力上最大的增进，以及运用劳动时所表现的更大的熟练、技巧和判断力，似乎都是分工的结果。”——是不是听完满脑子雾水？", gap_after_s=0.22),
        dlg("w01_08", "act1", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 哎哟，绕得我都喘不过气！我原本想说的话特简单：为什么干活越干越麻利、脑子越用越灵光、东西越造越多？说穿了就两个字——分工！", gap_after_s=0.24),
        dlg("w01_08b", "act1", "adam_smith", "亚当·斯密", "[warmly] 我写《国富论》从没打算摆学术架子吓唬人，我是写给跑船的水手、开铺子的老板和议会老爷听的！别人写国富开口必谈皇家金库，我偏偏第一页抓着一根半便士都不值的小扣针不撒手！", gap_after_s=0.24),
        sfx("w01_09", "act1", "Heavy wooden tavern door creaking open to brisk Scottish evening breeze and wet footsteps stepping onto Edinburgh cobblestone street, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.20),
        dlg("w01_09b", "act1", "adam_smith", "亚当·斯密", "[warmly] 别光坐在炉边空聊！雨停了，大伙儿披上呢子大衣，随我去格拉斯哥后巷瞧一眼老麦考利的扣针小厂——所有让世界变富的秘密，全都藏在那十个忙活的小伙子手里！", gap_after_s=0.28),
        # --- ACT 2: Inside Macaulay's Pin Factory + 3 causes + Agriculture vs Manufacturing ---
        motif("w01_10", "act2", "pin_factory_clatter", gap_after_s=0.20),
        dlg("w01_11", "act2", "boss_macaulay", "老麦考利", "[earthy] 欢迎欢迎！斯密教授，您带着休谟老先生和这位东方姑娘来我这窄作坊，可别嫌炭火呛人！汤姆，停一下手，让客人瞧瞧咱们这一根小铜针是怎么变出来的！", gap_after_s=0.24),
        dlg("w01_12", "act2", "apprentice_tom", "学徒汤姆", "[excited] 姑娘您看仔细喽！前头那小伙专把粗铜条拉成细铜丝；第二位专把弯丝抻直；我站第三道位子，咔嚓咔嚓按寸半截断；左手边专磨针尖，后头还有做针帽、蘸锡抛光和插纸卡的！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_13", "act2", "host_su", "苏清禾", "[curious] 天呐，这么一根比牙签还细的小扣针，你们居然拆成了十几道不同的活计？一共才十来号人吧，一天能做出多少根？", gap_after_s=0.22),
        dlg("w01_14", "act2", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 拆成整整十八道工序！咱们小厂条件简陋，才雇了十个人，有人还得兼干两三道。就这，一天能稳稳攒出十二磅扣针——一磅四千根，十个人一天能出整整四万八千根！平均每人四千八百根！", gap_after_s=0.24),
        dlg("w01_15", "act2", "host_su", "苏清禾", "[seriously] 四万八千根？！那如果让一个手脚麻利的聪明人单干，从拉铜丝到装纸卡全自己包圆，一天能造多少？", gap_after_s=0.22),
        dlg("w01_16", "act2", "boss_macaulay", "老麦考利", "[earthy] 别说四千八百根了，他拼了老命一天磨出二十根就算祖师爷显灵，弄不好连一根像样的都做不出来！", gap_after_s=0.22),
        dlg("w01_17", "act2", "adam_smith", "亚当·斯密", "[warmly] [seriously] 你看，二十根变成四千八百根，一眨眼效率翻了整整二百四十倍！为什么一分工就能凭空变出这么多财富？原因就三条，三条都简单得像家里算菜账。", gap_after_s=0.24),
        sfx("w01_18", "act2", "Rapid rhythmic blacksmith hammer tapping hot iron nails onto an anvil with bright metallic clinks in a busy 18th-century Scottish smithy, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w01_19", "act2", "adam_smith", "亚当·斯密", "[calmly] 第一叫熟能生巧。人一辈子专攻一个动作，手指头长了眼睛一样快！你看我认识的十八岁打铁钉小伙，一天能敲出两千三百颗钉子；换个样样都会的老铁匠来打，一天连三百颗都打不出来。", gap_after_s=0.24),
        dlg("w01_20", "act2", "james_watt", "詹姆斯·瓦特", "[excited] 第二条我最懂——省掉了来回换工具、换脑筋的时间！我修精密仪器最怕刚摸车床又去生炉子，来回一折腾，手生了、心散了，半天工夫全耗在“挪屁股”上了！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_21", "act2", "adam_smith", "亚当·斯密", "[warmly] 没错！而第三条最神奇——当你整天只盯这一道工序，脑袋自然会琢磨怎么造个巧机关替自己省力气！早年蒸汽机边上有个开关气门的小男孩，嫌老守着阀门没法出去玩耍。", gap_after_s=0.22),
        dlg("w01_22", "act2", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 你猜这机灵鬼怎么干？他拿根细绳把阀门拴在机器摇臂上，让蒸汽机一上一下自己拉动阀门——世上最早的自动联杆，就这么给一个想早点出去疯玩的孩子发明出来了！", gap_after_s=0.24),
        dlg("w01_23", "act2", "david_hume", "大卫·休谟", "[chuckles] [warmly] 哈哈，原来推动人类技术进步的，一半是科学家的钻研，另一半是打工人想偷个懒、早点下班的巧劲儿！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_24", "act2", "host_su", "苏清禾", "[curious] 教授，既然分工这么厉害，那为什么工厂里工业品越造越便宜，可农田里种小麦却很难靠分工一下子翻两百倍呢？", gap_after_s=0.22),
        dlg("w01_25", "act2", "adam_smith", "亚当·斯密", "[calmly] 问得极妙！工厂里拉铜丝和磨针尖可以同一秒钟并行开工；可种地得听老天爷的节气！春天犁地、夏天除草、秋天收割，你总不能雇一个人一年三百六十五天专门割麦子吧？", gap_after_s=0.24),
        dlg("w01_26", "act2", "adam_smith", "亚当·斯密", "[warmly] 所以富国在造布、炼铁、做机器上能甩开穷国十条街，可在种粮食这件事上，富国农夫的效率反而没法把穷国农夫甩开太远——这就是农业天然的节奏局限！", gap_after_s=0.28),
        # --- ACT 3: Why humans trade + "Not from the benevolence of the butcher" ---
        sfx("w01_27", "act3", "Lively 18th-century Scottish open town market ambience with rustic cart wheels on cobblestones, muffled friendly crowd murmur, and crisp bread paper wrapping, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("w01_28", "act3", "narrator", "历史旁白", "走出作坊，众人穿过飘着麦香和烤肉味的格拉斯哥老市集。苏清禾忽然抛出一个直击人心的问题：既然分工这么神，那人类是怎么学会分工的？难道是哪位圣明君主下诏书安排出来的吗？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_29", "act3", "adam_smith", "亚当·斯密", "[wryly] 绝不是哪位大人物坐在书房里设计出来的！分工源自人类骨子里一种其他动物全都没有的天性——喜欢做买卖、喜欢拿我多出来的东西换你手里的东西。", gap_after_s=0.24),
        dlg("w01_30", "act3", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 清禾，你活这么大，见过两只狗坐下来心平气和地拿一块猪骨头换另一块羊骨头吗？没有吧！小狗想吃肉只会摇尾巴讨好主人；可人一辈子指望上万陌生人帮忙，光靠讨好早就饿死了！", gap_after_s=0.24),
        dlg("w01_31", "act3", "host_su", "苏清禾", "[curious] 所以这就引出了您全书最出名、但也最容易被翻得文绉绉的那句名言——关于屠夫、酿酒师和面包房老板？", gap_after_s=0.22),
        dlg("w01_32", "act3", "adam_smith", "亚当·斯密", "[warmly] [seriously] 来，我用最直白的话说一遍。咱们今晚能吃上热腾腾的炖牛肉、喝上麦芽啤酒、咬上一口刚出炉的面包，靠的从来不是肉铺老张、酒馆老板和面包师傅突然大发善心，而是人家也得挣钱养家！", gap_after_s=0.24),
        dlg("w01_33", "act3", "boss_macaulay", "老麦考利", "[earthy] 太实在了！谁要跑来我店里说“老板你发发慈悲白送我两盒扣针”，我肯定拿扫帚轰他出去；可他要说“老板我拿两袋好面粉换你十盒扣针，咱俩都划算”，我立马拉他坐下喝一杯！", gap_after_s=0.24),
        dlg("w01_34", "act3", "adam_smith", "亚当·斯密", "[warmly] 这正是交易最体面的地方：你不必指望陌生人像亲爹亲妈一样爱你，也不用低三下四去乞讨。把人家想要的好东西摆在桌上，谈成一笔双赢买卖，哪怕素昧平生，他天没亮就甘心替你烤好面包。", gap_after_s=0.24),
        dlg("w01_35", "act3", "host_su", "苏清禾", "[warmly] 这么一讲我彻底透亮了！您书里其实还藏着一句特暖心的话：您说街上挑担子的搬运工和书斋里的大学教授，刚生下来时天分其实差不多，拉开差距的是后来的分工和历练。", gap_after_s=0.24),
        dlg("w01_36", "act3", "adam_smith", "亚当·斯密", "[warmly] [solemn] 没错。两只不同品种的猎犬天生差别巨大，可两个刚出生的孩子本没多大差别。分工先锤炼出不同的本事，大市场再把每个人的本事汇成宝库——人人都把一门手艺练精，就能换回全世界的丰盛。", gap_after_s=0.28),
        # --- ACT 4: Division of labor is limited by the extent of the market ---
        motif("w01_37", "act4", "merchant_port_harbor", gap_after_s=0.22),
        dlg("w01_38", "act4", "david_hume", "大卫·休谟", "[seriously] 等一下，亚当。既然分工这么能造富，为什么苏格兰高地那些偏僻山村里的农夫，至今还得自己当屠夫、自己烤面包、自己补皮靴，忙活一辈子照样穷得叮当响？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_39", "act4", "adam_smith", "亚当·斯密", "[seriously] 这就是《国富论》第三章最核心的一条铁律：分工能做到多细，完全取决于你的市场有多大！", gap_after_s=0.22),
        dlg("w01_40", "act4", "boss_macaulay", "老麦考利", "[earthy] 我拿我打铁钉的侄子举例！他在格拉斯哥大城一天敲一千颗钉子，一年三十万颗轻轻松松卖光；要是搬回高地只有几十户人的小山沟，全村一年都用不完他一天的货，专心打钉子非饿死不可！", gap_after_s=0.24),
        sfx("w01_41", "act4", "Wooden horse-drawn cargo wagon rattling slowly over muddy gravel lane fading into smooth wind-filled sails creaking swiftly across open water, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("w01_42", "act4", "adam_smith", "亚当·斯密", "[warmly] 精辟！所以人类历史上所有最先富起来的地方——古埃及的尼罗河、地中海沿岸、中国的长江珠江三角洲、还有今天的大西洋海港——全都是水运最顺畅的地方！", gap_after_s=0.24),
        dlg("w01_43", "act4", "james_watt", "詹姆斯·瓦特", "[excited] 咱们算过运输账！一辆大马车雇两个人、套八匹马，从伦敦颠簸六个礼拜到爱丁堡，最多拉四吨货；可一条海船只需六八个水手，同样时间能拉整整两百吨货！运费一下便宜几十倍！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_44", "act4", "host_su", "苏清禾", "[curious] 哇，放到今天中国一看简直一模一样！为什么高铁、高速公路、快递物流网一打通，一个小县城专做一把剪刀、一只打火机或者一件羽绒服，都能卖出百亿产值？因为市场瞬间变成了十几亿人！", gap_after_s=0.24),
        dlg("w01_45", "act4", "adam_smith", "亚当·斯密", "[warmly] 交通越顺畅、关卡越少，市场就越大；市场越大，分工就越细；分工越细，全社会就越富。反过来，谁要是到处设路障、搞地方保护，等于硬生生把大都市逼回穷山沟！", gap_after_s=0.28),
        # --- ACT 5: The Woolen Coat Miracle + Cliffhanger to Episode 2 ---
        motif("w01_46", "act5", "edinburgh_tavern_hearth", gap_after_s=0.20),
        dlg("w01_47", "act5", "narrator", "历史旁白", "夜色渐深，一行人回到暖烘烘的牡蛎俱乐部。壁炉火光照亮每个人身上的粗呢外套，斯密轻轻拎起学徒汤姆的衣袖，说出了《国富论》第一章末尾最令人震撼的一幕。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w01_48", "act5", "adam_smith", "亚当·斯密", "[warmly] [solemn] 汤姆，你身上这件最普通不过的粗羊毛大衣，看上去土里土气吧？可你算过没有，为了让它穿到你身上，全世界有多少个素昧平生的人替你忙活过？", gap_after_s=0.24),
        sfx("w01_49", "act5", "Steady wooden handloom shuttle clacking rhythmically beside crisp shears snipping coarse wool cloth in a cozy Scottish weaving cottage, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w01_50", "act5", "adam_smith", "亚当·斯密", "[warmly] 牧羊人、剪毛工、洗毛工、梳毛工、纺纱女、织布匠、染布师傅、裁缝；还有给剪毛工造剪刀的矿工、烧炭工、炼铁匠、砌熔炉的泥瓦匠；还有运来染料的造船工、帆布匠、水手和码头挑夫！", gap_after_s=0.24),
        dlg("w01_51", "act5", "apprentice_tom", "学徒汤姆", "[gasps] [excited] 我的天呐！光我这件几先令买来的粗布大衣，背后居然站着上万个帮我干活的人？！", stability=0.0, acoustic_space="dry", gap_after_s=0.22),
        dlg("w01_52", "act5", "adam_smith", "亚当·斯密", "[solemn] [warmly] 一点不假。在分工发达的文明社会里，哪怕是最普通一个打工人的衣食住行，论舒适便利，其实已经胜过荒原上统领一万名赤脚武士的部落国王。", gap_after_s=0.24),
        dlg("w01_53", "act5", "host_su", "苏清禾", "[curious] 斯密教授，既然千千万万个陌生人靠分工合作，可每天大家手里拿的东西五花八门，肉铺拿牛肉、铁匠拿铁钉、裁缝拿衣服，这买卖要是一对一硬换，非乱套不可吧？", gap_after_s=0.24),
        dlg("w01_54", "act5", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 问到点子上了！所以明天晚上，咱们就聊聊人类最伟大的发明之一——钱到底是怎么从牛羊贝壳一步步长成金银货币的，还有为什么救命的水几乎免费，不能吃的钻石却贵到天上去！", gap_after_s=0.24),
        dlg("w01_55", "act5", "narrator", "历史旁白", "[warmly] 下一集，《从贝壳到金币：钱是怎么长出来的，与水钻悖论》。炉火正旺，咱们不见不散。", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E001",
        chapter_number=1,
        title="一枚扣针的奇迹_为什么分工让世界突然变富了",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e002_money_and_price() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·牵牛买盐的尴尬与苏格兰铁钉零钱", "market_ledger_debate", bgm_duration_s=75.0),
        act("act2", "第二幕·金银胜出、国王偷掺铜与阿姆斯特丹诚实银行", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act3", "第三幕·水钻悖论与牛津剑桥靠小麦保住两百年家业", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
        act("act4", "第四幕·自然价格像地心引力，市场价格像风筝", "market_ledger_debate", bgm_duration_s=75.0),
        act("act5", "第五幕·国葬黑布暴涨、波尔多红酒与垄断的枷锁", "monopoly_trade_storm", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Barter nightmare + origins of money ---
        motif("w02_01", "act1", "brass_balance_coins", gap_after_s=0.20),
        dlg("w02_02", "act1", "narrator", "历史旁白", "[warmly] 第二夜，爱丁堡牡蛎俱乐部桌上摆出一架亮锃锃的黄铜天平和一捧叮当作响的先令银币。今晚的话题，直戳每个普通人的钱袋子：钱到底是怎么诞生的？东西的价钱又是谁定出来的？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_03", "act1", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 诸位想象一下没有钱的日子！我是个肉铺老板，今天宰了头肥牛想换点面包和啤酒。可我扛着半扇牛肉走到面包房，面包师傅说他家刚炖了一锅羊肉，根本不要牛肉！", gap_after_s=0.24),
        dlg("w02_04", "act1", "apprentice_tom", "学徒汤姆", "[curious] 那您拿牛肉换啤酒不就完了？", acoustic_space="dry", gap_after_s=0.20),
        dlg("w02_05", "act1", "boss_macaulay", "老麦考利", "[earthy] 问题更大！啤酒馆老板只要两斤牛肉，可我手里牵着一整头大活牛啊！难道我为了买半斤盐、两杯啤酒，还得当街把一头活牛切成二十块找零吗？", gap_after_s=0.24),
        dlg("w02_06", "act1", "adam_smith", "亚当·斯密", "[warmly] 这就叫“物物交换的死胡同”。你想要的他正好有，他想要的你还得正好有，而且价值还得刚好能切开找零——这种巧合简直比中头彩还难！", gap_after_s=0.24),
        dlg("w02_07", "act1", "adam_smith", "亚当·斯密", "[calmly] 于是聪明人自然琢磨出一个土办法：每个做买卖的人除了自家手艺，兜里总得备一样全镇子人见了都点头肯收的“硬通货”。", gap_after_s=0.24),
        sfx("w02_08", "act1", "Handful of iron nails clinking onto an oak Scottish tavern bar counter beside a ceramic ale mug set down with a solid thud, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w02_09", "act1", "david_hume", "大卫·休谟", "[warmly] [chuckles] 历史上大伙儿试过的硬通货五花八门！古希腊用牛羊，阿比西尼亚用盐块，印度沿海用海贝壳，纽芬兰用咸鳕鱼干，弗吉尼亚用烟叶，甚至咱们苏格兰有些穷村子，工匠进酒馆居然揣一把铁钉当零钱！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_10", "act1", "apprentice_tom", "学徒汤姆", "[chuckles] [excited] 哈哈，拿铁钉买酒我真见过！我老家铁匠进面包店，掏出五颗铁钉拍在柜台上换个黑面包，老板连看都不带犹豫的！", acoustic_space="dry", gap_after_s=0.22),
        dlg("w02_11", "act1", "host_su", "苏清禾", "[curious] 可铁钉太沉、咸鱼会臭、牛羊还得喂草！所以世界各地绕了一大圈，最后不约而同全选了金子和银子当钱？", gap_after_s=0.22),
        # --- ACT 2: Why gold/silver won + royal debasement + Bank of Amsterdam ---
        sfx("w02_12", "act2", "Heavy iron minting die stamping a gleaming gold coin cleanly onto a wooden workbench followed by coins stacking crisply, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("w02_13", "act2", "adam_smith", "亚当·斯密", "[calmly] 就凭两个过硬本事：第一耐放，放一百年不烂不发霉，不像咸鱼和牛羊过两天就臭了老了；第二好分割又好拼回，一块金锭切成十片再熔回一块，分量一点不少，揣兜里就能走遍天下。", gap_after_s=0.24),
        dlg("w02_14", "act2", "boss_macaulay", "老麦考利", "[earthy] 不过早年没铸币的时候也麻烦！每次买块布都得掏出小天平称分量，还得提防奸商在银块里掺铅掺铜，买个菜跟做炼金术似的。", gap_after_s=0.24),
        dlg("w02_15", "act2", "adam_smith", "亚当·斯密", "[warmly] 所以才有了公家铸币厂——把金银压成一样重、一样纯的圆片，盖上国王印章，省得大家天天拿秤称。本意是极好的便民服务。", gap_after_s=0.24),
        dlg("w02_16", "act2", "merchant_lord", "东印度商董", "[condescending] 瞧，教授您自己也承认了，还是得靠王室和朝廷发钱立规矩嘛！", acoustic_space="dry", gap_after_s=0.20),
        dlg("w02_17", "act2", "adam_smith", "亚当·斯密", "[wryly] [seriously] 商董先别急着得意。我翻遍了古罗马、古希腊和欧洲几百年铸币史，发现几乎所有缺钱打仗的国王和政府，最后都干过同一件缺德事——偷偷往硬币里减料掺铜！", gap_after_s=0.24),
        dlg("w02_18", "act2", "david_hume", "大卫·休谟", "[seriously] 说透了！最初一英镑就是实打实的一磅纯银；古罗马的铜币最初也重整整一磅。可几百年王室一缺钱就缩水重铸，到咱们今天，一英镑硬币里的含银量连当初三分之一都不到！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_19", "act2", "adam_smith", "亚当·斯密", "[coldly] [seriously] 表面上叫“新币照旧顶一镑用”，骨子里就是赖账和隐形抽税！债权人和存了一辈子辛苦钱的老百姓稀里糊涂资产缩水，这跟后来纸币滥发引发通胀，原理完全一脉相承！", gap_after_s=0.24),
        dlg("w02_20", "act2", "host_su", "苏清禾", "[curious] 那当年欧洲商人们面对五花八门的缩水破硬币，就没有想出什么防坑的好办法吗？", gap_after_s=0.22),
        dlg("w02_21", "act2", "adam_smith", "亚当·斯密", "[warmly] 有！阿姆斯特丹银行就是神来之笔！他们收进各国磨损硬币后，严格按实际纯银分量记成诚实的“银行账面钱”，绝不掺假，结果全欧洲商人都抢着拿阿姆斯特丹的信用票据结账！", gap_after_s=0.28),
        # --- ACT 3: Water vs Diamond Paradox + Real Purchasing Power (Elizabethan Corn Rent!) ---
        motif("w02_22", "act3", "edinburgh_tavern_hearth", gap_after_s=0.20),
        dlg("w02_23", "act3", "host_su", "苏清禾", "[curious] 教授，说完了钱，我还有一个藏在心里多年的疑惑——您书里第四章末尾提过著名的“水与钻石悖论”：人三天不喝水会渴死，水几乎不要钱；钻石不能吃不能喝，凭啥能换一座庄园？", gap_after_s=0.26),
        dlg("w02_24", "act3", "adam_smith", "亚当·斯密", "[warmly] 因为“价值”这个词平时有两种截然不同的意思！一种叫“实用价值”，就是东西对活命有多大用处；另一种叫“交换价值”，就是拿它去市场上能换回多少别的东西。", gap_after_s=0.24),
        dlg("w02_25", "act3", "adam_smith", "亚当·斯密", "[calmly] 最救命的东西往往交换价值极低，比如空气和溪水；而几乎没啥实用价值的东西，比如钻石，交换价值高得吓人。第一，挖出一颗好钻石得耗费极高劳动成本；第二，这东西稀缺得要命！", gap_after_s=0.24),
        dlg("w02_26", "act3", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 嘿，我懂了！要是我俩困在撒哈拉大沙漠里快渴死了，你手里拎着一壶凉白开，我兜里揣着十颗大钻石，我肯定二话不说拿十颗钻石换你一口水！值不值钱，全看稀缺和费劲程度！", gap_after_s=0.24),
        sfx("w02_27", "act3", "Dry golden wheat grains rustling crisply into a wooden bushel measure beside parchment lease documents unfolding, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w02_28", "act3", "adam_smith", "亚当·斯密", "[warmly] 老麦考利这句沙漠换水太透彻了！顺着这理儿再多悟一层：看一个人真富还是假富，别只盯账面上有多少银币，要看手里的钱能换回多少实打实的衣食住行——这叫“真实价格”与“名义价格”！", gap_after_s=0.24),
        dlg("w02_29", "act3", "david_hume", "大卫·休谟", "[warmly] 亚当书里那个牛津和剑桥学院收地租的真故事最经典！伊丽莎白女王时代立过一条怪规矩：两所大学出租校产土地，必须把三分之一租金按“小麦”来算，不许全按死银币算！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_30", "act3", "adam_smith", "亚当·斯密", "[chuckles] [warmly] 结果两百年后你猜怎么着？美洲大批白银涌进欧洲，银子大幅贬值！当初只收固定银币的贵族地主全亏惨了，唯独牛津和剑桥那三分之一的小麦租金，购买力翻了好几倍，稳稳养活了整个学院！", gap_after_s=0.26),
        dlg("w02_31", "act3", "host_su", "苏清禾", "[excited] 哇，这就是穿越两百年的抗通胀神课啊！只看工资条上数字涨了没用，得算扣掉物价之后能买几斤米、几顿肉，那才是实打实的真实收入！", gap_after_s=0.28),
        # --- ACT 4: Natural Price vs Market Price (Gravity & Kite) ---
        sfx("w02_32", "act4", "Quiet wooden merchant study with quill pen scratching columns of figures in an account ledger beside steady ticking grandfather clock, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("w02_33", "act4", "narrator", "历史旁白", "弄清了货币与价值，斯密在第七章亮出了全书最精妙的一组概念——“自然价格”与“市场价格”。这听着像学术黑话，其实用老百姓的话一拆，人人秒懂。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_34", "act4", "adam_smith", "亚当·斯密", "[calmly] 老麦考利，你卖一盒扣针，成本怎么算？第一是工人的工钱，第二是你的厂房地租，第三是你垫本钱开厂该赚的正常利润。这三笔账加在一起不亏不暴利，就叫“自然价格”——说白了，就是合理底价。", gap_after_s=0.24),
        dlg("w02_35", "act4", "host_su", "苏清禾", "[curious] 那“市场价格”就是每天店门口实际挂牌卖的价钱？这两个价钱难道不是一回事吗？", gap_after_s=0.22),
        dlg("w02_36", "act4", "adam_smith", "亚当·斯密", "[warmly] 经常不一样！市场价格取决于今天货架上摆了多少货，以及有多少揣着真金白银、真心想买的人站在柜台前——注意，穷光蛋对着六驾豪华马车流口水不算有效需求，揣着钱能买单的才算！", gap_after_s=0.24),
        dlg("w02_37", "act4", "adam_smith", "亚当·斯密", "[warmly] 如果今天货少买家多，大家抢着加价，市场价就会飞到合理底价上头；反过来货堆成山没人买，老板就得流血甩卖，市场价跌到合理底价下头。", gap_after_s=0.24),
        dlg("w02_38", "act4", "david_hume", "大卫·休谟", "[warmly] 可妙就妙在它不会永远偏离！只要没外力硬拦着，如果卖扣针利润高得流油，明天全城的生意人都会带着资金和工人杀进来开扣针厂，货一多，价格自然跌回合理底价！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_39", "act4", "adam_smith", "亚当·斯密", "[warmly] 反之如果种小麦亏本，明年大伙儿少种麦子改养羊，粮食一紧俏，价格又会爬回合理底价！所以“自然价格”像地心引力，“市场价格”像牵着线的风筝，风大时忽高忽低，终究围着中心打转！", gap_after_s=0.24),
        dlg("w02_40", "act4", "james_watt", "詹姆斯·瓦特", "[curious] 那如果是靠独门绝活呢？比如一位染布师傅偷偷研出一种绝美新染料，成本比同行便宜一半，他藏着配方不告诉别人，是不是就能一连好几年赚超额利润？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w02_41", "act4", "adam_smith", "亚当·斯密", "[warmly] 对！手艺绝活和专利创新赚的正是这笔先行者奖赏——而且这种商业秘密迟早会被同行学去，最后好技术惠及全天下，跟靠官府大印硬霸占市场的垄断完全是两码事！", gap_after_s=0.28),
        # --- ACT 5: Royal Funeral Black Cloth + Bordeaux Wine + Monopoly Price Rigging ---
        sfx("w02_42", "act5", "Solemn distant London cathedral funeral bells tolling over hurried footsteps rushing into a bustling tailor cloth shop with crisp linen bolts unrolling fast, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("w02_43", "act5", "boss_macaulay", "老麦考利", "[earthy] [chuckles] 短期涨价我亲眼见过！前年王室办国葬，全伦敦一夜之间人人都得穿黑礼服。布店里的黑呢子价钱当天翻了一倍，裁缝师傅工钱也水涨船高；可满街红布绿布压根没人理，价钱照旧！", gap_after_s=0.24),
        dlg("w02_44", "act5", "host_su", "苏清禾", "[pushback] 等等教授！碰到这种突发缺货涨价，好多人第一反应都是喊官府出面“强制限价”，不许布店涨一分钱！您怎么看？", gap_after_s=0.22),
        dlg("w02_45", "act5", "adam_smith", "亚当·斯密", "[seriously] 看起来解气，其实最坑人！黑布价钱涨上去，是在给全国布商发紧急电报：“伦敦急缺黑布，快连夜运货来，有钱赚！”不出三天，外地黑布铺天盖地涌进来，价钱自己就掉下来了。", gap_after_s=0.24),
        dlg("w02_46", "act5", "adam_smith", "亚当·斯密", "[coldly] 可你要是下死命令不准涨价，外地布商算完运费不划算根本不来，本地布商把货藏进地下室搞黑市，结果谁也买不到黑布！真正让价格长期居高不下的，从来只有两种稀缺——天然稀缺和人为垄断。", gap_after_s=0.24),
        sfx("w02_47", "act5", "Crisp wine cork popping and fine red wine pouring gently into a crystal glass inside a quiet stone cellar, pure foley, no human voice", duration_seconds=2.2, gap_after_s=0.18),
        dlg("w02_48", "act5", "david_hume", "大卫·休谟", "[warmly] 天然稀缺比如法国波尔多那几片阳光土壤绝佳的顶级葡萄园，全地球就那么几亩地，好酒产量封顶，价格自然永远高挂；可人为垄断则是强盗用栅栏圈住原本人人能干的买卖！", acoustic_space="dry", gap_after_s=0.24),
        sfx("w02_48b", "act5", "Heavy pouring Scottish autumn rain pattering over muddy farmland transitioning to rustic wooden flour mill wheel creaking slowly, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("w02_48c", "act5", "apprentice_tom", "学徒汤姆", "[curious] 教授，还有件事我想不明白！前年阴雨连绵、苏格兰燕麦减产两成，市场上的燕麦价钱居然直接翻了一倍！可布店里的毛呢减产两成，价钱也就涨了一星半点，这又是为啥？", acoustic_space="dry", gap_after_s=0.22),
        dlg("w02_48d", "act5", "adam_smith", "亚当·斯密", "[warmly] 汤姆这双眼睛真毒！道理就在肚皮上：新呢大衣买不起，你大可以把去年那件旧衣裳再补补多穿一冬；可每天嘴里这口救命粮食，一天不吃都挨不住！", gap_after_s=0.24),
        dlg("w02_48e", "act5", "adam_smith", "亚当·斯密", "[calmly] 越是家家户户离不了的必需品，货架上一旦少了一点点，买家的恐慌就会把价钱瞬间推上天；而可买可不买的消费品，涨一点大家就掉头不买了，波动小得多！", gap_after_s=0.24),
        dlg("w02_48f", "act5", "host_su", "苏清禾", "[excited] 哈哈，后世经济学教科书讲得云里雾里的“需求价格弹性”，被教授两句旧大衣和燕麦粥直接讲成大白话了！", gap_after_s=0.24),
        dlg("w02_49", "act5", "merchant_lord", "东印度商董", "[sarcastic] 呵，教授又把矛头对准咱们大商行和特许垄断啦？没有独家专卖权，哪来高额利润养活这么多体面大老板？", acoustic_space="dry", gap_after_s=0.22),
        dlg("w02_50", "act5", "adam_smith", "亚当·斯密", "[coldly] [solemn] 垄断价格永远是能从买家兜里榨出来的最高价，而自由竞争的价格永远是卖家能活下去的最低价。商董，下一场夜话，咱们就当着工匠、老板和地主的面，把国民财富这块大蛋糕切开算笔总账！", gap_after_s=0.24),
        dlg("w02_51", "act5", "narrator", "历史旁白", "[warmly] 下一集，《谁在切蛋糕：工资、利润、地租，与为什么同行总爱私下凑堆》。为什么说斯密其实最警惕资本家抱团？敬请收听！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E002",
        chapter_number=2,
        title="从贝壳到金币_钱是怎么长出来的与水钻悖论",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e003_wages_profits_guilds() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·为什么经济往上走时，打工人的工资才真涨", "glasgow_workshop_vigor", bgm_duration_s=75.0),
        act("act2", "第二幕·斯密打脸名句：同行聚会为何总想密谋抬价", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act3", "第三幕·瓦特的真实遭遇与“不准出村找工作”的荒唐法", "monopoly_trade_storm", bgm_duration_s=75.0),
        act("act4", "第四幕·矿工、大律师与人的蜜汁自信：职业薪酬密码", "market_ledger_debate", bgm_duration_s=75.0),
        act("act5", "第五幕·老板为何只骂高工资不提暴利？三方利益总账", "edinburgh_hearth_enlightenment", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Wages rise in a growing economy + High wages boost productivity ---
        motif("w03_01", "act1", "edinburgh_tavern_hearth", gap_after_s=0.20),
        dlg("w03_02", "act1", "narrator", "历史旁白", "[warmly] 第三夜，牡蛎俱乐部的辩论火药味越来越浓。很多现代读者没翻过《国富论》原书，听人以讹传讹，以为亚当·斯密是个只替资本家说话的冷血学者。今晚，斯密亲手掀翻这个天大误会。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_03", "act1", "host_su", "苏清禾", "[pushback] 斯密教授，我直说了吧！现在好多人骂市场经济，说老板眼里只有利润，工人永远是被压榨的份。您在《国富论》第八章讲工资，到底站在哪一边？", gap_after_s=0.24),
        dlg("w03_04", "act1", "adam_smith", "亚当·斯密", "[seriously] [warmly] 清禾，我先说一句写在书里的实在话：哪一个社会如果大多数老百姓活得穷困潦倒、吃了上顿没下顿，这个国家绝对谈不上繁荣幸福！给出力气养活全社会的劳动者体面工钱，既公道更强国。", gap_after_s=0.24),
        dlg("w03_05", "act1", "apprentice_tom", "学徒汤姆", "[sighs] 话是这么说，可现实里咱们工人跟老板谈工钱哪谈得过啊？老板家有余粮，停工半年照样吃肉喝酒；咱们工人停工一个礼拜，家里锅都揭不开了！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_06", "act1", "adam_smith", "亚当·斯密", "[seriously] 汤姆说出了大实话！谈判桌上，雇主人数少、好串通，家底厚能硬扛，天然占上风。而且老板们平时悄悄达成的“绝不随便涨薪”的默契，外头根本听不见；工人一罢工喊口号，报纸就满街骂！", gap_after_s=0.24),
        sfx("w03_07", "act1", "Bustling 18th-century shipyard hammers knocking timber beams with brisk sawing and busy dockyard carts rolling steadily, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("w03_08", "act1", "boss_macaulay", "老麦考利", "[earthy] 那靠啥逼着咱们老板乖乖涨工资？靠生意红火、满街抢人！去年格拉斯哥港口扩建、新开十几家船厂织布厂，我厂里要是敢压工钱，明早十个小伙全被对街老板加价挖走啦！", gap_after_s=0.24),
        dlg("w03_09", "act1", "adam_smith", "亚当·斯密", "[warmly] 听明白了吗？让工资往上涨的，从来不是一个国家老本有多厚，而是经济正处在往上冲的增量期！", gap_after_s=0.22),
        dlg("w03_10", "act1", "adam_smith", "亚当·斯密", "[calmly] 你看大西洋对岸的北美殖民地，家底比英国薄得多，可到处开荒建厂缺人手，木匠和农工的工资比伦敦还高一截；反观停滞不前、几百年不长进的老帝国，老本再厚，底层苦力也只能挣口糊口饭！", gap_after_s=0.24),
        dlg("w03_11", "act1", "merchant_lord", "东印度商董", "[condescending] 哼，教授太天真！给穷工人发高工资只会惯坏他们——兜里有钱了，干三天歇四天去酒馆买醉，活儿反倒没人干了！还是饥荒年头粮价高，大伙儿才肯玩命干活！", acoustic_space="dry", gap_after_s=0.22),
        dlg("w03_12", "act1", "adam_smith", "亚当·斯密", "[coldly] [seriously] 这是富人最懒惰、最残忍的偏见！我查过法国和苏格兰几十年的织布厂账本：丰收粮价便宜的年景，工人吃得饱、身子壮、心里有盼头，干活手脚麻利，全厂产量年年创新高！", gap_after_s=0.24),
        dlg("w03_12b", "act1", "adam_smith", "亚当·斯密", "[solemn] 到了闹饥荒的年景，老百姓饿得头晕眼花、还要把老婆孩子从工厂叫去讨饭，病死饿死一大片，工坊生意照样冷清！反而是计件高薪最怕工人拼命加班透支身体，根本不存在高薪养懒汉的鬼话！", gap_after_s=0.24),
        dlg("w03_12c", "act1", "boss_macaulay", "老麦考利", "[earthy] 我替教授作证！我厂里给汤姆他们涨了计件工钱、午饭管够燕麦肉汤以后，次品率直接掉了一半，连请病假的都没几个！省小钱坑员工的老板，才是最不会算账的傻瓜！", gap_after_s=0.24),
        dlg("w03_13", "act1", "host_su", "苏清禾", "[warmly] 哇，这句话放到今天太戳心了！增量时代老板抢着加薪，存量停滞时代大家只能内卷——鼓励创业、保住经济活力，才是对打工人最硬核的保护！", gap_after_s=0.28),
        # --- ACT 2: Smith's famous quote warning against merchants conspiring ---
        sfx("w03_14", "act2", "Clinking heavy crystal wine decanters behind closed oak clubroom doors with low secretive murmured clatter in a gilded London guild hall, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("w03_15", "act2", "merchant_lord", "东印度商董", "[condescending] 教授，话别说太满。咱们当老板的聚在一起开商会、定行业指导价、商量工资封顶，那是为了防止恶性竞争、维护行业体面嘛！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_16", "act2", "adam_smith", "亚当·斯密", "[coldly] [wryly] 商董，我就爱听你说这句大实话。各位记住我写在《国富论》第一篇第十章里的原话，一字不差——", gap_after_s=0.20),
        dlg("w03_17", "act2", "adam_smith", "亚当·斯密", "[solemn] [coldly] 干同一行生意的老板们，平时很少凑到一块儿；就算为了喝酒聊天、消遣玩乐偶尔聚在一起，聊着聊着，话题最后也几乎总免不了变成一场对付老百姓的密谋——或者商量怎么联手抬高物价！", gap_after_s=0.26),
        dlg("w03_18", "act2", "boss_macaulay", "老麦考利", "[chuckles] [earthy] 哈哈哈哈！教授你这嘴太毒了，直接把咱们商会的底裤都扒光了！确实，真有哪个行业大佬喊大家开“自律大会”，十有八九不是商量降价让利，而是商量怎么别抢对方肥肉！", gap_after_s=0.24),
        dlg("w03_19", "act2", "adam_smith", "亚当·斯密", "[seriously] 我从来不是替资本家唱赞歌，我是站在全社会消费者一边！靠道德劝老板发善心没用，唯一管用的办法，就是拆掉准入高墙，让新对手随时能冲进来抢生意——门一敞开，价格同盟不出三个月就会瓦解！", gap_after_s=0.28),
        # --- ACT 3: James Watt vs Glasgow Hammermen Guild + Parish Settlement Law ---
        motif("w03_20", "act3", "watt_steam_workshop", gap_after_s=0.22),
        dlg("w03_21", "act3", "narrator", "历史旁白", "说到“准入高墙”，屋角一直默默擦拭铜齿轮的年轻人猛地站起了身。他就是日后改写人类工业文明的詹姆斯·瓦特——而在一七五七年，他差点被一张行会禁令扼杀在摇篮里。", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_22", "act3", "james_watt", "詹姆斯·瓦特", "[angry] 清禾姑娘，刚才那位商董满口行业秩序，你听听我当年在格拉斯哥吃了什么苦头！我从伦敦学成最精密的航海仪器手艺回来，想在格拉斯哥街头租间小铺子修罗盘、鼓捣蒸汽机。", acoustic_space="dry", gap_after_s=0.24),
        sfx("w03_23", "act3", "Heavy wooden shop shutters slamming shut and iron padlock snapping locked in a quiet stone alleyway, pure foley, no human voice", duration_seconds=2.3, gap_after_s=0.18),
        dlg("w03_24", "act3", "james_watt", "詹姆斯·瓦特", "[fiercely] 结果呢？格拉斯哥“铁匠行会”一纸禁令直接封了我的门！理由可笑至极——说我既不是行会会员的儿子，又没在本地乖乖熬满七年学徒，哪怕我手艺比全城老师傅加起来都高，也不准我开店！", stability=0.0, acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_25", "act3", "host_su", "苏清禾", "[gasps] [curious] 竟然真有这事？！那后来瓦特先生是怎么冲出来的？", gap_after_s=0.20),
        dlg("w03_26", "act3", "james_watt", "詹姆斯·瓦特", "[warmly] 全靠当年在格拉斯哥大学当教授的亚当·斯密和几位学者！因为大学校园不受城里行会管辖，斯密教授帮我在校内批了间地下工坊，聘我当大学仪器师——改良蒸汽机就是在这间小屋里诞生的！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_27", "act3", "adam_smith", "亚当·斯密", "[coldly] [seriously] 所以我在书里痛骂了足足几十页的“七年强制学徒制”！修个仪器用得着白白给师傅当七年免费苦力吗？行会根本不是保质量，就是既得利益者竖起铁丝网，阻止像瓦特这样的天才进来抢饭碗！", gap_after_s=0.24),
        dlg("w03_28", "act3", "apprentice_tom", "学徒汤姆", "[angry] 还不止行会呢！教授，英格兰那个《教区定居法》更坑咱们穷人！我表叔在邻镇找着一份双倍工钱的活，结果当地教区官怕他以后老了吃救济，硬派衙役把他撵回穷老家！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_29", "act3", "adam_smith", "亚当·斯密", "[solemn] [angry] 荒唐透顶！我在书里写得明明白白：一个穷人凭双手吃饭，那是世上最神圣不可侵犯的财产！逼着老实人困死在没活干的老家、跨过教区界线比翻山越海还难，这是最赤裸裸的暴政！", stability=0.0, gap_after_s=0.24),
        dlg("w03_30", "act3", "adam_smith", "亚当·斯密", "[calmly] 至于商董担心的次品问题？掏钱买单的顾客就是最严厉的质检官！哪家店敢卖次品，不出半个月街坊就不登门了；反倒是有行会撑腰、别无分店的老爷铺子，才敢把次品卖成天价！", gap_after_s=0.28),
        # --- ACT 4: Why wages differ across jobs (All 5 compensating differentials + Overconfidence!) ---
        sfx("w03_31", "act4", "Echoing pickaxe strikes against deep coal seam followed by bright quill pen scribbling swiftly on legal parchment in a courthouse, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("w03_32", "act4", "host_su", "苏清禾", "[curious] 教授，就算拆掉了所有高墙，自由市场里不同行当的收入差距也很大呀！为什么下井挖煤的矿工比坐窗边织布的挣得多，而大律师、外科名医挣得更是普通人几十倍？", gap_after_s=0.24),
        dlg("w03_33", "act4", "adam_smith", "亚当·斯密", "[warmly] 这背后是市场极聪明的“五条冷暖找平规则”！第一看活儿舒不舒服、体不体面——挖煤矿又黑又脏又危险，当屠夫满手血污，不给高工钱谁肯去干？这就是辛苦和风险补贴。", gap_after_s=0.24),
        dlg("w03_34", "act4", "adam_smith", "亚当·斯密", "[calmly] 第二看学费成本——学医和学法律得烧掉十年光阴和大把银子，毕业后的高薪里，有一大块是在还前期读书的本钱和利息！第三看工作稳不稳定，瓦匠下雨下雪没法开工，干一天得把歇工那天的饭钱挣出来。", gap_after_s=0.24),
        dlg("w03_35", "act4", "boss_macaulay", "老麦考利", "[earthy] 第四条我猜到了——靠不靠谱、担多大干系！你把一袋子金子交金匠打戒指，或者把亲爹性命交到大夫手里，总不能找个穷得揭不开锅的混混吧？高薪里藏着一份“信任溢价”！", gap_after_s=0.24),
        dlg("w03_36", "act4", "david_hume", "大卫·休谟", "[chuckles] [wryly] 第五条最像买彩票——成名概率！一百个咬牙苦读法律的穷学生，可能只有一两个能当上名动伦敦的大律师，所以头牌大律师的天价收入，是把落榜九十九人的学费全折算进奖池了！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_37", "act4", "adam_smith", "亚当·斯密", "[wryly] [chuckles] 可笑的是，人的天性总高估自己的好运气！明知战场上炮弹不长眼、出海船容易沉，年轻小伙照样争着当水手和士兵——因为人人都觉得“倒霉的肯定是别人，立功发财的一定是我”！", gap_after_s=0.28),
        # --- ACT 5: Rent, Profit, and Whose Interest Aligns with Society ---
        motif("w03_38", "act5", "brass_balance_coins", gap_after_s=0.20),
        dlg("w03_39", "act5", "narrator", "历史旁白", "夜过三更，斯密在第一篇末尾做了一场极为冷静的利益解剖：社会分三大群体——拿地租的地主、拿工资的劳动者、拿利润的资本老板。这三拨人里，谁的钱包跟国家兴衰绑得最死？", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_40", "act5", "adam_smith", "亚当·斯密", "[solemn] 劳动者的利益和国家兴衰完全一致：国家蒸蒸日上，工人有活干、有涨薪；国家一垮，最先挨饿的就是工人。地主的利益也大多和国家一致，全城繁荣，地价自然水涨船高。", gap_after_s=0.24),
        dlg("w03_40b", "act5", "david_hume", "大卫·休谟", "[wryly] [chuckles] 可惜贵族地主老爷们有个毛病：收地租不用动脑筋也不用干苦活，天天在庄园里打猎喝茶，结果压根不懂经济账，在议会里常常被能说会道的大商行老板忽悠得团团转！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_40c", "act5", "adam_smith", "亚当·斯密", "[warmly] 没错，地主是利益对得上但懒得操心；工人是利益最一致但每天忙着糊口没空去议会发声。", gap_after_s=0.22),
        dlg("w03_41", "act5", "adam_smith", "亚当·斯密", "[coldly] [seriously] 唯独靠高额利润吃饭的大商人与大工厂主，大家必须留十个心眼！咱们的大老板整天哀嚎“高工资把物价推高了，害得出口卖不动”，可你听见哪位老板抱怨过高额利润推高物价吗？", gap_after_s=0.24),
        dlg("w03_42", "act5", "david_hume", "大卫·休谟", "[chuckles] [sarcastic] 哈，一针见血！利润和工资一样计进成本，可大老板嘴上只骂工钱太贵，对自己滚雪球似的暴利装聋作哑！", acoustic_space="dry", gap_after_s=0.24),
        dlg("w03_43", "act5", "adam_smith", "亚当·斯密", "[coldly] [solemn] 竞争越充分、国家越富强，平均利润率反而越低；所以大老板天然喜欢扩市场、却总暗搓搓想收紧竞争！凡是这批人向议会递的新法案，必须拿放大镜反复细查，绝不能轻信！", gap_after_s=0.26),
        dlg("w03_44", "act5", "host_su", "苏清禾", "[excited] 天呐！今天彻底刷新三观！原来《国富论》不是资本家的护身符，而是人类第一部反垄断、护普通人的清醒指南！那传说中最著名的“看不见的手”，原书里到底是怎么说的？", gap_after_s=0.24),
        dlg("w03_45", "act5", "adam_smith", "亚当·斯密", "[warmly] 明天晚上，咱们翻开资本与银行的大账本，把“看不见的手”的真身请出来，再聊聊纸币这条既能造福天下、也能让人粉身碎骨的“空中高速公路”！", gap_after_s=0.24),
        dlg("w03_46", "act5", "narrator", "历史旁白", "[warmly] 下一集，《看不见的手真相：资本流向与纸币空中公路》。咱们准时开讲！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E003",
        chapter_number=3,
        title="谁在切蛋糕_工资利润地租与为什么同行爱凑堆",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )
