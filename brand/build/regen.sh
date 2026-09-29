#!/usr/bin/env bash
# regen.sh —— crescens.one 标识件再生成（STUDIO-002 补丁1 §2）：装依赖 → 备 Noto Serif CJK 2.002 → 原样跑 build_crescens.py。
# 起因：build_crescens.py 在 macOS 上直接跑不起来（缺 uharfbuzz、cairosvg；brand.py 里 Noto 目录写的是 Linux 路径）。
#       三个生成脚本不改；本脚本在导入 brand 之后把 Noto 目录改指到本机，再执行 build_crescens.py。
# 用法（任意目录执行）：
#   bash brand/build/regen.sh <输出目录>   # 出四组（夜海／月白 × 中／英），png 与 svg 共 24 个文件
#   bash brand/build/regen.sh --check      # 出到临时目录，与 brand/crescens/ 逐个比对
# --check 的判据：svg 必须逐字节相同，不同即失败；png 逐字节不同时再逐像素比，
#   不同的像素不超过 2 个只记告警（不同机器上 cairo 出图会差一两个像素），超过即失败。
# 环境变量：
#   BRAND_CACHE  虚拟环境与字体的存放处，缺省 ~/.cache/crescens-brand（不在仓里）
#   NOTO_DIR     已有 Noto Serif CJK 的目录；给了就不下载，也不核字体哈希
# 前提：python3、curl；系统装有 cairo（macOS：brew install cairo）。
# 退出码：0 正常（--check 时＝通过，可带告警）；1 --check 不过；2 用法或环境错误；3 字体哈希不符。
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
CACHE="${BRAND_CACHE:-$HOME/.cache/crescens-brand}"
NOTO_TAG="Serif2.002"
NOTO_URL="https://github.com/notofonts/noto-cjk/raw/$NOTO_TAG/Serif/OTC"
# 三个字重的 sha256（2026-09-29 自上面地址下载后实测）
NOTO_SUMS="b313b12c4ca6bffd67fced7ace2050bc70c9d6768327157636f8cef7d5aa2c8d  NotoSerifCJK-SemiBold.ttc
9a9bec9cdcbb187384748656fa8e63f3c29b30c84e20fb91ec0af944e2bc2a29  NotoSerifCJK-Medium.ttc
93069d8e9e45d515cc421c971a79e6a5777704b348e36a9ef86578bf58adef77  NotoSerifCJK-Regular.ttc"
# 依赖版本＝比对时所用的版本
DEPS="fonttools==4.66.0 uharfbuzz==0.56.2 cairosvg==2.9.1 pillow==12.3.0"
MAX_PX=2   # png 允许不同的像素个数上限

[ "$#" -eq 1 ] || { echo "用法：bash brand/build/regen.sh <输出目录> ｜ --check"; exit 2; }
command -v python3 >/dev/null || { echo "✘ 缺 python3"; exit 2; }
command -v curl >/dev/null || { echo "✘ 缺 curl"; exit 2; }
export PYTHONDONTWRITEBYTECODE=1   # 不在 brand/build/ 里留 __pycache__

# ① 依赖：装进缓存目录里的虚拟环境，不动系统 python
VENV="$CACHE/venv"
if [ ! -x "$VENV/bin/python" ]; then
  mkdir -p "$CACHE" && python3 -m venv "$VENV" || { echo "✘ 建虚拟环境失败：$VENV"; exit 2; }
fi
# shellcheck disable=SC2086
"$VENV/bin/pip" install -q --disable-pip-version-check $DEPS || { echo "✘ 装依赖失败"; exit 2; }

# ② cairo：Homebrew 不在缺省前缀时，动态库要另指路径
if command -v brew >/dev/null; then
  export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"
fi

# ③ 字体：缺则下载，下完核哈希
if [ -n "${NOTO_DIR:-}" ]; then
  NOTO="$NOTO_DIR"
else
  NOTO="$CACHE/noto-$NOTO_TAG"; mkdir -p "$NOTO"
  for w in SemiBold Medium Regular; do
    f="NotoSerifCJK-$w.ttc"
    [ -s "$NOTO/$f" ] || curl -sSL --fail -o "$NOTO/$f" "$NOTO_URL/$f" || { echo "✘ 下载失败：$f"; rm -f "$NOTO/$f"; exit 2; }
  done
  (cd "$NOTO" && printf '%s\n' "$NOTO_SUMS" | shasum -a 256 -c --quiet -) || { echo "✘ 字体哈希不符：$NOTO"; exit 3; }
fi

# ④ 出图：导入 brand 后改指 Noto 目录，再原样执行 build_crescens.py
if [ "$1" = "--check" ]; then OUT="$(mktemp -d)"; else mkdir -p "$1" && OUT="$(cd "$1" && pwd)" || exit 2; fi
"$VENV/bin/python" - "$HERE" "$NOTO" "$OUT" <<'PY' || { echo "✘ build_crescens.py 失败"; exit 2; }
import os, runpy, sys
here, noto, out = sys.argv[1:4]
sys.path.insert(0, here); os.chdir(here)
import brand
brand.NOTO = noto.rstrip("/") + "/"
sys.argv = [os.path.join(here, "build_crescens.py"), out]
runpy.run_path(sys.argv[0], run_name="__main__")
PY
echo "✔ 已出图：$OUT/crescens"
[ "$1" = "--check" ] || exit 0

# ⑤ 比对：svg 逐字节；png 先逐字节，不同再逐像素
"$VENV/bin/python" - "$OUT/crescens" "$REPO/brand/crescens" "$MAX_PX" <<'PY'
import os, sys
from PIL import Image, ImageChops
built, kept, max_px = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = bad = warn = 0
for root, _, files in sorted(os.walk(built)):
    for f in sorted(files):
        if not f.endswith((".png", ".svg")):
            continue
        n += 1
        a = os.path.join(root, f); rel = os.path.relpath(a, built); b = os.path.join(kept, rel)
        if not os.path.exists(b):
            print(f"✘ 入库件里没有：{rel}"); bad += 1; continue
        if open(a, "rb").read() == open(b, "rb").read():
            continue
        if f.endswith(".svg"):
            print(f"✘ svg 不同：{rel}"); bad += 1; continue
        A, B = Image.open(a).convert("RGBA"), Image.open(b).convert("RGBA")
        if A.size != B.size:
            print(f"✘ png 尺寸不同：{rel}"); bad += 1; continue
        diff = ImageChops.difference(A, B)
        box = diff.getbbox(alpha_only=False)   # 缺省只看透明度通道，这里四个通道都要看
        data = diff.crop(box).tobytes() if box else b""   # 只数外接框里的像素
        px = sum(1 for i in range(0, len(data), 4) if data[i:i + 4] != b"\x00\x00\x00\x00")
        top = max(hi for _, hi in diff.getextrema())
        if px <= max_px:
            print(f"⚠ png 差 {px} 个像素（通道差最大 {top}），在允许范围内：{rel}"); warn += 1
        else:
            print(f"✘ png 差 {px} 个像素（通道差最大 {top}）：{rel}"); bad += 1
if n == 0:
    print("✘ 没有出图"); sys.exit(1)
if bad:
    print(f"✘ {n} 个文件里 {bad} 个不过，{warn} 个告警"); sys.exit(1)
print(f"✔ {n} 个文件比对通过" + (f"，其中 {warn} 个 png 有告警" if warn else "，全部逐字节相同"))
PY
rc=$?
rm -rf "$OUT"
exit "$rc"
