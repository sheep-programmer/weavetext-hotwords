#!/usr/bin/env python3
"""
织文热词：校验 words/*.tsv，合并去重、去掉过期词，生成 dist/hotwords.tsv，并用 Ed25519 签名。
WeaveText hot words: validate words/*.tsv, merge, dedupe, drop expired rows, write dist/hotwords.tsv and sign it.

用法 / Usage:
  python3 tools/build.py --check          # 只校验（PR 用） / validate only (for pull requests)
  HOTWORDS_SIGNING_KEY=<base64> python3 tools/build.py   # 生成并签名 / build and sign

行格式 / Row format (TAB separated):
  词  拼音(空格分隔，无声调，ü 写 v)  权重 1-1000  加入日期 YYYY-MM-DD  到期日期 YYYY-MM-DD(可空)  备注(可空)
"""
import base64
import datetime as dt
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYLLABLES = set((ROOT / "tools" / "syllables.txt").read_text().split())
MAX_ROWS = 50_000


def parse_date(s):
    return dt.date.fromisoformat(s) if s else None


def load(errors):
    rows = {}
    for f in sorted((ROOT / "words").glob("*.tsv")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            where = f"{f.name}:{n}"
            cols = line.split("\t")
            if len(cols) < 4:
                errors.append(f"{where}: 至少需要 词、拼音、权重、加入日期 四列 / need 4 columns")
                continue
            word, py, w, added = (c.strip() for c in cols[:4])
            expires = cols[4].strip() if len(cols) > 4 else ""
            if not word or any(c.isspace() for c in word) or len(word) > 20:
                errors.append(f"{where}: 词为空、含空白或超过 20 字 / bad word")
                continue
            syls = py.split()
            bad = [s for s in syls if s not in SYLLABLES]
            if not syls or bad:
                errors.append(f"{where}: 拼音不合法 / invalid pinyin: {' '.join(bad) or py}")
                continue
            try:
                weight = int(w)
                assert 1 <= weight <= 1000
            except (ValueError, AssertionError):
                errors.append(f"{where}: 权重应为 1-1000 的整数 / weight must be 1-1000")
                continue
            try:
                a, e = parse_date(added), parse_date(expires)
                if a is None:
                    raise ValueError
            except ValueError:
                errors.append(f"{where}: 日期格式应为 YYYY-MM-DD / dates must be YYYY-MM-DD")
                continue
            if e and e < a:
                errors.append(f"{where}: 到期早于加入 / expiry before added")
                continue
            key = (word, " ".join(syls))
            if key in rows:
                errors.append(f"{where}: 与 {rows[key]['where']} 重复 / duplicate")
                continue
            rows[key] = {"word": word, "py": " ".join(syls), "w": weight, "exp": expires, "where": where}
    return rows


def main():
    check = "--check" in sys.argv
    errors = []
    rows = load(errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    today = dt.datetime.now(dt.timezone.utc).date()
    live = [r for r in rows.values() if not r["exp"] or parse_date(r["exp"]) >= today]
    live.sort(key=lambda r: (-r["w"], r["word"]))
    if len(live) > MAX_ROWS:
        print(f"超过 {MAX_ROWS} 条 / more than {MAX_ROWS} rows", file=sys.stderr)
        sys.exit(1)
    print(f"{len(rows)} rows, {len(live)} live, {len(rows) - len(live)} expired")
    if check:
        return
    version = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H")
    lines = ["#! weavetext-hotwords 1", f"#! version {version}"]
    lines += [f"{r['word']}\t{r['py']}\t{r['w']}\t{r['exp']}" for r in live]
    data = ("\n".join(lines) + "\n").encode("utf-8")
    key = os.environ.get("HOTWORDS_SIGNING_KEY", "").strip()
    if not key:
        print("缺少 HOTWORDS_SIGNING_KEY / missing HOTWORDS_SIGNING_KEY", file=sys.stderr)
        sys.exit(2)
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    sk = Ed25519PrivateKey.from_private_bytes(base64.b64decode(key))
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "hotwords.tsv").write_bytes(data)
    (dist / "hotwords.tsv.sig").write_text(sk.sign(data).hex() + "\n")
    print(f"wrote dist/hotwords.tsv (version {version}, {len(data)} bytes) and its signature")


if __name__ == "__main__":
    main()
