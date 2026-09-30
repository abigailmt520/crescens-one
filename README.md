# crescens-one

人牌 crescens.one 的标识件（`brand/`）与域名一页站（`site/`，由 `tools/build_site.py` 生成，不手改）。规则见 `CLAUDE.md`。

- 一页站去处的条目类型有两种，都写在 `tools/site_links.json`：**链接**条目有 `url`，页面显示为可点的名字；**文本**条目不写 `url`、写 `"text": true`，页面只列名字不带链接（PG-003 补丁9 §1②，2026-09-29）。
