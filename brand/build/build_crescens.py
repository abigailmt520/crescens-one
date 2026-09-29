"""Build the crescens.one kit: two grounds (night = default, day = light) × two voices (zh, en).
Usage: python3 build_crescens.py [outdir]. Deps: fontTools, uharfbuzz, cairosvg, Pillow; Noto Serif CJK at /usr/share/fonts/opentype/noto/.
brand.py is only used for its helpers. Avatars carry no text and are identical across zh/en."""
import sys, os, hashlib
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import brand as B
import crescens as C
out = sys.argv[1] if len(sys.argv) > 1 else "kit"
for ground, pal in (("night", C.PAL_NIGHT), ("day", C.PAL_DAY)):
    for lang in ("zh", "en"):
        yt, bb = C.banner_youtube(pal=pal, lang=lang); xh, bx = C.header_x(pal=pal, lang=lang)
        assert 507 <= bb[0] and bb[2] <= 2053 and 508 <= bb[1] and bb[3] <= 931, (ground, lang, bb)
        assert bx[0] >= 380 or bx[3] <= 320, (ground, lang, bx)
        files = {
            "avatar-800": (B.svg(800, 800, C.mark(bg=pal["bg"], pal=pal)), 800, 800),
            "banner-youtube-2560x1440": (yt, 2560, 1440),
            "header-x-1500x500": (xh, 1500, 500),
        }
        reg = f"{out}/crescens/{ground}-{lang}"
        os.makedirs(reg, exist_ok=True)
        for name, (svg, w, h) in files.items():
            open(f"{reg}/{name}.svg", "w").write(svg)
            B.render(svg, f"{reg}/{name}.png", w, h)
            p = f"{reg}/{name}.png"
            print(hashlib.sha256(open(p, "rb").read()).hexdigest()[:16], os.path.getsize(p), p)
        print(ground, lang, "yt", [round(v) for v in bb], "x", [round(v) for v in bx])
