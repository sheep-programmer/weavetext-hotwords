# 织文热词 · WeaveText hot words

织文输入法「云端热词」的数据仓库：维护者在这里收录新词、热词，客户端（默认关闭）每天最多下载一次。

- **只下载，不上传**：客户端只读取这里发布的文件，你打的字不会离开设备。
- **可验证**：发布文件用 Ed25519 签名，客户端内置公钥，签名不对就不用。
- **会过期**：每个词可以带到期日，过期后自动从发布文件里消失。
- **不抢位**：热词与系统词库同尺度计分并整体靠后，只在你打出对应拼音时出现在候选里。

## 添加词语

在 `words/` 下按月份的文件（如 `2026-09.tsv`）里加一行，用 TAB 分隔：

```
词	拼音（空格分隔，无声调，ü 写 v）	权重 1-1000	加入日期	到期日期（可空）	备注（可空）
```

权重建议：刚出现的新词 100–300，广泛流行的 300–600，只有极常用、确定不会过时的才超过 600。
提交 PR 后会自动校验拼音、日期与重复。

## 发布

合并到 `main`（以及每天定时）时，GitHub Action 运行 `tools/build.py`：合并全部词表、去掉过期词、签名，
推送到 `dist` 分支。客户端读取：

```
https://raw.githubusercontent.com/<owner>/weavetext-hotwords/dist/hotwords.tsv
https://raw.githubusercontent.com/<owner>/weavetext-hotwords/dist/hotwords.tsv.sig
```

签名私钥放在仓库 Secret `HOTWORDS_SIGNING_KEY`（32 字节原始私钥的 base64）。换钥需要同时更新客户端内置的公钥。

## 许可

自主整理的数据（含网络热梗）以 CC0 1.0 发布。导入的万象数据保留 CC BY 4.0，THUOCL 保留 MIT，维基词典与维基百科的网络用语、时政文化词和俗语成语保留 CC BY-SA 4.0，chinese-poetry 的诗词保留 MIT，注音派生数据保留万象的 CC BY 4.0；来源、固定版本、转换说明和许可证见 [SOURCES.md](SOURCES.md)。发布文件注释头携带署名与 MIT 声明，不能把整个合并词表理解为 CC0。收录时只加入公开常见的词语。

---

# WeaveText hot words (English)

Data for the optional "cloud hot words" feature of WeaveText (off by default). Clients download at most once a
day; nothing typed is ever uploaded. The published file is signed with Ed25519 (the public key is built into the
clients), words may carry an expiry date, and they are scored behind the system dictionary so they never take
over common words.

Add a TAB-separated row to a monthly file under `words/` (word, toneless pinyin with spaces and `v` for `ü`,
weight 1–1000, date added, optional expiry, optional note) and open a pull request; CI validates it. Merges to
`main` and a daily run build, sign and push `dist/hotwords.tsv` + `.sig` to the `dist` branch. The signing key lives
in the `HOTWORDS_SIGNING_KEY` secret (base64 of the raw 32-byte private key). Independently curated terms (internet memes included) are CC0 1.0. Imported Wanxiang data remain CC BY 4.0, THUOCL data retain MIT, slang, current-affairs terms, proverbs and idioms from Wiktionary and Wikipedia stay CC BY-SA 4.0, and chinese-poetry lines keep MIT; annotation uses Wanxiang CC BY 4.0 data. See SOURCES.md and NOTICE for attribution, pinned revisions and transformations. The merged file is not wholly CC0.
