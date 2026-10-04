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
}
# 简体词 → (条目里的写法, 审阅过的拼音；dictgen annotate 按万象注音后人工核对)。
# Simplified word → (form in the article, reviewed pinyin; annotated by dictgen with Wanxiang, then checked by hand).
WIKIPEDIA={
    '画美不看':('画美不看','hua mei bu kan'),
    '我伙惊':('我伙惊','wo huo jing'),
    '啊痛悟蜡':('啊痛悟蜡','a tong wu la'),
    '百错仍硕':('百错仍硕','bai cuo reng shuo'),
    '吸猫':('吸猫','xi mao'),
    '吸狗':('吸狗','xi gou'),
    '圆头耄耋':('圆头耄耋','yuan tou mao die'),
    '旋转猫':('旋转猫','xuan zhuan mao'),
    '主要看气质':('主要看气质','zhu yao kan qi zhi'),
    '还有这种操作':('还有这种操作','hai you zhe zhong cao zuo'),
    '贫穷限制了我的想象力':('贫穷限制了我的想象力','pin qiong xian zhi le wo de xiang xiang li'),
    '高速运转的机械进入中国':('高速运转的机械进入中国','gao su yun zhuan de ji xie jin ru zhong guo'),
    '爱你老己':('爱你老己','ai ni lao ji'),
    '我劝你善良':('我劝你善良','wo quan ni shan liang'),
    '误闯天家':('误闯天家','wu chuang tian jia'),
    '一首凉凉送给你':('一首涼涼送給你','yi shou liang liang song gei ni'),
    '世界是个草台班子':('世界是个草台班子','shi jie shi ge cao tai ban zi'),
    '低智商的善良':('低智商的善良','di zhi shang de shan liang'),
    '你已急哭':('你已急哭','ni yi ji ku'),
    '回笼漂':('回籠漂','hui long piao'),
    '京爷':('京爷','jing ye'),
    '花西币':('花西币','hua xi bi'),
    '力工思维':('力工思维','li gong si wei'),
    '山姆规则':('山姆规则','shan mu gui ze'),
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
    wiki=next(s for s in manifest['sources'] if s['id']=='wikipedia-slang')
    (cache/'wikipedia-slang.wiki').write_bytes(get('https://zh.wikipedia.org/w/index.php?'+urllib.parse.urlencode(
        {'oldid':wiki['revision'],'action':'raw'})))
    pages={}
    revids=[str(rev) for _,rev,_ in WIKTIONARY.values()]
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
    for word,(title,revid,reviewed) in WIKTIONARY.items():
        page=pages[title]
        assert page['revid']==revid,f'{title}: revision {page["revid"]} != {revid}'
        section=chinese_section(page['text'])
        labels={l.strip() for m in re.findall(r'\{\{(?:lb|lbl|label)\|zh\|([^}]*)\}\}',section) for l in m.split('|')}
        assert not labels&REFUSED,f'{title}: labelled {labels&REFUSED}'
        pron=re.search(r'\{\{zh-pron[^}]*?\|m=([^|}\n]*)',section,re.S)
        assert pron,f'{title}: no Mandarin pronunciation'
        letters=re.sub(r'[^a-z]','',toneless(pron.group(1).split(',')[0]))
        assert letters==reviewed.replace(' ',''),f'{title}: pinyin {letters} != {reviewed}'
        yield word,reviewed

def wikipedia_rows(text):
    plain=re.sub(r'-\{(.*?)\}-',r'\1',re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',text))
    for word,(form,reviewed) in WIKIPEDIA.items():
        assert form in plain,f'{form}: not in the pinned article'
        yield word,reviewed

def main():
    manifest=json.loads((ROOT/'sources.json').read_text())
    if sys.argv[1]=='--fetch':
        fetch(Path(sys.argv[2]),manifest);return
    cache=Path(sys.argv[1])
    sources={s['id']:s for s in manifest['sources']}
    for name,source in [('wiktionary-slang.json','wiktionary-slang'),('wikipedia-slang.wiki','wikipedia-slang')]:
        assert hashlib.sha256((cache/name).read_bytes()).hexdigest()==sources[source]['sha256'],f'upstream hash: {name}'
    # 手工词表已有的词不重复导入。 Skip words the hand-curated lists already carry.
    taken={line.split('\t')[0] for path in (ROOT/'words').glob('*.tsv') if not path.name.startswith('imported-')
        for line in path.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    pages=json.loads((cache/'wiktionary-slang.json').read_text(encoding='utf-8'))
    batches=[('wiktionary-slang',wiktionary_rows(pages)),
        ('wikipedia-slang',wikipedia_rows((cache/'wikipedia-slang.wiki').read_text(encoding='utf-8')))]
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
