#!/usr/bin/env python3
"""从固定版本的维基词典、维基百科导入网络用语（CC BY-SA 4.0）。
Import internet slang from pinned Wiktionary and Wikipedia revisions (CC BY-SA 4.0).

用法 / Usage:
  python3 tools/import_wiki.py --fetch CACHE   # 按 sources.json 的固定版本下载 / download the pinned revisions
  python3 tools/import_wiki.py CACHE           # 核对摘要，生成两份导入词表 / verify hashes, write the imported lists

只导入下面人工审阅过的词：去掉侮辱、低俗、政治、地域攻击和针对真人的说法，也去掉内置词库已有的词。
维基词典词条带「粗俗、贬义、冒犯」等标签的一律不收；拼音取自词条本身并与审阅值核对。
Only the reviewed words below are imported: insults, vulgarity, politics, regional attacks and memes aimed at real
people are left out, as are words the built-in dictionary already has. Wiktionary entries labelled vulgar,
derogatory, offensive and the like are refused; pinyin comes from the entry itself and must match the reviewed value.
"""
import hashlib,json,re,sys,time,unicodedata,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ADDED='2026-10-03'
AGENT='weavetext-hotwords/1 (https://github.com/sheep-programmer/weavetext-hotwords)'
# 简体词 → (维基词典词条, 固定版本, 审阅过的拼音)。 Simplified word → (Wiktionary entry, pinned revision, reviewed pinyin).
WIKTIONARY={
    '主包':('主包',84923523,'zhu bao'),
    '乃们':('乃們',73793691,'nai men'),
    '你开心就好':('你開心就好',60743482,'ni kai xin jiu hao'),
    '修沟':('修溝',90364558,'xiu gou'),
    '名词大动词':('名詞大動詞',92365706,'ming ci da dong ci'),
    '哈基米':('哈基米',92513460,'ha ji mi'),
    '哈基米南北绿豆':('哈基米南北绿豆',90430128,'ha ji mi nan bei lv dou'),
    '啊我死了':('啊我死了',91339172,'a wo si le'),
    '嗦嘎':('嗦嘎',78885151,'suo ga'),
    '呕泥酱':('嘔泥醬',85776972,'ou ni jiang'),
    '块陶':('塊陶',83566755,'kuai tao'),
    '小公举':('小公舉',78587628,'xiao gong ju'),
    '巴拉巴拉':('巴拉巴拉',71479951,'ba la ba la'),
    '复更':('復更',85369845,'fu geng'),
    '怒答':('怒答',50114169,'nu da'),
    '爱存不存':('愛存不存',81601069,'ai cun bu cun'),
    '抖内':('抖內',84406649,'dou nei'),
    '拍谢':('拍謝',78433570,'pai xie'),
    '拖更':('拖更',61963598,'tuo geng'),
    '掰头':('掰頭',71192558,'bai tou'),
    '扩列':('擴列',87451106,'kuo lie'),
    '旮旯给木':('旮旯給木',88054780,'ga la gei mu'),
    '木大':('木大',77616774,'mu da'),
    '森七七':('森七七',84129300,'sen qi qi'),
    '桥豆麻袋':('橋豆麻袋',91544407,'qiao dou ma dai'),
    '水啦':('水啦',86698834,'shui la'),
    '泰裤辣':('泰褲辣',91729016,'tai ku la'),
    '活字乱刷术':('活字亂刷術',90517985,'huo zi luan shua shu'),
    '深藏功与名':('深藏功與名',90698881,'shen cang gong yu ming'),
    '温拿':('溫拿',78646718,'wen na'),
    '炸号':('炸號',78588383,'zha hao'),
    '焚诀':('焚訣',90364452,'fen jue'),
    '爷关更':('爺關更',75027254,'ye guan geng'),
    '狗勾':('狗勾',81335305,'gou gou'),
    '猿粪':('猿糞',78650945,'yuan fen'),
    '兽迷':('獸迷',74183695,'shou mi'),
    '生草':('生草',83166922,'sheng cao'),
    '用魔法打败魔法':('用魔法打敗魔法',90364485,'yong mo fa da bai mo fa'),
    '申必':('申必',91633576,'shen bi'),
    '留爪':('留爪',78653079,'liu zhao'),
    '石乐志':('石樂志',78588603,'shi le zhi'),
    '神必':('神必',91637486,'shen bi'),
    '福瑞控':('福瑞控',74183710,'fu rui kong'),
    '私密马赛':('私密馬賽',85199477,'si mi ma sai'),
    '米有':('米有',78588703,'mi you'),
    '红红火火恍恍惚惚':('紅紅火火恍恍惚惚',79159534,'hong hong huo huo huang huang hu hu'),
    '红豆泥私密马赛':('紅豆泥私密馬賽',85199489,'hong dou ni si mi ma sai'),
    '紫薯布丁':('紫薯布丁',78588763,'zi shu bu ding'),
    '老天奶':('老天奶',91822035,'lao tian nai'),
    '老盆友':('老盆友',78664292,'lao pen you'),
    '肥宅快乐水':('肥宅快樂水',73624147,'fei zhai kuai le shui'),
    '肥宅快乐堡':('肥宅快樂堡',60809414,'fei zhai kuai le bao'),
    '蚌埠住':('蚌埠住',80965350,'beng bu zhu'),
    '复制文':('複製文',73409149,'fu zhi wen'),
    '车万':('車万',93038427,'che wan'),
    '酱子':('醬子',89932537,'jiang zi'),
    '锅锅':('鍋鍋',78683282,'guo guo'),
    '长辈图':('長輩圖',74177648,'zhang bei tu'),
    '闭眼冲':('閉眼衝',85011642,'bi yan chong'),
    '阿姨洗铁路':('阿姨洗鐵路',60743393,'a yi xi tie lu'),
    '阳过':('陽過',86776549,'yang guo'),
    '雀食':('雀食',90515342,'que shi'),
    '雨女无瓜':('雨女無瓜',90126758,'yu nv wu gua'),
    '电子包浆':('電子包漿',78686522,'dian zi bao jiang'),
    '鲁蛇':('魯蛇',87969877,'lu she'),
    '麦门':('麥門',87445659,'mai men'),
    # 词条拼音写成汉字缩写或整句带逗号时，改用 dictgen annotate 注音并人工核对。
    # Where the entry abbreviates pinyin with characters or spans a comma, dictgen annotate supplies it, checked by hand.
    '了个寂寞':('了個寂寞',63016513,'le ge ji mo','annotated'),
    '中回力镖':('中回力鏢',87395370,'zhong hui li biao','annotated'),
    '智熄':('智熄',88657214,'zhi xi','annotated'),
    '忍一时越想越气':('忍一時越想越氣，退一步越想越虧',90751169,'ren yi shi yue xiang yue qi','annotated'),
    '退一步越想越亏':('忍一時越想越氣，退一步越想越虧',90751169,'tui yi bu yue xiang yue kui','annotated'),
    '听君一席话如听一席话':('聽君一席話，如聽一席話',91719321,'ting jun yi xi hua ru ting yi xi hua','annotated'),
}
# 维基百科条目与固定版本：网络用语列表，以及历年「十大网络用语」「十大流行语」。
# Wikipedia articles and pinned revisions: the slang list and the yearly top-ten internet terms and buzzwords.
WIKIPEDIA_PAGES={'list':('中国大陆网络用语列表',94713536),'hypd':('汉语盘点',93299004),'ywjz':('咬文嚼字',94531753)}
# 简体词 → (条目, 条目里的写法, 审阅过的拼音；dictgen annotate 按万象注音后人工核对)。
# Simplified word → (article, form in it, reviewed pinyin; annotated by dictgen with Wanxiang, then checked by hand).
WIKIPEDIA={
    '画美不看':('list','画美不看','hua mei bu kan'),
    '我伙惊':('list','我伙惊','wo huo jing'),
    '啊痛悟蜡':('list','啊痛悟蜡','a tong wu la'),
    '百错仍硕':('list','百错仍硕','bai cuo reng shuo'),
    '吸猫':('list','吸猫','xi mao'),
    '吸狗':('list','吸狗','xi gou'),
    '圆头耄耋':('list','圆头耄耋','yuan tou mao die'),
    '旋转猫':('list','旋转猫','xuan zhuan mao'),
    '主要看气质':('list','主要看气质','zhu yao kan qi zhi'),
    '还有这种操作':('list','还有这种操作','hai you zhe zhong cao zuo'),
    '贫穷限制了我的想象力':('list','贫穷限制了我的想象力','pin qiong xian zhi le wo de xiang xiang li'),
    '高速运转的机械进入中国':('list','高速运转的机械进入中国','gao su yun zhuan de ji xie jin ru zhong guo'),
    '爱你老己':('list','爱你老己','ai ni lao ji'),
    '我劝你善良':('list','我劝你善良','wo quan ni shan liang'),
    '误闯天家':('list','误闯天家','wu chuang tian jia'),
    '一首凉凉送给你':('list','一首涼涼送給你','yi shou liang liang song gei ni'),
    '世界是个草台班子':('list','世界是个草台班子','shi jie shi ge cao tai ban zi'),
    '低智商的善良':('list','低智商的善良','di zhi shang de shan liang'),
    '你已急哭':('list','你已急哭','ni yi ji ku'),
    '回笼漂':('list','回籠漂','hui long piao'),
    '京爷':('list','京爷','jing ye'),
    '花西币':('list','花西币','hua xi bi'),
    '力工思维':('list','力工思维','li gong si wei'),
    '山姆规则':('list','山姆规则','shan mu gui ze'),
    '躺着也中枪':('hypd','躺着也中枪','tang zhe ye zhong qiang'),
    '高端大气上档次':('hypd','高端大气上档次','gao duan da qi shang dang ci'),
    '小伙伴们都惊呆了':('hypd','小伙伴们都惊呆了','xiao huo ban men dou jing dai le'),
    '我也是醉了':('hypd','我也是醉了','wo ye shi zui le'),
    '有钱就是任性':('hypd','有钱就是任性','you qian jiu shi ren xing'),
    '挖掘机技术哪家强':('hypd','挖掘机技术哪家强','wa jue ji ji shu na jia qiang'),
    '我读书少你别骗我':('hypd','我读书少你别骗我','wo du shu shao ni bie pian wo'),
    '画面太美我不敢看':('hypd','画面太美我不敢看','hua mian tai mei wo bu gan kan'),
    '世界那么大我想去看看':('hypd','世界那么大我想去看看','shi jie na me da wo xiang qu kan kan'),
    '你们城里人真会玩儿':('hypd','你们城里人真会玩儿','ni men cheng li ren zhen hui wan er'),
    '吓死宝宝了':('hypd','吓死宝宝了','xia si bao bao le'),
    '内心几乎是崩溃的':('hypd','内心几乎是崩溃的','nei xin ji hu shi beng kui de'),
    '定个小目标':('hypd','定个小目标','ding ge xiao mu biao'),
    '你的良心不会痛吗':('hypd','你的良心不会痛吗','ni de liang xin bu hui tong ma'),
    '确认过眼神':('hypd','确认过眼神','que ren guo yan shen'),
    '好嗨哟':('hypd','好嗨哟','hao hai yo'),
    '是个狼人':('hypd','是个狼人','shi ge lang ren'),
    '伤害性不高侮辱性极强':('hypd','伤害性不高侮辱性极强','shang hai xing bu gao wu ru xing ji qiang'),
    '我看不懂但我大受震撼':('hypd','我看不懂但我大受震撼','wo kan bu dong dan wo da shou zhen han'),
    '含金量还在上升':('hypd','含金量还在上升','han jin liang hai zai shang sheng'),
    '偏偏你最争气':('hypd','偏偏你最争气','pian pian ni zui zheng qi'),
    '敬自己一杯':('hypd','敬自己一杯','jing zi ji yi bei'),
    '助我破鼎':('hypd','助我破鼎','zhu wo po ding'),
    '千百次练习只为这一刻':('hypd','千百次练习只为这一刻','qian bai ci lian xi zhi wei zhe yi ke'),
    '如何呢又能怎':('hypd','如何呢又能怎','ru he ne you neng zen'),
    '村咖':('hypd','村咖','cun ka'),
    '浪浪山小妖怪':('hypd','浪浪山小妖怪','lang lang shan xiao yao guai'),
    '我太南了':('hypd','我太南了','wo tai nan le'),
    '我不要你觉得':('ywjz','我不要你觉得','wo bu yao ni jue de'),
    '我要我觉得':('ywjz','我要我觉得','wo yao wo jue de'),
    '赛博对账':('ywjz','赛博对账','sai bo dui zhang'),
    '融梗':('ywjz','融梗','rong geng'),
    '神马都是浮云':('ywjz','神马都是浮云','shen ma dou shi fu yun'),
}
REFUSED={'derogatory','vulgar','offensive','pejorative','euphemistic','euphemism','politics','ethnic slur','slur',
    'sexual','dysphemistic','sarcastic','swear word','obscene','misogynistic','racist','homophobic'}

