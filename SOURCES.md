# 词库来源与许可

这是织文主动下载的公共补充词表，不收集个人输入，也不向上游查询每次按键。当前包含自主整理的词、万象的通用补充和 THUOCL 的 IT 术语。专业术语不等于新闻热榜。

| 数据 | 来源与固定版本 | 许可 | 本次处理 |
|---|---|---|---|
| 原有示例与 `words/2026-10.tsv` | WeaveText contributors 独立整理 | CC0-1.0 | 公开常见术语，人工注音 |
| `words/imported-wanxiang-new.tsv` | [amzxyz/rime-wanxiang](https://github.com/amzxyz/rime-wanxiang/tree/908108a09121aaf7ba2cad1fcfbe71b427ea9090)，`dicts/jichu.dict.yaml` | [CC-BY-4.0](LICENSES/CC-BY-4.0.txt) | 去声调、ü 写 v，排除内置词库已有词、过滤非中文与无效音节，保留新增且有一定频率的词，压低权重 |
| `words/imported-thuocl-it.tsv` | [THUNLP / THUOCL](https://github.com/thunlp/THUOCL/tree/a30ce79d895d01ab5132a5c74c29703ff7efb4cc)，`data/THUOCL_IT.txt`；Copyright © 2018 THUNLP | [MIT](LICENSES/THUOCL-MIT.txt)；补充注音所用万象数据保留 CC-BY-4.0 | 用织文 `dictgen annotate` 按内置万象词表最长匹配注音；去声调，过滤非中文、未能注音的词和已内置词，选取 1200 项并降低权重 |

万象署名：本词表部分来自 amzxyz 及 rime-wanxiang 贡献者维护的万象拼音词库，依 CC BY 4.0 授权使用，已做筛选、去重、注音格式转换和权重调整。THUOCL 署名：使用清华大学开放中文词库，原始 MIT 版权及许可声明保留于上方文件。

导入数据保留自己的许可证；**CC0 只覆盖自主整理的数据，不能理解为第三方数据也被改成 CC0**。合并发布文件在注释头中携带本页、项目、许可链接、修改说明，以及 THUOCL 的 MIT 声明。客户端保存验签过的原始文本，并提供“词库来源与许可”入口。

## 可复现

`sources.json` 记录来源提交、下载文件 SHA-256、基线词表 SHA-256、注音结果摘要和生成参数。基线是织文内置万象词库提交 `516b1bb66bdce1fd5785f5481c415f13ff736548` 的八个基础词表。

1. 从固定提交下载所列文件及许可证，核对 SHA-256。
2. 使用织文仓库 `fcb3167` 的 `weave-dict` 命令：`dictgen annotate thu-it-annotated.yaml THUOCL_IT.txt <八个基线词表>`。
3. 把注音结果和原始数据放进缓存目录，执行 `python3 tools/import_sources.py <基线 dicts 目录> <缓存目录>`。脚本先验摘要，再生成同样的两份导入 TSV。
4. 执行 `python3 tools/build.py --check`；签名发布仍由 GitHub Action 的维护者密钥完成，不改变客户端公钥。

上游更新需要先核对许可、修改固定版本和摘要，再人工审阅导入差异。不会在每日签名任务中自动抓取未经核对的最新词库。
