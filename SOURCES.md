# 词库来源与许可

这是织文主动下载的公共补充词表，不收集个人输入，也不向上游查询每次按键。当前包含自主整理的词与网络热梗、万象的通用补充、THUOCL 的 IT 术语，维基词典、维基百科收录的网络用语、年度时政文化词、谚语歇后语和成语，以及 chinese-poetry 的诗词名句。

| 数据 | 来源与固定版本 | 许可 | 本次处理 |
|---|---|---|---|
| 原有示例与 `words/2026-10.tsv` | WeaveText contributors 独立整理 | CC0-1.0 | 公开常见术语，人工注音 |
| `words/2026-10-memes.tsv` | WeaveText contributors 独立整理的网络热梗 | CC0-1.0 | 只收常见说法，人工核对拼音；不收侮辱、低俗、政治与针对真人的梗 |
| `words/imported-wiktionary-slang.tsv` | [英文维基词典 Category:Chinese internet slang](https://en.wiktionary.org/wiki/Category:Chinese_internet_slang)，每个词条的固定版本号见 `tools/import_wiki.py` | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt) | 人工审阅白名单；带粗俗、贬义、冒犯等标签的词条拒收；繁体词条转简体，拼音取自词条的普通话读音并去声调（词条拼音不完整的几条改用 `dictgen annotate` 注音后人工核对）；去掉内置词库和手工词表已有的词 |
| `words/imported-wikipedia-slang.tsv` | 中文维基百科「[中国大陆网络用语列表](https://zh.wikipedia.org/w/index.php?oldid=94713536)」「[汉语盘点](https://zh.wikipedia.org/w/index.php?oldid=93299004)」「[咬文嚼字](https://zh.wikipedia.org/w/index.php?oldid=94531753)」的固定版本 | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt)；注音所用万象数据为 CC-BY-4.0 | 人工审阅白名单：列表只取日常用语类章节，另两篇只取历年「十大网络用语」「十大流行语」里的网络用语；用 `dictgen annotate` 按万象注音后人工核对；去掉已有的词 |
| `words/imported-wikipedia-news.tsv` | 中文维基百科「[汉语盘点](https://zh.wikipedia.org/w/index.php?oldid=93299004)」「[咬文嚼字](https://zh.wikipedia.org/w/index.php?oldid=94531753)」的固定版本 | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt)；注音所用万象数据为 CC-BY-4.0 | 人工审阅白名单：历年十大新词语、流行语里的官方提法和时政、科技、文体用词，只收中性说法；`dictgen annotate` 注音后人工核对 |
| `words/imported-wiktionary-idioms.tsv` | 英文维基词典 [Chinese proverbs](https://en.wiktionary.org/wiki/Category:Chinese_proverbs)、[xiehouyu](https://en.wiktionary.org/wiki/Category:Chinese_xiehouyu)、[chengyu](https://en.wiktionary.org/wiki/Category:Chinese_chengyu)、[idioms](https://en.wiktionary.org/wiki/Category:Chinese_idioms) 分类，每个词条的固定版本见 `tools/wiktionary-idioms.tsv` | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt) | 人工审阅白名单；带粗俗、贬义、冒犯、仅限方言、废弃等标签的词条和异体写法拒收；繁体用 OpenCC 转简体，拼音取自词条（还原「一」「不」的变调简写）并去声调；去掉已有的词 |
| `words/imported-poetry.tsv` | [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry/tree/b8594f81a89752241442f2ce267d6f66f96704ee)：《增广贤文》《朱子家训》《千家诗》《唐诗三百首》《宋词三百首》 | [MIT](LICENSES/chinese-poetry-MIT.txt)（古籍原文为公有领域）；注音所用万象数据为 CC-BY-4.0 | OpenCC 繁转简，按标点切成 4–9 字的句子，只留 GB2312 常用字，去掉内置已有；`dictgen annotate` 注音，多音字可能少量误读，权重很低 |
| `words/imported-wanxiang-new.tsv` | [amzxyz/rime-wanxiang](https://github.com/amzxyz/rime-wanxiang/tree/908108a09121aaf7ba2cad1fcfbe71b427ea9090)，`dicts/jichu.dict.yaml` | [CC-BY-4.0](LICENSES/CC-BY-4.0.txt) | 去声调、ü 写 v，排除内置词库已有词、过滤非中文与无效音节，保留新增且有一定频率的词，压低权重 |
| `words/imported-thuocl-it.tsv` | [THUNLP / THUOCL](https://github.com/thunlp/THUOCL/tree/a30ce79d895d01ab5132a5c74c29703ff7efb4cc)，`data/THUOCL_IT.txt`；Copyright © 2018 THUNLP | [MIT](LICENSES/THUOCL-MIT.txt)；补充注音所用万象数据保留 CC-BY-4.0 | 用织文 `dictgen annotate` 按内置万象词表最长匹配注音；去声调，过滤非中文、未能注音的词和已内置词，选取 1200 项并降低权重 |

万象署名：本词表部分来自 amzxyz 及 rime-wanxiang 贡献者维护的万象拼音词库，依 CC BY 4.0 授权使用，已做筛选、去重、注音格式转换和权重调整。THUOCL 署名：使用清华大学开放中文词库，原始 MIT 版权及许可声明保留于上方文件。

维基署名：网络用语来自英文维基词典与中文维基百科的贡献者，依 CC BY-SA 4.0 授权使用，已做筛选、繁简转换、拼音格式转换和去重；这两份导入词表本身继续以 CC BY-SA 4.0 提供，合并发布文件只是把它们与其他数据放在一起，并不改变其他部分的许可。

导入数据保留自己的许可证；**CC0 只覆盖自主整理的数据，不能理解为第三方数据也被改成 CC0**。合并发布文件在注释头中携带本页、项目、许可链接、修改说明，以及 THUOCL 的 MIT 声明。客户端保存验签过的原始文本，并提供“词库来源与许可”入口。

## 可复现

`sources.json` 记录来源提交、下载文件 SHA-256、基线词表 SHA-256、注音结果摘要和生成参数。基线是织文内置万象词库提交 `516b1bb66bdce1fd5785f5481c415f13ff736548` 的八个基础词表。

1. 从固定提交下载所列文件及许可证，核对 SHA-256。
2. 使用织文仓库 `fcb3167` 的 `weave-dict` 命令：`dictgen annotate thu-it-annotated.yaml THUOCL_IT.txt <八个基线词表>`。
3. 把注音结果和原始数据放进缓存目录，执行 `python3 tools/import_sources.py <基线 dicts 目录> <缓存目录>`。脚本先验摘要，再生成同样的两份导入 TSV。
4. 执行 `python3 tools/build.py --check`；签名发布仍由 GitHub Action 的维护者密钥完成，不改变客户端公钥。

诗词用 `tools/import_poetry.py` 三步生成：`--fetch` 下载、`--candidates` 繁转简切句、`dictgen annotate` 注音，最后核对摘要写出词表，步骤写在脚本开头。

维基来源用 `python3 tools/import_wiki.py --fetch <缓存目录>` 按固定版本下载，再执行 `python3 tools/import_wiki.py <缓存目录>`：脚本核对摘要、标签和审阅过的拼音，生成两份导入词表。

上游更新需要先核对许可、修改固定版本和摘要，再人工审阅导入差异。不会在每日签名任务中自动抓取未经核对的最新词库。