def get(url,params=None):
    data=urllib.parse.urlencode(params).encode() if params else None
    request=urllib.request.Request(url,data=data,headers={'User-Agent':AGENT})
    for attempt in range(4):
        try:return urllib.request.urlopen(request,timeout=60).read()
        except OSError:
            if attempt==3:raise
            time.sleep(3+attempt*3)

def fetch(cache,manifest):
    cache.mkdir(parents=True,exist_ok=True)
    for key,(_,oldid) in WIKIPEDIA_PAGES.items():
        (cache/f'wikipedia-{key}.wiki').write_bytes(get('https://zh.wikipedia.org/w/index.php?'+urllib.parse.urlencode(
            {'oldid':oldid,'action':'raw'})))
    pages={}
    revids=sorted({str(row[1]) for row in WIKTIONARY.values()})
    for i in range(0,len(revids),50):
        reply=json.loads(get('https://en.wiktionary.org/w/api.php',{'action':'query','prop':'revisions','rvprop':'ids|content',
            'rvslots':'main','revids':'|'.join(revids[i:i+50]),'format':'json','formatversion':'2'}))
        for page in reply['query']['pages']:
            for rev in page['revisions']:
                pages[page['title']]={'revid':rev['revid'],'text':rev['slots']['main']['content']}
    (cache/'wiktionary-slang.json').write_text(json.dumps(pages,ensure_ascii=False,sort_keys=True,indent=0)+'\n',encoding='utf-8')

