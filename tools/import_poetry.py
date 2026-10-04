#!/usr/bin/env python3
"""从 chinese-poetry 固定版本导入诗词名句与蒙学格言（MIT）。
Import classic poetry lines and maxims from a pinned chinese-poetry revision (MIT).

用法 / Usage:
  python3 tools/import_poetry.py --fetch CACHE                    # 下载固定版本 / download the pinned files
  python3 tools/import_poetry.py --candidates CACHE BASELINE_DICTS  # 繁转简、切句、去掉内置已有，写 CACHE/poetry-candidates.txt
                                                                  # (needs `pip install opencc==1.4.2`)
  dictgen annotate CACHE/poetry-annotated.yaml CACHE/poetry-candidates.txt <sources.json 里的八个基线词表>
  python3 tools/import_poetry.py CACHE                            # 核对摘要，写 words/imported-poetry.tsv

取《增广贤文》《朱子家训》《千家诗》《唐诗三百首》《宋词三百首》，按标点切成 4–9 字的句子，只留 GB2312 常用字；
注音用织文 dictgen annotate（按万象词库最长匹配，CC BY 4.0），多音字可能有少量误读，所以权重放得很低。
Takes 增广贤文, 朱子家训, 千家诗, 唐诗三百首 and 宋词三百首, cut at punctuation into 4–9 character lines in GB2312
characters only. Pinyin comes from WeaveText's dictgen annotate (longest match over Wanxiang, CC BY 4.0); a few
polyphones may be misread, so the weight stays low.
"""
import hashlib,json,re,sys,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ADDED='2026-10-03'
WEIGHT=80
REVISION='b8594f81a89752241442f2ce267d6f66f96704ee'
FILES=['蒙学/zengguangxianwen.json','蒙学/zhuzijiaxun.json','蒙学/qianjiashi.json','全唐诗/唐诗三百首.json','宋词/宋词三百首.json']

def lines(path):
    def strings(node,inside=False):
        if isinstance(node,str):
            if inside:yield node
        elif isinstance(node,dict):
            for key,value in node.items():yield from strings(value,key=='paragraphs')
        elif isinstance(node,list):
            for value in node:yield from strings(value,inside)
    yield from strings(json.loads(path.read_text(encoding='utf-8')))

def common(text):
    try:text.encode('gb2312');return all('一'<=c<='鿿' for c in text)
    except UnicodeEncodeError:return False

def main():
    manifest={s['id']:s for s in json.loads((ROOT/'sources.json').read_text())['sources']}
    if sys.argv[1]=='--fetch':
        cache=Path(sys.argv[2]);cache.mkdir(parents=True,exist_ok=True)
        for name in FILES:
            url=f'https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/{REVISION}/'+urllib.parse.quote(name)
            (cache/Path(name).name).write_bytes(urllib.request.urlopen(url,timeout=120).read())
        return
    cache=Path(sys.argv[2] if sys.argv[1]=='--candidates' else sys.argv[1])
    source=manifest['poetry']
    for name,digest in source['sha256'].items():
        if name=='poetry-annotated.yaml' and sys.argv[1]=='--candidates':continue
        assert hashlib.sha256((cache/name).read_bytes()).hexdigest()==digest,f'hash: {name}'
    if sys.argv[1]=='--candidates':
        import opencc
        convert=opencc.OpenCC('t2s').convert
        baseline=Path(sys.argv[3])
        known={line.split('\t')[0] for name in json.loads((ROOT/'sources.json').read_text())['baseline']['sha256']
            for line in (baseline/name).read_text(encoding='utf-8').splitlines() if '\t' in line}
        found=[]
        for name in FILES:
            for line in lines(cache/Path(name).name):
                for clause in re.split(r'[，。！？；：、“”‘’「」『』（）《》\s]+',convert(line)):
                    if 4<=len(clause)<=9 and common(clause) and clause not in known:found.append(clause)
        (cache/'poetry-candidates.txt').write_text(''.join(f'{w}\t1\n' for w in dict.fromkeys(found)),encoding='utf-8')
        return
    # 其他词表已有的词不重复导入。 Skip words any other list already carries.
    taken={line.split('\t')[0] for path in (ROOT/'words').glob('*.tsv') if path.name!='imported-poetry.tsv'
        for line in path.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    rows=[]
    for line in (cache/'poetry-annotated.yaml').read_text(encoding='utf-8').splitlines():
        fields=line.split('\t')
        if len(fields)<2 or line.startswith('#') or fields[0] in taken:continue
        taken.add(fields[0]);rows.append((fields[0],fields[1]))
    output='# source: poetry; MIT (chinese-poetry), pinyin CC BY 4.0 (Wanxiang); see sources.json and SOURCES.md\n'+''.join(
        f'{w}\t{py}\t{WEIGHT}\t{ADDED}\t\tpoetry\n' for w,py in sorted(rows))
    (ROOT/'words/imported-poetry.tsv').write_text(output,encoding='utf-8')
    print('poetry',len(rows),hashlib.sha256(output.encode()).hexdigest())

if __name__=='__main__':main()
