#!/usr/bin/env python3
"""Reproduce licensed supplements from pinned source files and dictgen's annotated IT list.
Usage: python3 tools/import_sources.py BASELINE_DICTS SOURCE_CACHE
SOURCE_CACHE holds wx-jichu.yaml, THUOCL_IT.txt and thu-it-annotated.yaml.
Before annotation verify upstream revision/hash in sources.json; run WeaveText dictgen annotate
with the eight baseline files listed there. No mutable upstream content is silently accepted.
"""
import collections,hashlib,json,math,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SYLLABLES=set((ROOT/'tools/syllables.txt').read_text().split())
def normalize(value):
    value=value.lower().translate(str.maketrans({c:'v' for c in 'üǖǘǚǜ'}))
    return ''.join(c for c in unicodedata.normalize('NFD',value) if not unicodedata.combining(c))
def rows(path):
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):continue
        fields=line.split('\t')
        if len(fields)<3:continue
        word=fields[0].strip();py=normalize(fields[1]);parts=py.split()
        if not 2<=len(word)<=10 or not all('\u3400'<=c<='\u9fff' for c in word):continue
        if len(parts)!=len(word) or any(p not in SYLLABLES for p in parts):continue
        try:frequency=int(fields[2])
        except ValueError:continue
        yield word,' '.join(parts),frequency
def main():
    baseline,cache=map(Path,sys.argv[1:])
    manifest=json.loads((ROOT/'sources.json').read_text())
    for item in manifest['sources']:
        name='wx-jichu.yaml' if item['id']=='wanxiang-new' else 'THUOCL_IT.txt'
        assert hashlib.sha256((cache/name).read_bytes()).hexdigest()==item['sha256'],f'upstream hash: {name}'
    for name,digest in manifest['baseline']['sha256'].items():
        assert hashlib.sha256((baseline/name).read_bytes()).hexdigest()==digest,f'baseline hash: {name}'
    assert hashlib.sha256((cache/'thu-it-annotated.yaml').read_bytes()).hexdigest()==manifest['annotation_sha256'],'annotation differs'
    base={word for name in manifest['baseline']['sha256'] for word,py,f in rows(baseline/name)}
    seen=set(base);imported=[]
    for word,py,f in sorted(rows(cache/'thu-it-annotated.yaml'),key=lambda r:(-r[2],r[0])):
        if word in seen:continue
        seen.add(word);imported.append((word,py,min(300,max(80,f//3)),'thuocl-it'))
        if len(imported)>=1200:break
    for word,py,f in sorted(rows(cache/'wx-jichu.yaml'),key=lambda r:(-r[2],r[0])):
        if word in seen or f<100:continue
        seen.add(word);imported.append((word,py,min(300,max(80,int(30*math.log2(f+1)))),'wanxiang-new'))
    for item in manifest['sources']:
        source=item['id'];selected=sorted((r for r in imported if r[3]==source),key=lambda r:(-r[2],r[0]))
        output=f'# source: {source}; see sources.json and SOURCES.md\n'+''.join(f'{w}\t{py}\t{weight}\t2026-10-02\t\t{source}\n' for w,py,weight,_ in selected)
        path=ROOT/f'words/imported-{source}.tsv'
        path.write_text(output,encoding='utf-8')
        print(source,len(selected),hashlib.sha256(output.encode()).hexdigest())
if __name__=='__main__':main()