def toneless(value):
    value=unicodedata.normalize('NFD',value.lower()).replace('u\u0308','v').replace('u:','v')
    return ''.join(c for c in value if not unicodedata.combining(c))

def chinese_section(text):
    start=text.find('==Chinese==')
    if start<0:return ''
    end=re.search(r'\n==[^=]',text[start+3:])
    return text[start:start+3+end.start()] if end else text[start:]

def wiktionary_rows(pages):
    for word,(title,revid,reviewed,*annotated) in WIKTIONARY.items():
        page=pages[title]
        assert page['revid']==revid,f'{title}: revision {page["revid"]} != {revid}'
        section=chinese_section(page['text'])
        labels={l.strip() for m in re.findall(r'\{\{(?:lb|lbl|label)\|zh\|([^}]*)\}\}',section) for l in m.split('|')}
        assert not labels&REFUSED,f'{title}: labelled {labels&REFUSED}'
        if annotated:
            forms=re.search(r'\{\{zh-forms[^}]*\|s=([^|}\n]+)',section)
            assert word in re.sub(r'[，,]','',forms.group(1) if forms else title),f'{title}: {word} not in the entry'
            yield word,reviewed
            continue
        pron=re.search(r'\{\{zh-pron[^}]*?\|m=([^|}\n]*)',section,re.S)
        assert pron,f'{title}: no Mandarin pronunciation'
        letters=re.sub(r'[^a-z]','',toneless(pron.group(1).split(',')[0]))
        assert letters==reviewed.replace(' ',''),f'{title}: pinyin {letters} != {reviewed}'
        yield word,reviewed

