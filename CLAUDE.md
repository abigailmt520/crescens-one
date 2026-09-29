# CLAUDE.md — STUDIO 线（crescens-one）开场说明

## ① 本仓属哪条线与航道
- **STUDIO 线，航道 A**。本仓是主理人的人牌 crescens.one：标识件（`brand/`）与域名一页站（`site/`）。不是新线，挂在 STUDIO 线下（STUDIO-002）。
- 与「物理AI实验场」是两个牌子：那边是产品牌（proving-ground 仓），这边是人牌。只共用生成器。

## ② 编号与回报
- 令号前缀 **STUDIO-###**。执行摘要末尾注明「本轮执行：STUDIO-0XX」。本仓不发号，INDEX 真源在 dream-os `00_portfolio/index/STUDIO-INDEX.md`。

## ③ 真源与纪律（以仓内既有文件为准）
- 真源：本机 `lines/crescens-one`（全路径见 dream-os 护照 STUDIO）；远端：GitHub（地址唯一居所＝dream-os 护照 STUDIO 锚点节）。
- **公开仓**（2026-09-29 主理人拍板公开，STUDIO-002 补丁1）。入仓的每个文件都是对外可见的：不写人名、不写完整邮箱地址、不写本机路径。
- `brand/` 是随包送来的原件，除 STUDIO-002 补丁1 点名的几处外**不改**；规格与使用规则见 `brand/crescens-spec.md`。要改图，改生成器后整批重出，不手改成品。
- `site/index.html` 由 `tools/build_site.py` 生成，**不手改**；字标与两行字取自横幅 svg 的轮廓，不手打字；两声文案只取 `brand/build/crescens.py` 的 `TAGLINE`。
- 页面不出现公司、工作、服务、合作类字眼；不放统计脚本；不引外部字体与脚本（STUDIO-002 §3）。
- **仓内不出现完整邮箱地址**：用户名与域名分开存，页面脚本运行时拼接（STUDIO-002 修订1）。
- 不存账号密码、密钥；推送只走 `bash tools/push_gate.sh`。

## ④ INDEX 与会话卫生
- **会话卫生四条**（dream-os ONE-014，DEC-20260916-14）：一令一会话｜跨日必切｜上下文超阈值（建议 150k token）即交接新开，交接件只写已完成步骤号＋下一步｜禁多令续跑。
- INDEX：dream-os `00_portfolio/index/STUDIO-INDEX.md`；护照：`00_portfolio/passports/STUDIO.md`。

## 协作提示词落地件（LAB-005，源＝手册 T25／T32；勿手改，改源在手册后重新发放）

> **钩子管硬红线，本段管灰区。** `.claude/hooks/` 的护栏拦的是冻结物/密钥这类**明确禁止**；
> 下面两段管的是**规则没写死、要靠判断**的那一片——可逆性、爆炸半径、默认动不动。

```text
Weigh reversibility and blast radius before acting. Local, reversible steps — editing files, running tests — are yours to take. Ask first for anything hard to undo, visible to others, or destructive: deleting files or branches, dropping tables, rm -rf, force pushes, hard resets, amending published commits, pushing code, commenting on PRs or issues, sending messages, changing shared infrastructure. Never take a destructive shortcut around an obstacle: no bypassing safety checks (--no-verify), no discarding unfamiliar files that may be someone's in-progress work.
```

```text
<default_to_action>
By default, make the change rather than only suggesting it. If the intent is unclear, infer the most useful action and proceed, using tools to discover missing details instead of guessing; judge from context whether a tool call (a file read or edit) is what the user wants, and act accordingly.
</default_to_action>
```

（对话席用的是另一半 `do_not_act_before_instructions`，见 dream-os `00_portfolio/PROTOCOL.md` §5。）

## 用量卫生硬约束（直达·用量卫生，2026-09-12 原文版；六条原文与落地见 dream-os `.claude/skills/repo-hygiene/SKILL.md` §9）

- **课件审读禁整页图 Read**：走 pptx→文本导出（课件真源＝页面稿文本），文本审读；图片只做抽检，**每会话 ≤5 张**。
- **子代理配额**：每令 ≤5 个，只用于真正独立可并行的活；给子代理最小上下文；**禁 busy-wait**。
- **禁轮询循环**：等 CI、等文件——**退出会话、下次核对，或由 GitHub 通知**；空转的 `sleep 1` 也在烧五小时窗（它让会话保持活跃）。
