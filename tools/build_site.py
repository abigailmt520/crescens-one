#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_site.py —— 生成 crescens.one 一页站 site/index.html（STUDIO-002 §3；仅标准库）。

页面上的图和字都从 brand/ 里取，不手打：
  标识      ＝ brand/crescens/night-zh/avatar-800.svg 的内容，内联
  字标与两行字＝ brand/crescens/night-{zh,en}/banner-youtube-2560x1440.svg 里文字块的轮廓，内联
  两声文案   ＝ brand/build/crescens.py 的 TAGLINE（只用来写无障碍说明与页面描述，不画成字）
去处读 tools/site_links.json：列在里面且有地址的才上页面，没地址的不列（STUDIO-002 补丁1 §2）。
邮箱的用户与域名两段分开写进页面，由页面脚本拼接，完整地址不落盘。

用法（任意目录执行）：
  python3 tools/build_site.py            # 生成 site/index.html
  python3 tools/build_site.py --check    # 只比对：现有页面与生成结果不同则 rc 1
  python3 tools/build_site.py --strict   # 已列的去处里有地址为空的则 rc 3，可与 --check 同用
退出码：0 正常；1 --check 不一致；2 取件或自查不过；3 --strict 下已列的去处有空地址。
"""
import ast, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "brand")
OUT = os.path.join(ROOT, "site", "index.html")
WORDMARK = "crescens.one"   # 只进 <title> 与无障碍说明；页面上看到的字标是轮廓
PAD = 6                     # 文字块外接框四周留白（横幅坐标系下的像素）

# 页面不许出现的字眼（STUDIO-002 §3）
BANNED_ZH = ("公司", "工作", "服务", "合作", "上班")
BANNED_EN = re.compile(r"\b(compan(y|ies)|works?|working|services?|business(es)?|hir(e|ing)|jobs?|cooperat\w*|partner\w*)\b", re.I)


def die(msg, rc=2):
    print(f"✘ {msg}"); sys.exit(rc)


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


def taglines():
    """从 crescens.py 源码里取 TAGLINE 字面量；不导入模块（导入要装出图依赖）。"""
    tree = ast.parse(read(BRAND, "build", "crescens.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "TAGLINE" for t in node.targets):
            t = ast.literal_eval(node.value)
            assert set(t) == {"zh", "en"} and all(len(v) == 2 for v in t.values()), "TAGLINE 结构变了"
            return t
    die("brand/build/crescens.py 里找不到 TAGLINE")


def svg_lines(path):
    lines = read(path).split("\n")
    if not (lines[0].startswith("<svg ") and lines[-1].strip() == "</svg>"):
        die(f"svg 结构不认识：{path}")
    return lines[1:-1]


def mark_svg():
    """头像 svg 去掉底色矩形后的内容；底色由页面给。"""
    body = svg_lines(os.path.join(BRAND, "crescens", "night-zh", "avatar-800.svg"))
    if not body[0].startswith('<rect width="800" height="800"'):
        die("头像 svg 首行不是底色矩形")
    return "\n".join(body[1:])


NUM = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")
ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "Q": 4, "A": 7, "Z": 0}


def path_points(d):
    """路径里出现的全部坐标点（含控制点，所以得到的外接框只会偏大不会偏小）。只认绝对坐标命令。"""
    pts, x, y = [], 0.0, 0.0
    for cmd, rest in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        if cmd not in ARGS:
            die(f"文字块路径里有不认识的命令 {cmd!r}")
        nums = [float(n) for n in NUM.findall(rest)]
        k = ARGS[cmd]
        if k == 0:
            continue
        if len(nums) % k:
            die(f"路径命令 {cmd} 的参数个数不对")
        for i in range(0, len(nums), k):
            a = nums[i:i + k]
            if cmd == "H": x = a[0]
            elif cmd == "V": y = a[0]
            elif cmd == "A": x, y = a[5], a[6]
            else:
                for j in range(0, k - 2, 2):
                    pts.append((a[j], a[j + 1]))
                x, y = a[-2], a[-1]
            pts.append((x, y))
    return pts


def text_block(lang):
    """横幅 svg 末行＝文字块：字标五件（crescens／点／月轮圈／月牙／ne）＋索引行＋一句话。返回 (内联 svg 内容, viewBox)。"""
    body = svg_lines(os.path.join(BRAND, "crescens", f"night-{lang}", "banner-youtube-2560x1440.svg"))
    block = body[-1]
    els = re.findall(r"<(path|circle)\b([^>]*?)/>", block)
    if [e[0] for e in els] != ["path", "path", "circle", "path", "path", "path", "path"] or "".join(f"<{t}{a}/>" for t, a in els) != block:
        die(f"night-{lang} 横幅的文字块结构变了，生成器要跟着改")
    pts = []
    for tag, attrs in els:
        if tag == "circle":
            cx, cy, r = (float(re.search(rf'\b{k}="([^"]+)"', attrs).group(1)) for k in ("cx", "cy", "r"))
            sw = float(re.search(r'stroke-width="([^"]+)"', attrs).group(1))
            pts += [(cx - r - sw, cy - r - sw), (cx + r + sw, cy + r + sw)]
        else:
            pts += path_points(re.search(r'\bd="([^"]+)"', attrs).group(1))
    x0, y0 = min(p[0] for p in pts) - PAD, min(p[1] for p in pts) - PAD
    x1, y1 = max(p[0] for p in pts) + PAD, max(p[1] for p in pts) + PAD
    return block, f"{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}"


def two(item, cls=""):
    """同一处的中英两种叫法；相同就只写一次。"""
    zh, en = html.escape(item["zh"]), html.escape(item["en"])
    if zh == en:
        return zh
    return f'<span class="zh" lang="zh-CN">{zh}</span><span class="en" lang="en">{en}</span>'


def dest(item):
    return f'<a href="{html.escape(item["url"], quote=True)}" rel="noopener">{two(item)}</a>'


def build():
    tl = taglines()
    links = json.loads(read(ROOT, "tools", "site_links.json"))
    blocks = {lang: text_block(lang) for lang in ("zh", "en")}
    listed = ([links["pg_site"]] if "pg_site" in links else []) + list(links.get("accounts", []))
    empty = [i.get("en") or i.get("zh") or "?" for i in listed if not i.get("url")]
    site = [i for i in listed[:1] if "pg_site" in links and i.get("url")]
    accts = [i for i in links.get("accounts", []) if i.get("url")]
    mail = links.get("mail")
    if mail and not (mail.get("user") and mail.get("host")):
        empty.append("mail")
        mail = None
    if mail and ("@" in mail["user"] or "@" in mail["host"]):
        die("site_links.json 的 mail 要把用户与域名两段分开写，不带 @")
    rows = []
    if site:
        rows.append(dest(site[0]))
    if accts:
        rows.append('<span class="dot" aria-hidden="true">·</span>'.join(dest(a) for a in accts))
    if mail:
        rows.append(f'<a id="mail" data-u="{html.escape(mail["user"], quote=True)}" data-h="{html.escape(mail["host"], quote=True)}">{two(mail)}</a>')
    if not rows:
        die("一个去处都没有：tools/site_links.json 里至少要有一条带地址的")
    nav = "\n".join(f"<li>{r}</li>" for r in rows)

    def h1(lang, code):
        block, vb = blocks[lang]
        label = html.escape(f"{WORDMARK} — {tl[lang][0]} — {tl[lang][1]}", quote=True)
        return f'<svg class="words {lang}" lang="{code}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{block}</svg>'

    page = f'''<!doctype html>
<!-- 本文件由 tools/build_site.py 生成，不手改；图与字取自 brand/。 -->
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{WORDMARK}</title>
<meta name="description" content="{html.escape(tl["en"][1], quote=True)}">
<style>
:root {{ --bg: #0F1E33; --ink: #F2E4B8; --gold: #E6B34A; --sea: #3E97A0; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; min-height: 100%; background: var(--bg); color: var(--ink); }}
body {{ min-height: 100vh; min-height: 100svh; display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 72px 16px 56px; font: 16px/1.6 -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", "Segoe UI", Roboto, sans-serif; }}
[data-lang="zh"] .en, [data-lang="en"] .zh {{ display: none; }}
main {{ display: flex; flex-direction: column; align-items: center; }}
.mark {{ width: min(62vw, 300px); height: auto; display: block; }}
h1 {{ margin: 8px 0 0; font-size: 0; line-height: 0; }}
.words {{ width: min(86vw, 460px); height: auto; }}
nav {{ margin-top: 40px; text-align: center; }}
nav ul {{ list-style: none; margin: 0; padding: 0; }}
nav li {{ margin: 6px 0; overflow-wrap: anywhere; }}
nav a {{ color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--sea); padding-bottom: 1px; }}
nav a:hover {{ border-bottom-color: var(--gold); }}
nav a:focus-visible, #lang:focus-visible {{ outline: 2px solid var(--gold); outline-offset: 3px; }}
.dot {{ margin: 0 .6em; color: var(--sea); }}
#lang {{ position: fixed; top: 16px; right: 16px; padding: 6px 12px; font: inherit; font-size: 14px; color: var(--ink);
  background: transparent; border: 1px solid var(--sea); border-radius: 999px; cursor: pointer; }}
#lang:hover {{ border-color: var(--gold); }}
</style>
</head>
<body>
<button id="lang" type="button">中／EN</button>
<main>
<svg class="mark" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800">
{mark_svg()}
</svg>
<h1>
{h1("zh", "zh-CN")}
{h1("en", "en")}
</h1>
</main>
<nav>
<ul>
{nav}
</ul>
</nav>
<script>
(function () {{
  var KEY = "crescens.lang", root = document.documentElement, cur = null;
  try {{ cur = localStorage.getItem(KEY); }} catch (e) {{}}
  if (cur !== "zh" && cur !== "en") cur = (navigator.language || "").toLowerCase().indexOf("zh") === 0 ? "zh" : "en";
  function show(v) {{ cur = v; root.setAttribute("data-lang", v); root.lang = v === "zh" ? "zh-CN" : "en"; }}
  show(cur);
  document.getElementById("lang").addEventListener("click", function () {{
    show(cur === "zh" ? "en" : "zh");
    try {{ localStorage.setItem(KEY, cur); }} catch (e) {{}}
  }});
  var m = document.getElementById("mail");
  if (m) {{ var addr = m.getAttribute("data-u") + "\\u0040" + m.getAttribute("data-h"); m.href = "mailto:" + addr; m.textContent = addr; }}
}})();
</script>
</body>
</html>
'''
    # 自查：字眼、外部资源、完整邮箱地址
    visible = re.sub(r'\sd="[^"]*"', "", page)
    hit = [w for w in BANNED_ZH if w in visible] + [m.group(0) for m in BANNED_EN.finditer(re.sub(r"<(style|script)>.*?</\1>", "", visible, flags=re.S))]
    if hit:
        die(f"页面里出现了不许出现的字眼：{hit}")
    if re.search(r"<script[^>]*\bsrc=|<link\b|@import|url\(|<img\b|<iframe\b", page):
        die("页面引了外部资源")
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", page):
        die("页面里出现了完整邮箱地址")
    return page, empty


def main():
    flags = set(sys.argv[1:])
    if flags - {"--check", "--strict"}:
        die("用法：python3 tools/build_site.py [--check] [--strict]")
    page, empty = build()
    if "--check" in flags:
        if not os.path.exists(OUT) or read(OUT) != page:
            print("✘ site/index.html 与生成结果不一致：重跑 python3 tools/build_site.py"); sys.exit(1)
        print(f"✔ site/index.html 与生成结果一致（{len(page.encode('utf-8'))} 字节）")
    else:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"✔ 已生成 site/index.html（{len(page.encode('utf-8'))} 字节）")
    if empty:
        print(f"{'✘' if '--strict' in flags else '⚠'} 已列但地址为空、没上页面的去处 {len(empty)} 处：" + "、".join(empty))
        if "--strict" in flags:
            sys.exit(3)


if __name__ == "__main__":
    main()
