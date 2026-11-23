"""Season 1 Episodes E004–E006 for《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》.

Flagship 15–17 minute anti-translationese (零翻译腔) historical satirical radio drama adapted directly
from Frédéric Bastiat's 100% globally public-domain 1848–1850 masterpieces (*Ce qu'on voit et ce qu'on
ne voit pas*, *L'État*, and *La Loi*):
- E004: 《裁军与铁饭碗_政府养闲人为什么没增加总需求》
- E005: 《花钱如流水是恩人吗_浪子阔少与节俭人的暗账》
- E006: 《国家是什么_每个人都想靠别人养活的宏大幻觉》
"""

from __future__ import annotations

from aigc_audio_pipeline.models import EpisodeCueSheet
from drama_helpers import act, dlg, motif, sfx


def build_e004_disbanding_troops_taxes() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·裁减十万冗兵风波：一亿法郎采购单真没了吗？", "parliament_satire_march", bgm_duration_s=75.0),
        act("act2", "第二幕·水桶舀水魔术与五十名看果园的守夜人", "paris_salon_wit", bgm_duration_s=75.0),
        act("act3", "第三幕·强盗请客该颁“刺激消费奖”吗？兼谈衙门渗水管道", "broken_window_alley", bgm_duration_s=75.0),
        act("act4", "第四幕·六万法郎歌剧院补贴：谁在为贵族看戏买单？", "candle_makers_petition", bgm_duration_s=75.0),
        act("act5", "第五幕·真基建与面子工程：花公款与花私钱的分水岭", "seine_evening_clarity", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: The Disbanding Troops Panic in the 1850 Assembly ---
        motif("b04_01", "act1", "parliament_gavel_hall", gap_after_s=0.20),
        dlg("b04_02", "act1", "narrator", "历史旁白", "[warmly] 第四夜，巴黎国民议会迎来一场火药味十足的预算大辩论。财政紧张，有人提议裁减十万名和平时期多余的常备兵和闲职官员，替老百姓减税。话音未落，反对声差点掀翻屋顶。", acoustic_space="dry", gap_after_s=0.24),
        sfx("b04_03", "act1", "Crisp synchronized leather military boots marching steadily across a stone Paris courtyard and halting sharply on granite cobblestones, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.18),
        dlg("b04_04", "act1", "deputy_mont", "蒙托邦议员", "[dramatically] [angry] 绝对不行！这十万大兵和衙门闲员，朝廷每年发给他们一亿法郎薪水！他们拿这笔钱买军靴、啃法棍、买蜡烛、喝红酒，是巴黎最稳的大客户！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_05", "act1", "deputy_mont", "蒙托邦议员", "[condescending] 巴斯夏，你今天大手一挥把这十万人裁了，明天巴黎市场上瞬间蒸发一亿法郎总需求！面包房滞销、鞋铺关门、商贩喝西北风，这责任你担得起吗？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_06", "act1", "candle_boss", "杜邦会长", "[dramatically] 议员说得太对了！军营和各部委衙门，光晚上办公点蜡烛每年就从我厂里订走十万根！裁掉闲差，不是硬生生砸咱们生意人的饭碗吗？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_07", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [sighs] 哎哟，听着挺吓人啊！我家面包店斜对面就是个税务闲差办事处，里头二十个科员整天喝茶看报纸，可每天中午确实都来买我二十个热法棍呀！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_08", "act1", "apprentice_luc", "吕克", "[curious] 是啊巴斯夏先生，咱们鞋铺每年也接不少军靴订单呢！要是把多余人马和铁饭碗全撤了，市场上的总消费不就真少了一大块吗？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_08b", "act1", "madame_claire", "玛丽夫人", "[wryly] [sarcastic] 照杜邦会长这妙算，我干脆在织布坊多雇十个整天喝茶打盹的闲人，每天光给他们发工钱买法棍，我家织布坊岂不越养闲人越发财？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_09", "act1", "host_su", "苏晚星", "[curious] 这可太戳现代听众的痛点了！今天一提精简臃肿机构、削减低效开支，立马就有人喊“公家少花钱会打击总需求”。巴斯夏议员，这道题您怎么破？", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 2: The Bucket Trick & Fifty Watchmen Guarding One Apple Tree ---
        sfx("b04_10", "act2", "Metal tin ladle scooping water loudly from one side of a wooden bucket and pouring it splashing back into the opposite side of the same bucket, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b04_11", "act2", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 诸位先听这水声！我拿一把铁勺，从木桶左边舀起一瓢水，哗啦倒进同一个木桶右边，然后激动地大喊：“快来看神迹，水桶里的水暴涨了一瓢！”你们信吗？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_12", "act2", "madame_claire", "玛丽夫人", "[chuckles] [sarcastic] 噗！谁信谁傻子呀！水还是原来那桶水，左边少一瓢，右边多一瓢，一滴也没多出来，倒来倒去还洒地上半碗呢！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_13", "act2", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [seriously] 玛丽夫人一针见血！现在我只问蒙托邦议员一个小学生都能答的问题：政府自己不种小麦、不织布、不打鞋底，它手里那一亿法郎军饷和官俸，到底是从哪儿变出来的？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_14", "act2", "deputy_mont", "蒙托邦议员", "[dismissive] 这还用问？当然是从全法国纳税人兜里收上来的税款呗！", acoustic_space="vast_hall", gap_after_s=0.20),
        dlg("b04_15", "act2", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [seriously] 破案啦！老博诺姆，你每天光看见对面那二十个闲职科员拿着公家发的一百法郎来买你的法棍——这是“看得见的”！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_16", "act2", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 可你忘了，“看不见的”是税吏前一天先敲开你的店门、敲开玛丽夫人的织布坊、敲开全城农夫的门，从你们兜里生生收走了这一百法郎税钱！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_17", "act2", "baker_bonhomme", "老博诺姆", "[earthy] [gasps] 哎哟喂！合着那帮科员花在我柜台上的钱，本来就是税吏昨天刚从我后院抽走的血汗钱？！等于我自己掏钱请他们吃我的免费面包？！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_18", "act2", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [warmly] 大叔算盘一下拨响啦！如果不收这笔多余的税、把那十万冗员裁撤归民，这一亿法郎不会凭空消失，它稳稳留在老博诺姆、玛丽夫人和千万纳税人自己兜里！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_19", "act2", "madame_claire", "玛丽夫人", "[warmly] 没错！税负一轻，我立刻给家里添面包、给女工涨工钱买皮鞋、给厂里添新纱锭！那一亿法郎一分不少照样花在市场上，总需求压根没少一分钱！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_20", "act2", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 而且真正惊人的差距才刚刚露出水面：这十万精壮小伙子脱下闲差制服回到民间，一边花钱消费，一边开始亲手种粮食、盖房子、做家具、修铁路！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_20b", "act2", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 我绝不反对保家卫国的必要军防，就像果园必须雇一位尽责的看园人；可为了“拉动苹果消费”硬雇五十个看园人守着一棵苹果树，最后连树带果子都被他们吃光了！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b04_21", "act2", "apprentice_luc", "吕克", "[excited] 我明白了！养闲人时，全国光吃不干活，老百姓交税养着他们白白耗粮食；裁掉闲差减了税，市场消费总额一样大，全社会还凭空多出十万个造真东西的生力军！", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 3: The Generous Pickpocket Medal + Leaky Tax Pipe ---
        motif("b04_22", "act3", "paris_cafe_salon", gap_after_s=0.20),
        dlg("b04_23", "act3", "narrator", "历史旁白", "[wryly] 散会后，大伙儿走进街角咖啡沙龙。蒙托邦议员仍嘟囔着“花税钱总能带旺酒馆和商店”。巴斯夏端起咖啡杯，顺手抛出一个让全法国笑掉大牙的“好心强盗”段子。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b04_24", "act3", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 蒙托邦议员，照您刚才那套逻辑，昨晚有个飞贼钻进老博诺姆后窗，顺走一百法郎。今天一早，飞贼大摇大摆走进酒馆点红酒、去裁缝店做礼服，花得痛快极了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_25", "act3", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 飞贼被捕后站在法庭上理直气壮喊：“法官大人，我把这一百法郎全花在市场上了，养活了酒馆老板和裁缝师傅，我拉动了内需！您不该判我坐牢，该给我颁勋章呀！”", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_26", "act3", "baker_bonhomme", "老博诺姆", "[earthy] [angry] 颁他个大头鬼勋章！他要是不偷我这一百法郎，我自己一样会拿去买酒买衣裳买面粉，凭啥他偷去花就成刺激消费的大善人了？！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_27", "act3", "bastiat", "弗雷德里克·巴斯夏", "[calmly] [wryly] 看，面对飞贼，大伙儿脑子清醒得很。可只要把“飞贼”换成“冗官闲差”，把“偷走”换成“收税补贴”，怎么就有那么多人看着聚光灯下的消费单热泪盈眶呢？", acoustic_space="studio_warm", gap_after_s=0.24),
        sfx("b04_27b", "act3", "Heavy brass office rubber stamp thumping repeatedly on stacks of tax forms beside coins rattling faintly through a wooden counting chute, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("b04_27c", "act3", "madame_claire", "玛丽夫人", "[wryly] 更扎心的是玛丽我刚说的“洒地上半碗水”！从乡下农夫兜里收走十法郎，经过税吏、县署、省署、财政部一路盖章发薪，最后真正回到民间消费的，能剩七法郎就谢天谢地！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_27d", "act3", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 说得太准！我原书里讲过老博诺姆卖一桶葡萄酒交五法郎税的故事——税吏拿五法郎去帽子店买帽，人们欢呼税款救活了帽子匠，却忘了博诺姆本可以自己去买帽或买靴，还省下了官僚过路费！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_28", "act3", "host_su", "苏晚星", "[chuckles] [warmly] 哈哈，太毒舌了！聚光灯永远只照着公家发钱花钱的那一幕，没人去拍纳税人交完苛税后，默默把菜篮子里的肉放回货架的那一幕！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 4: The 60,000-Franc Opera Subsidy Debate ---
        sfx("b04_29", "act4", "Grand theatrical velvet curtain swishing open on an empty ornate opera stage followed by delicate tuning notes of a solo violin and wooden cello bow, pure foley, no human voice", duration_seconds=2.7, gap_after_s=0.20),
        dlg("b04_30", "act4", "deputy_mont", "蒙托邦议员", "[condescending] 慢着巴斯夏！裁闲兵就算你说得通，可议会刚投票拨六万法郎补贴巴黎豪华歌剧院，这总归是高雅善政吧？砍掉它，大提琴手和舞者岂不全丢了饭碗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_31", "act4", "candle_boss", "杜邦会长", "[warmly] 就是！歌剧院舞台金碧辉煌，每晚点三百支上等白蜡烛，那是法兰西艺术的脸面，养活多少艺术家呀！", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b04_32", "act4", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 艺术当然高贵，我本人也是狂热的大提琴迷！可咱们先别谈情怀，先算账——请问这六万法郎歌剧院补贴，是从谁兜里抽出来的？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_33", "act4", "madame_claire", "玛丽夫人", "[angry] 还不是从全法国种土豆的农夫、踩织布机的女工和做面包的博诺姆大叔身上，一法郎一法郎收上来的税！农夫一辈子进过巴黎豪华歌剧院大门吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_34", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 看到了吗？舞台上看得见的，是那六万法郎养活了大提琴手、舞台画师和卖豪华包厢票的剧场经理，顺带让巴黎富豪半价听了高雅歌剧。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_35", "act4", "bastiat", "弗雷德里克·巴斯夏", "[solemn] 而看不见的，是全法国数万户交税的普通家庭各自少花了几个法郎——结果乡下修补屋顶的瓦匠、卖冬靴的吕克、做木椅的木匠平白丢掉了正好价值六万法郎的订单！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_36", "act4", "apprentice_luc", "吕克", "[sighs] [angry] 敢情这不是“用公款多养活了一批艺术家”，而是强迫穿破棉袄的穷鞋匠少吃顿肉，去补贴穿燕尾服的大老爷听打折歌剧呀！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_36b", "act4", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [sarcastic] 最讽刺的是流程最后一步！先从波尔多农夫碗里挖走买土豆的税银，换成巴黎歌剧院的丝绒包厢，最后政客站在水晶吊灯下慷慨激昂宣布：“要没有官府补贴，法兰西文明就完蛋啦！”", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_36c", "act4", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哈哈，敢情拿我们乡下人的血汗钱给大老爷补贴戏票，反倒成了政客的大仁大德，顺手还把咱们老百姓说成不懂艺术的粗人啦！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_37", "act4", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 说得透彻！如果巴黎富豪真心爱听歌剧，他们自己掏钱买全价票照样能养活世界一流歌剧院；拿穷人的面包税去给富人娱乐买单，既没增加一分总就业，还败坏了社会公道！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 5: Genuine Public Services vs White-Elephant Public Works + E005 Hook ---
        sfx("b04_38", "act5", "Heavy granite paving stones clunking firmly onto a damp stone roadbed with mason chisels tapping steadily beside a flowing French river bridge, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.18),
        dlg("b04_39", "act5", "host_su", "苏晚星", "[curious] 巴斯夏议员，那您是不是反对政府收一分税、修一条路呢？比如保卫国土的必要军队、审案的法庭、大家天天走的石板大桥，这些公家开支您怎么评价？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_40", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [calmly] 问得极好，别把我当成不要政府的疯子！我书里写得清清楚楚：如果收老百姓一百法郎税，换回来价值一百五十法郎的安全国防、公正司法或急需大桥，那是大赚特赚的好买卖！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_41", "act5", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 我唯一痛打的，是那种为了“创造就业”而凭空硬造出来的没用工程——比如把好好的石板路挖开再重铺、在没人去的荒山修豪华凯旋门、或者硬养十万没事干的闲差！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_42", "act5", "baker_bonhomme", "老博诺姆", "[earthy] 我懂了！判断一项公共工程值不值，别听政客吹它“雇了多少工人、花了多少钱”，要问老百姓：“修完这玩意儿，到底值不值从大伙儿兜里掏出的血汗税？”", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_42b", "act5", "host_su", "苏晚星", "[warmly] 放到今天也一针见血！花钱修大家天天用、能大幅降物流成本的高铁大桥叫真基建；在荒郊野外盖空荡荡的豪华门楼叫面子工程，花的是看得见的预算，亏的是百姓看不见的实惠！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_42c", "act5", "madame_claire", "玛丽夫人", "[wryly] 说句掏心窝子的大实话：天底下花钱最精明、最不舍得糟蹋一分银子的，永远是拿自己血汗钱过日子的老百姓；至于帮别人花税款的委员会，往往花得最大手大脚，还最不心疼！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_43", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 满分答案！衡量公家服务，永远只看它给老百姓省了多少事、创了多少真价值，绝不看它烧掉了多少银子！", acoustic_space="studio_warm", gap_after_s=0.24),
        sfx("b04_44", "act5", "Sparkling champagne cork popping brightly in a Paris banquet hall with fine crystal goblets clinking festively and carriage harness bells jingling outside, pure foley, no human voice", duration_seconds=2.6, gap_after_s=0.20),
        dlg("b04_45", "act5", "apprentice_luc", "吕克", "[excited] 哎哟各位快看窗外！香槟喷得老高！那位开镶金马车、一晚上打赏几百法郎的花花大少蒙多尔又在办豪华派对啦！街坊全夸他花钱如流水，是巴黎商贩的大恩人呢！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_46", "act5", "madame_claire", "玛丽夫人", "[wryly] 可不是嘛！反倒是他那位穿朴素大衣、赚五万存三万的亲弟弟阿里斯特，天天被街坊背后戳脊梁骨，骂他是个不肯花钱的铁公鸡！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_47", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 哈哈，世人对“挥霍阔少”和“节俭实干家”的误解，是整本《看得见的与看不见的》里最精彩的大反转！明晚咱们就查查这对亲兄弟的账本，看看谁才是巴黎工匠真正的大恩人！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b04_48", "act5", "narrator", "历史旁白", "[warmly] 下一集，《花钱如流水是恩人吗：浪子阔少与节俭人的暗账》。省下来的钱真的躲在床底下发霉吗？咱们明晚揭晓！", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E004",
        chapter_number=4,
        title="裁军与铁饭碗_政府养闲人为什么没增加总需求",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e005_thrift_vs_spendthrift() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·香槟豪宴与铁公鸡：巴黎街头最流行的误会", "paris_salon_wit", bgm_duration_s=75.0),
        act("act2", "第二幕·两兄弟年入五万法郎：浪子蒙多尔的“明账光环”", "broken_window_alley", bgm_duration_s=75.0),
        act("act3", "第三幕·大反转！阿里斯特不是守财奴阿巴贡，三万法郎去哪了？", "paris_salon_wit", bgm_duration_s=75.0),
        act("act4", "第四幕·五年后的天壤之别：破产典当 vs 越滚越大的实业树", "parliament_satire_march", bgm_duration_s=75.0),
        act("act5", "第五幕·木匠刨子与印钞机：戳破“免费信贷”幻觉", "seine_evening_clarity", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Mondor the Spendthrift vs Ariste the Thrifty Brother ---
        motif("b05_01", "act1", "paris_cafe_salon", gap_after_s=0.20),
        dlg("b05_02", "act1", "narrator", "历史旁白", "[warmly] 第五夜，巴黎香榭丽舍灯火通明。街坊茶余饭后最爱争论一桩怪事：挥金如土的败家阔少，和精打细算存钱投资的节俭人，到底谁对社会贡献更大？", acoustic_space="dry", gap_after_s=0.24),
        sfx("b05_03", "act1", "Festive champagne cork popping and fine crystal glasses clinking loudly over brisk horse hooves trotting on a Paris boulevard, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b05_04", "act1", "candle_boss", "杜邦会长", "[excited] [warmly] 这还用争吗？当然是人家蒙多尔大少爷！年收入五万法郎，敢花八万！每天晚宴点满我的高级香薰蜡烛，摔碎十个水晶杯眼睛都不眨！这才是活财神！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_05", "act1", "deputy_mont", "蒙托邦议员", "[condescending] 没错！花钱如流水，裁缝、花店、名厨、马车夫全跟着沾光！再瞧瞧他亲弟弟阿里斯特，同样年入五万法郎，一年只舍得花两万，硬攒下三万——活脱脱一个自私抠门鬼！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_06", "act1", "apprentice_luc", "吕克", "[curious] 哎呀，说句心里话，我平时在街上听见人夸蒙多尔少爷“有钱不攥着、肯给大伙儿发活干”，也老觉得挺有道理。要是人人都像阿里斯特那样省吃俭用，钱不就不转了吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_07", "act1", "host_su", "苏晚星", "[curious] 巴斯夏议员，这个争论穿越一百七十年到了今天，简直丝毫没降温！今天依然天天有人说“奢侈挥霍拉动高端消费，老百姓爱存钱拖累经济”。您怎么给阿里斯特平反？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_08", "act1", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [wryly] 哈哈，我当年写《节俭与奢侈》这篇时就拍着桌子乐！为什么全巴黎都误会阿里斯特？因为大家把“储蓄”和莫里哀喜剧里那个叫阿巴贡的怪老头混为一谈啦！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_08b", "act1", "madame_claire", "玛丽夫人", "[chuckles] 莫里哀喜剧里那个守财奴阿巴贡，半夜把一万金币装进铁盒埋在自家菜园土坑里，整天哆哆嗦嗦守着土堆！现实里除了疯子，哪有聪明人把银子埋地里长毛呀？", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 2: Following Mondor's 50,000 Francs ---
        sfx("b05_09", "act2", "Delicate crystal glass shattering on marble floor followed by silk fabric rustling and gold coins tossed carelessly onto a velvet tray, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b05_10", "act2", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 咱们先把两位兄弟的账本摊开！哥哥蒙多尔和弟弟阿里斯特，今年手头各有五万法郎收入。先看哥哥蒙多尔，他那花钱阵仗可太“看得见”了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_11", "act2", "baker_bonhomme", "老博诺姆", "[earthy] 我亲眼见过！蒙多尔少爷先花两万过体面日子，剩下三万法郎全拿去买顶级香槟、放彻夜大烟花、定做只穿一晚的丝绸礼服、养八匹只拉风不干活的纯血赛马！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_11b", "act2", "deputy_mont", "蒙托邦议员", "[dramatically] 每回蒙多尔马车驶过香榭丽舍，整条街五百双眼睛全看傻了！花店小妹、酒窖掌柜、绸缎庄老板齐声高喊少爷万岁，这还不算造福巴黎经济？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_12", "act2", "candle_boss", "杜邦会长", "[warmly] 瞧瞧！这三万法郎清清楚楚落进了香槟商、烟花匠、丝绸裁缝和赛马场伙计兜里！实打实养活了几十号工匠，光凭这点谁敢说他不是大恩人？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_12b", "act2", "host_su", "苏晚星", "[wryly] 难怪大家总给浪子鼓掌！香槟喷泉、霓虹排场和镶金马车全摆在大街正中央，谁路过都能看个满眼；可勤俭人的善行躲在账本后面，一点不张扬！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_13", "act2", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 别急，我现在问一个最关键的问题：弟弟阿里斯特自己家也体面花了两万法郎过日子，剩下那三万法郎，他到底拿去干嘛了？真埋在菜园地底下发霉了吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_14", "act2", "madame_claire", "玛丽夫人", "[chuckles] [excited] 才没有呢！这事儿我最清楚，因为阿里斯特先生上周刚跟我签完借款合同，借给我一万五千法郎呢！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_15", "act2", "deputy_mont", "蒙托邦议员", "[gasps] 啊？他把省下来的钱借给你干嘛？", stability=0.0, acoustic_space="studio_warm", gap_after_s=0.20),
        # --- ACT 3: Where Ariste's Unseen 30,000 Francs Actually Went! ---
        sfx("b05_16", "act3", "Crisp wooden carpenter plane shaving oak planks beside iron hammers forging spinning-loom parts and mason trowels building a sturdy brick bakery oven, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("b05_17", "act3", "madame_claire", "玛丽夫人", "[excited] [warmly] 我拿这一万五千法郎，立刻请铁匠和木匠造了五台崭新的高效率织布机，还把旧厂房屋顶重新翻修了一遍！那笔钱三天不到就全变成了铁匠、木匠和瓦工的工钱！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_18", "act3", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 嘿嘿，另外一万法郎阿里斯特先生存进巴黎银行，银行低息贷给了我！我拿它新砌了两座省炭大烤炉，雇了泥瓦匠、铁炉匠，还多招了两名面包学徒！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_19", "act3", "apprentice_luc", "吕克", "[excited] 剩下五千法郎我也打听到了！阿里斯特先生买下郊外一片荒坡，雇了十几个农夫挖水渠、种果树、修石围墙！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_20", "act3", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [warmly] 啪！真相大白！哥哥蒙多尔挥霍三万法郎，发给了烟花匠和香槟侍者；弟弟阿里斯特省下三万法郎，通过储蓄投资，一分不少全发给了铁匠、瓦工、木匠和农夫！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_20b", "act3", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 只不过蒙多尔是在香榭丽舍大街敲锣打鼓放烟花，全城看得见；阿里斯特的银子安安静静通过银行和借据流进了工坊后院，路人瞧不见，就瞎骂他是铁公鸡！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_21", "act3", "host_su", "苏晚星", "[excited] 天呐，大反转来得太猛烈了！原来正常的节俭储蓄，压根不是把钱憋死在枕头底下——它和挥霍消费一样，百分之百流进了市场、百分之百给普通劳动者发了工资！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_22", "act3", "bastiat", "弗雷德里克·巴斯夏", "[seriously] [warmly] 第一局“有没有给工匠发工资”，兄弟俩打成平手，都是三万法郎！可到了第二年乃至第五年，兄弟俩拉开的天壤之别，才真正让人倒吸一口凉气！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 4: One Year & Five Years Later — Ashes & Auction vs Productive Capital ---
        sfx("b05_23", "act4", "Empty wine bottles clinking hollowly on a quiet dawn terrace transitioning to steady vibrant bakery ovens crackling and brisk looms humming smoothly, pure foley, no human voice", duration_seconds=2.7, gap_after_s=0.20),
        dlg("b05_24", "act4", "narrator", "历史旁白", "[warmly] 转眼过了几年。巴黎清晨阳光照进两兄弟的院子，一幅让所有围观街坊彻底闭嘴的对比画面摆在了眼前。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b05_25", "act4", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 先敲开浪子哥哥蒙多尔的门！去年那三万法郎挥霍完毕，天亮之后地上剩下了什么？一堆放完的烟花纸屑、几十个空香槟瓶、几只碎水晶杯！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_26", "act4", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 他不仅没多出一分新产值，甚至因为挥霍无度、借债啃老，第五年不得不把祖宅和良田全拿去拍卖还债，解雇马车夫、厨子和园丁，连一法郎工钱都发不出来了！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_27", "act4", "madame_claire", "玛丽夫人", "[warmly] [excited] 再来瞧弟弟阿里斯特这边！他那三万法郎照样养活了一大批工匠，可一年后，大地上实打实多出了五台新织布机、两座大烤炉和一片挂满果子的果园！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_28", "act4", "baker_bonhomme", "老博诺姆", "[earthy] 对呀！靠着这两座省炭大烤炉，我烤出来的法棍又香又便宜，全街坊都能少花钱吃饱饭！我按期还给阿里斯特利息，到了第五年，他的本钱滚大了一倍，养活的工匠也是从前的两倍！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_29", "act4", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [warmly] 看见“看得见的”与“看不见的”有多震撼了吗？挥霍是把宝贵劳动烧成一夜烟花，烧完归零；储蓄投资是把同等劳动铸成机器、烤炉和良田，年年下金蛋，让全社会永远更富裕！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_30", "act4", "apprentice_luc", "吕克", "[warmly] 怪不得呢！我以前总听街头小报骂存钱老板小气，现在算明白这笔暗账才知道——每多一台借储蓄造出来的新机器，全城工人的生产率和真工资才能实打实往上涨！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_30b", "act4", "candle_boss", "杜邦会长", "[sighs] [wryly] 哎呀，照这么算，蒙多尔少爷今年破产之后，连一根普通蜡烛都买不起了；反倒是阿里斯特投出来的玛丽夫人新厂房，成了我这儿最稳的大买家！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_30c", "act4", "deputy_mont", "蒙托邦议员", "[wryly] [sighs] 咳咳，好吧，这一局我勉强认输！原来阿里斯特不是把钱藏死，而是把钱投进了长庄稼、生工具的活水池里！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_30d", "act4", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 没错！这就是人类走出贫困的唯一阶梯：上一代人省下一点余粮造出铁犁和纺车，下一代人才能站在这副肩膀上轻松养活十倍人口！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_31", "act4", "host_su", "苏晚星", "[warmly] 不过巴斯夏议员，咱们也得客观补一句：消费本身不是坏事，大家辛苦挣钱就是为了体面生活嘛！您反对的不是正常享受，而是把“败家挥霍”吹成“拯救经济的恩人”！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_32", "act4", "bastiat", "弗雷德里克·巴斯夏", "[warmly] [chuckles] 正是！阿里斯特每年也舒舒服服花两万法郎享受生活呀！我只是要帮老实存钱、建工厂、造工具的普通人摘掉“守财奴”的冤枉帽子——他们才是社会进步的真脊梁！", acoustic_space="studio_warm", gap_after_s=0.26),
        # --- ACT 5: James & William's Carpenter Plane + Free Credit Fallacy + E006 Hook ---
        sfx("b05_32b", "act5", "Smooth wooden hand plane gliding crisply along a cedar workbench plank curling thin wood shavings neatly onto sawdust floor, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("b05_32c", "act5", "apprentice_luc", "吕克", "[curious] 巴斯夏先生，有人还骂阿里斯特借钱给玛丽夫人收利息是“不劳而获的吸血鬼”，这事儿到底该怎么看呀？", acoustic_space="studio_warm", gap_after_s=0.22),
        dlg("b05_32d", "act5", "bastiat", "弗雷德里克·巴斯夏", "[warmly] 我用木匠雅克和威廉借刨子的故事一秒讲透！雅克省吃俭用十天，亲手打出一把好木刨。邻居威廉借走这把刨子用一年，多打出三百张木桌，年底还完刨子顺便分给雅克几块好木板当利息。", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_32e", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [warmly] 请问谁吃亏了？威廉借刨子多赚了十倍钱，雅克延迟享受得到了诚实回报！利息不是剥削，而是奖励人类“愿意今天少吃一口、攒出好工具帮明天增产”的奖章！", acoustic_space="studio_warm", gap_after_s=0.24),
        sfx("b05_33", "act5", "Mechanical 1850 banknote printing press rolling briskly and stacking crisp fresh paper currency sheets beside a heavy wooden farm plow resting silently, pure foley, no human voice", duration_seconds=2.7, gap_after_s=0.20),
        dlg("b05_34", "act5", "deputy_mont", "蒙托邦议员", "[dramatically] 等等！巴斯夏，既然你刚才自己承认了，织布机、木刨和资本这么宝贵，那干嘛苦哈哈靠节俭慢慢攒呀？咱们议会直接开一家“人民免息信贷银行”，猛印纸钞白借给每个人不就行了？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_35", "act5", "candle_boss", "杜邦会长", "[excited] 对呀！要是国家银行印十亿法郎纸币，零利息分给大家做本钱，人人手握巨款，全法国岂不一夜变成工业超级大国？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_36", "act5", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 哎哟，这招“印钞变资本”当年我跟巴黎激进派吵了整整十四个回合！来，咱们做个一秒就破功的小实验！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_37", "act5", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 假设乡下老农手里有一架实实在在的木犁，邻居想借去耕地。现在我开动印钞机，把这张“木犁借条”唰唰唰复印十张，发给十个农夫——请问地里能突然长出十架木犁吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_38", "act5", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哈哈，哪能长出十架木犁呀！木犁还是孤零零那一架，顶多十个农夫举着纸条抢成一团，把木犁租金炒高十倍！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_39", "act5", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 说透了！信贷从来不会凭空变出新资本，它只是把闲着的真工具，借给更能发挥它本事的人！真正的资本，永远只能是实打实省下来的粮食、铁锭、木料和机器！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_40", "act5", "bastiat", "弗雷德里克·巴斯夏", "[coldly] 不靠踏实劳动和储蓄积累实物资本，光指望印钞机猛印纸片，唯一变多出来的只有物价标签上的零，绝不会多出一块面包或一台织布机！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_40b", "act5", "host_su", "苏晚星", "[chuckles] [warmly] 哈哈，要是猛印纸钞就能消灭贫穷，全世界的穷国早买十台大印刷机，午饭前就全部实现共同富裕啦！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_40c", "act5", "madame_claire", "玛丽夫人", "[warmly] 这么一串下来全透亮了！真正的财富只能靠干活加省钱攒出来——偷懒靠砸玻璃、封太阳、挖断路、印废纸，全是糊弄外行的把戏！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_41", "act5", "host_su", "苏晚星", "[curious] 可我越听越好奇：既然道理这么明白，为什么全社会那么多聪明人，最后全都忍不住跑去敲议会大门、求国家给自己兜底呢？", acoustic_space="studio_warm", gap_after_s=0.24),
        motif("b05_42", "act5", "parliament_gavel_hall", gap_after_s=0.20),
        dlg("b05_43", "act5", "deputy_mont", "蒙托邦议员", "[dramatically] 因为国家就是万能大救星嘛！明天议会大厅门口，农夫要补贴、厂长要免息贷款、工人要保底包养、剧场要资助，大伙儿都指望国家兜底呢！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b05_44", "act5", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [wryly] 这正是我在病榻前拼尽最后一口气写下《国家论》和《法律》的缘由。明晚收官之夜，咱们就把那句流传百年的神级定义摆上台面——国家到底是什么？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b05_45", "act5", "narrator", "历史旁白", "[warmly] 下一集，第一季大结局，《国家是什么：每个人都想靠别人养活的宏大幻觉》。重返一八五零年冬日罗马，聆听巴斯夏生命最后时刻的清醒遗言。", acoustic_space="dry", gap_after_s=0.60),
    ]
    return EpisodeCueSheet(
        episode_id="E005",
        chapter_number=5,
        title="花钱如流水是恩人吗_浪子阔少与节俭人的暗账",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.2,
        acts=acts,
        cues=cues,
    )


def build_e006_state_fiction_rome_farewell() -> EpisodeCueSheet:
    acts = [
        act("act1", "第一幕·一八五〇巴黎请愿潮：人人都把国家当成聚宝盆", "parliament_satire_march", bgm_duration_s=75.0),
        act("act2", "第二幕·传世金句诞生：每个人都想靠别人养活的宏大幻觉", "paris_salon_wit", bgm_duration_s=75.0),
        act("act3", "第三幕·《法律》的警钟：合法掠夺，与“反对官办面包”不等于讨厌面包", "candle_makers_petition", bgm_duration_s=75.0),
        act("act4", "第四幕·一八五〇年平安夜罗马病榻：六年绝唱与巴黎老街坊来信", "seine_evening_clarity", bgm_duration_s=75.0),
        act("act5", "第五幕·绝笔“真理”：送给后世普通人的那双透视眼", "seine_evening_clarity", bgm_duration_s=75.0),
    ]
    cues = [
        # --- ACT 1: Everyone rushes to Parliament demanding subsidies AND tax cuts ---
        motif("b06_01", "act1", "parliament_gavel_hall", gap_after_s=0.20),
        dlg("b06_02", "act1", "narrator", "历史旁白", "[warmly] 终章之夜。一八五零年秋天，巴黎波旁宫门前挤满了形形色色的请愿队伍。每个人都举着厚厚的诉状，心里怀着同一个既天真又疯狂的美梦。", acoustic_space="dry", gap_after_s=0.24),
        sfx("b06_02b", "act1", "Thick bundles of parchment petitions thumping heavily one after another onto a massive wooden parliamentary table with brass bell ringing crisply, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.18),
        dlg("b06_03", "act1", "candle_boss", "杜邦会长", "[dramatically] 议员老爷，国家得给我们蜡烛厂发高额补贴、加满关税，不然我们活不下去呀！不过我可先说好，明年不许加我的营业税！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_03b", "act1", "apprentice_luc", "吕克", "[wryly] 门口排队的名单长着呢！小麦庄园主要求国家保底高价收购粮食，剧院经理要公家包圆戏票，连马车行会都要国家给每匹老马发退休金！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_03c", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [wryly] 听完他们喊，我都差点心动啦——要不我也写张条子，让国家明早给我面包店发五千法郎补贴，顺便免掉我十年房租？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_04", "act1", "deputy_mont", "蒙托邦议员", "[dramatically] 统统安排！我向全法国选民承诺：国家就是无所不能的慈祥母亲！免费贷款、免费补贴、免费铁饭碗、免费大工程全安排上，同时——把大家的税率砍掉一半！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_05", "act1", "baker_bonhomme", "老博诺姆", "[earthy] [curious] 等等议员！一边给全法国人人发大红包、包养到底，一边还把税收砍掉一半？天上真掉大金饼子了？这笔账您打算拿啥补窟窿呀？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_06", "act1", "madame_claire", "玛丽夫人", "[chuckles] [sarcastic] 博诺姆大叔你还看不明白吗？杜邦会长想要补贴，指望从咱俩兜里掏；农夫想要补贴，指望从织布坊掏；大伙儿围成一个大圆圈，谁都觉得自己能白占便宜！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_07", "act1", "host_su", "苏晚星", "[seriously] 巴斯夏议员，您此刻脸色很苍白，嗓子也哑了，却依然走上了议会讲台——历史上您就在这时写出了那篇轰动欧洲的《国家论》！", acoustic_space="vast_hall", gap_after_s=0.24),
        # --- ACT 2: The Immortal Definition of "The State" + The Two-Hands Circle ---
        sfx("b06_08", "act2", "Single deliberate heavy oak cane tapping once against marble assembly hall steps followed by hushed absolute stillness in the vast room, pure foley, no human voice", duration_seconds=2.4, gap_after_s=0.20),
        dlg("b06_09", "act2", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [wryly] 诸位，今天我不绕弯子了。我给全欧洲留下一句最简短、最刺耳、但也最清醒的定义——国家到底是什么？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_10", "act2", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [seriously] 国家就是那个宏大的幻觉——在这个幻觉里，每个人都拼命想靠别人的腰包来养活自己！", acoustic_space="vast_hall", gap_after_s=0.28),
        dlg("b06_11", "act2", "apprentice_luc", "吕克", "[gasps] [excited] “每个人都想靠别人养活自己的宏大幻觉”！老天爷，这句话像一盆冰水，瞬间把刚才那股燥热全浇清醒了！", stability=0.0, acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_11b", "act2", "deputy_mont", "蒙托邦议员", "[angry] 巴斯夏，你太尖酸刻薄了！老百姓生活不容易，找国家伸手要保障、要照顾，难道不是人之常情吗？", acoustic_space="vast_hall", gap_after_s=0.22),
        dlg("b06_11c", "act2", "bastiat", "弗雷德里克·巴斯夏", "[wryly] [chuckles] 哈哈，您瞧瞧每天寄到巴黎议会的自相矛盾电报！上午刚拍来急电喊“救救我们，快发补贴、快建铁饭碗”，下午又拍来急电大骂“税官抢钱，快砍一半苛捐杂税”！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_12", "act2", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 你们想想，这幻觉多滑稽！大伙儿总把国家当成一只神奇的独角兽，以为它自己长着摇钱树，随便抖一抖就能给所有行业免费洒金币。", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_13", "act2", "bastiat", "弗雷德里克·巴斯夏", "[wryly] 可真相呢？国家长着两只手——一只粗糙的左手，负责挨家挨户收税掏钱；一只戴着白手套的温柔右手，负责在闪光灯下往外发补贴、发福利！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_14", "act2", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 哎哟！左手先从我口袋里掏走十法郎，右手再笑着塞回我八法郎，说“快感谢恩典”——那凭空少掉的两法郎去哪儿了？", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_15", "act2", "madame_claire", "玛丽夫人", "[sarcastic] 少掉的那两法郎，成了养活那群负责左手倒右手的官老爷、盖大印的办事处和豪华公车的跑路费喽！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_15b", "act2", "host_su", "苏晚星", "[chuckles] [wryly] 简直像一百个人围成圆圈坐着，每个人都伸手去摸右边邻居的口袋，心里还偷着乐，以为全天下发现了不用干活就能发财的永动机！", acoustic_space="vast_hall", gap_after_s=0.24),
        dlg("b06_16", "act2", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 没错！全法国一千万个家庭互相把手伸进隔壁邻居兜里掏钱，最后谁也没凭空变富，反而因为人人忙着掏兜、不肯踏实干活，外加层层损耗，大伙儿一起变穷了！", acoustic_space="vast_hall", gap_after_s=0.26),
        # --- ACT 3: "The Law" — Legal Plunder + Government vs Society ---
        sfx("b06_17", "act3", "Heavy brass scales of justice settling evenly on a wooden courtroom bench beside thick leather law volumes closing firmly, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.20),
        dlg("b06_18", "act3", "narrator", "历史旁白", "[solemn] 就在《看得见的与看不见的》付印前一个月，一八五零年六月，巴斯夏还写下了另一部传世名篇——《法律》。他用最尖锐的刀锋，解剖了权力和贪欲的合谋。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b06_19", "act3", "host_su", "苏晚星", "[curious] 巴斯夏议员，您在《法律》里提出了一个震撼后世的词，叫“合法掠夺”。法律不就是为了惩治强盗、保护好人的吗？怎么会变成“掠夺”呢？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_20", "act3", "bastiat", "弗雷德里克·巴斯夏", "[seriously] 法律原本的使命极其简单、极其神圣：保护每个人的生命、自由，以及你靠自己双手挣来的财产，不受任何强盗和恶霸侵犯！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_20b", "act3", "bastiat", "弗雷德里克·巴斯夏", "[calmly] 人类在这个世界上养活自己，其实只有两条路：第一条叫生产与自愿交换，靠手艺挣钱；第二条叫掠夺，不劳而获抢别人的果子！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_20c", "act3", "apprentice_luc", "吕克", "[excited] 哎呀！咱前五集聊过的砸窗户、封太阳、挖断路、养闲差、印废纸，拆到最底层，全都是在替“不生产光想占便宜”穿一件体面的大衣裳呀！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_20d", "act3", "madame_claire", "玛丽夫人", "[seriously] 真是一针见血！强盗拿刀拦路抢劫，大家一眼就看穿是坏人；可一旦有人借着议会法案强行收高关税、发特权补贴，强盗就摇身一变成了体面老爷！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_21", "act3", "bastiat", "弗雷德里克·巴斯夏", "[coldly] 可人的天性总想走捷径：既然自己流汗干活太累，如果我能说服议会定一条偏向我的规矩——用关税挡住对手、用补贴拿别人税钱填我的账本——那我就不用冒险当强盗啦！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_22", "act3", "deputy_mont", "蒙托邦议员", "[angry] 巴斯夏！你竟敢把咱们议会正当表决通过的保护法案，说成是“掠夺”？！你反对国家办面包房、反对国家办剧院，你是不是冷血无情、巴不得百姓饿肚子没戏看？！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_22b", "act3", "bastiat", "弗雷德里克·巴斯夏", "[chuckles] [sarcastic] 哈哈，最经典的一顶大帽子又扣过来啦！蒙托邦议员总把“政府”和“社会”混成一团！我反对政府包办面包房，难道等于我讨厌吃面包、希望法国人饿死吗？", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_22c", "act3", "baker_bonhomme", "老博诺姆", "[earthy] [chuckles] 笑死我了！政府不来抢着烤面包，咱全巴黎几千家民间面包铺天不亮就把热法棍烤得喷香！正因为老百姓爱吃好面包，才更不该让官老爷垄断烤炉呀！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_22d", "act3", "host_su", "苏晚星", "[warmly] 巴斯夏这一针戳得太妙了！反对官府大包大揽，绝不等于反对老百姓互助合作；相反，正是因为相信民间千千万万普通人的智慧，才不该把一切都交给衙门管死！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_23", "act3", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [seriously] 辨别恶法只需一个试金石：如果一条法律拿走甲的劳动成果，转手白送给乙，让乙靠甲的汗水获利，哪怕它盖了一百个合法大印，骨子里依然是掠夺！", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_24", "act3", "madame_claire", "玛丽夫人", "[seriously] 最可怕的连锁反应我想到了！一旦法律开了这个口子，原本老实织布、烤面包的人也被逼疯了：“要是我不去议会拉关系抢法案，明天就得被别人用法律薅羊毛！”", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_25", "act3", "bastiat", "弗雷德里克·巴斯夏", "[solemn] [warmly] 玛丽夫人说到了根子上！当争抢特权比做好面包更赚钱，全社会最聪明的大脑就会离开作坊，全都挤进衙门争权夺利！善政的底线，就是把法律锁回“护民防抢”的本分里！", acoustic_space="studio_warm", gap_after_s=0.28),
        # --- ACT 4: Christmas Eve 1850 — Quiet Roman Sickroom & Bastiat's Six Blazing Years ---
        motif("b06_26", "act4", "seine_quill_clock", gap_after_s=0.22),
        sfx("b06_26b", "act4", "Slow wooden autumn carriage wheels rolling gently down a quiet southern French lane fading into calm Mediterranean coastal breeze, pure foley, no human voice", duration_seconds=2.5, gap_after_s=0.18),
        dlg("b06_28", "act4", "narrator", "历史旁白", "[softly] 一八五零年秋天，四十九岁的弗雷德里克·巴斯夏因肺病恶化，乘车南下罗马静养。十二月二十四日平安夜，地中海冬日微阳洒进安静石屋，他嗓音只剩气音，目光却清澈如水。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b06_28b", "act4", "narrator", "历史旁白", "[warmly] 很少有人记得，这位出身巴约讷的乡下庄园主，直到四十三岁才在巴黎发表第一篇文章。短短六年，他忍着病痛、拉着大提琴、以笑为刃，写出了经济学史上最锋利明快的篇章。", acoustic_space="dry", gap_after_s=0.24),
        sfx("b06_27", "act4", "Gentle distant Roman church winter chimes echoing softly across a quiet sun-warmed stone courtyard as crisp parchment letters unfold slowly, pure foley, no human voice", duration_seconds=2.8, gap_after_s=0.20),
        dlg("b06_29", "act4", "host_su", "苏晚星", "[softly] [warmly] 巴斯夏先生，圣诞前夜好。我刚从巴黎赶来罗马，街角那群老朋友托我给您带了一厚摞信，还带了老博诺姆烤的新鲜干果面包。", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_30", "act4", "bastiat", "弗雷德里克·巴斯夏", "[hoarsely] [warmly] 咳……苏记者，快坐。老博诺姆那块值六法郎的大玻璃，最近没再遭殃吧？", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_31", "act4", "baker_bonhomme", "老博诺姆", "[earthy] [warmly] 巴斯夏先生您放心！我在信里给您画了新铺面呢！没被乱加苛税，我用省下来的钱换了更亮堂的大窗，顺手买了两双吕克做的新牛皮鞋，街坊天天排长队！", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_32", "act4", "apprentice_luc", "吕克", "[warmly] 先生，我也写了几句！您教大伙儿算清那笔暗账之后，我借着阿里斯特先生的储蓄贷款，用上省力新工具，在圣日耳曼街开了自己的小鞋坊，还招了两个年轻学徒！", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_33", "act4", "madame_claire", "玛丽夫人", "[warmly] [chuckles] 连杜邦会长都偷偷给我写了条子！他说不靠钉死窗户，改做香气更好、不冒黑烟的精致晚宴蜡烛，反倒卖到了全欧洲，比当年哭着告太阳体面一百倍！", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_33b", "act4", "candle_boss", "杜邦会长", "[warmly] [wryly] 咳咳，巴斯夏先生，您别笑话我这老对手——真放开手脚拼手艺、不指望衙门封窗之后，我才发现靠真本事赢得顾客点头，睡觉踏实多啦！", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_34", "act4", "bastiat", "弗雷德里克·巴斯夏", "[hoarsely] [chuckles] 哈哈……太好了，连杜邦会长都改邪归正去拼真手艺啦。听见普通人靠自己双手把日子越过越红火，比听议会里任何掌声都让我痛快。", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_34b", "act4", "bastiat", "弗雷德里克·巴斯夏", "[hoarsely] [wryly] 我这辈子唯一的遗憾，就是上天没再多借我十年光阴——不然我真想坐在巴黎议会里，继续用笑声把那些一本正经的荒唐歪理全扎破！", acoustic_space="vintage_study", gap_after_s=0.28),
        # --- ACT 5: Dying Words "La vérité..." + Timeless Epilogue ---
        sfx("b06_35", "act5", "Soft Mediterranean winter breeze gently stirring linen curtains in a serene sunlit stone room with faint distant wooden clock ticking slowly, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.22),
        dlg("b06_36", "act5", "host_su", "苏晚星", "[softly] [solemn] 先生，您这几年明明病得这么重，为什么还要拼着命把《看得见的与看不见的》写得这么幽默好玩、一字一句磨成大白话呢？", acoustic_space="vintage_study", gap_after_s=0.24),
        dlg("b06_37", "act5", "bastiat", "弗雷德里克·巴斯夏", "[hoarsely] [solemn] 因为……谬误天生占着大便宜。谬误总是嗓门洪亮、站在聚光灯下，只给你看眼前那一点甜头；而常识总是安静的、藏在暗处的，需要人多想一步才看得见。", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("b06_38", "act5", "bastiat", "弗雷德里克·巴斯夏", "[softly] [warmly] 如果经济学写成催眠的厚砖头，老百姓打着哈欠合上书，就会继续被骗子糊弄。可只要大家笑着记住一块碎玻璃、一份告太阳的请愿书、一条挖断的铁路，谎言就骗不住他们啦。", acoustic_space="vintage_study", gap_after_s=0.26),
        dlg("b06_39", "act5", "bastiat", "弗雷德里克·巴斯夏", "[hoarsely] [softly] 苏记者，替我转告一百多年后的普通朋友们……别光看台上谁在欢呼，永远记得低头问一句——那看不见的另一半，去了哪儿……真理……", stability=0.0, acoustic_space="vintage_study", gap_after_s=0.35),
        sfx("b06_40", "act5", "Peaceful gentle twilight Seine river water lapping steadily against Paris stone embankments under calm evening wind, pure foley, no human voice", duration_seconds=3.0, gap_after_s=0.22),
        dlg("b06_41", "act5", "narrator", "历史旁白", "[softly] 一八五零年十二月二十四日，四十九岁的弗雷德里克·巴斯夏在罗马安详合眼，临终前低声说出的最后两个字，正是“真理”。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b06_42", "act5", "narrator", "历史旁白", "[warmly] 一百七十多年过去，经济学家熊彼特盛赞他是人类历史上最杰出的财经评论家。砸窗户的歪理换过无数新名词，控告太阳的请愿书至今仍在世界各个角落花样翻新。", acoustic_space="dry", gap_after_s=0.24),
        dlg("b06_43", "act5", "host_su", "苏晚星", "[warmly] [solemn] 但只要下次听到有人鼓吹“破坏能刺激经济”“设卡能增加就业”“印钞能变出财富”或者“靠别人养活自己”时，你嘴角微微一笑，脑海里响起老博诺姆那声清脆的碎玻璃——", acoustic_space="studio_warm", gap_after_s=0.24),
        dlg("b06_44", "act5", "narrator", "历史旁白", "[warmly] 你就已经接过了巴斯夏送给全人类最锋利的那双透视眼。《一八五零巴黎议会讽刺剧：看得见的与看不见的》第一季全六集，到此圆满收官！感谢一路相伴，咱们下一座思想剧场再会！", acoustic_space="dry", gap_after_s=0.80),
    ]
    return EpisodeCueSheet(
        episode_id="E006",
        chapter_number=6,
        title="国家是什么_每个人都想靠别人养活的宏大幻觉",
        mode="radio_drama",
        head_pad_s=0.45,
        tail_pad_s=1.4,
        acts=acts,
        cues=cues,
    )