def wikipedia_rows(texts):
    # 去掉链接、繁简标记和标点再找，「世界那么大，我想去看看」也能对上。
    # Search without link markup, conversion marks and punctuation so comma-split phrases still match.
    plain={key:re.sub(r'[\s，,、“”"]','',re.sub(r'-\{(.*?)\}-',r'\1',re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',text)))
        for key,text in texts.items()}
    for word,(page,form,reviewed) in WIKIPEDIA.items():
        assert form in plain[page],f'{form}: not in the pinned {WIKIPEDIA_PAGES[page][0]}'
        yield word,reviewed

def main():
    manifest=json.loads((ROOT/'sources.json').read_text())
    if sys.argv[1]=='--fetch':
        fetch(Path(sys.argv[2]),manifest);return
    cache=Path(sys.argv[1])
    sources={s['id']:s for s in manifest['sources']}
    for source in ('wiktionary-slang','wikipedia-slang'):
        for name,digest in sources[source]['sha256'].items():
            assert hashlib.sha256((cache/name).read_bytes()).hexdigest()==digest,f'upstream hash: {name}'
    # 手工词表已有的词不重复导入。 Skip words the hand-curated lists already carry.
    taken={line.split('\t')[0] for path in (ROOT/'words').glob('*.tsv') if not path.name.startswith('imported-')
        for line in path.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    pages=json.loads((cache/'wiktionary-slang.json').read_text(encoding='utf-8'))
    batches=[('wiktionary-slang',wiktionary_rows(pages)),
        ('wikipedia-slang',wikipedia_rows({key:(cache/f'wikipedia-{key}.wiki').read_text(encoding='utf-8') for key in WIKIPEDIA_PAGES}))]
    for source,rows in batches:
        kept=[]
        for word,py in rows:
            if word in taken:continue
            taken.add(word);kept.append((word,py))
        output=f'# source: {source}; CC BY-SA 4.0, see sources.json and SOURCES.md\n'+''.join(
            f'{w}\t{py}\t200\t{ADDED}\t\t{source}\n' for w,py in sorted(kept))
        (ROOT/f'words/imported-{source}.tsv').write_text(output,encoding='utf-8')
        print(source,len(kept),hashlib.sha256(output.encode()).hexdigest())

if __name__=='__main__':main()
