"""
AHWS logo, banner ve ikon üretici (Pillow gerekir).

Kullanım:  python tools/generate_assets.py
Çıktı:     assets/icon.ico, assets/logo.png, assets/banner.png
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"

BG = (30, 30, 46, 255)        # #1e1e2e
CARD = (40, 40, 58, 255)      # #28283a
ACCENT = (137, 180, 250, 255) # #89b4fa
GREEN = (166, 227, 161, 255)  # #a6e3a1
FG = (205, 214, 244, 255)     # #cdd6f4
FG2 = (166, 173, 200, 255)    # #a6adc8
SS = 4  # supersampling


def draw_mark(size: int) -> Image.Image:
    """Kare logo işareti: yuvarlak köşeli kart + iki bağlı sunucu düğümü + onay."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * 0.22), fill=BG)
    d.rounded_rectangle(
        (s * 0.04, s * 0.04, s * 0.96, s * 0.96),
        radius=int(s * 0.18), outline=ACCENT, width=max(2, int(s * 0.03)),
    )

    # İki sunucu düğümü (primary / secondary) ve aralarında bağlantı
    r = s * 0.13
    p1 = (s * 0.30, s * 0.38)
    p2 = (s * 0.70, s * 0.38)
    lw = max(2, int(s * 0.035))
    d.line((p1, p2), fill=ACCENT, width=lw)
    for (cx, cy), col in ((p1, ACCENT), (p2, GREEN)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
        d.ellipse((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), fill=BG)

    # Alt: onay işareti (failover hazır)
    d.line(
        ((s * 0.36, s * 0.68), (s * 0.46, s * 0.78), (s * 0.64, s * 0.58)),
        fill=GREEN, width=int(lw * 1.4), joint="curve",
    )
    return img.resize((size, size), Image.LANCZOS)


def get_font(px: int, bold: bool = True):
    for name in ("segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def make_logo() -> Image.Image:
    """200x100: işaret + AHWS yazısı (şeffaf arka plan)."""
    w, h = 200 * SS, 100 * SS
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mark = draw_mark(88).resize((88 * SS, 88 * SS), Image.LANCZOS)
    img.paste(mark, (6 * SS, 6 * SS), mark)
    d = ImageDraw.Draw(img)
    d.text((104 * SS, 26 * SS), "AHWS", font=get_font(26 * SS), fill=ACCENT)
    d.text((105 * SS, 60 * SS), "High Availability", font=get_font(10 * SS, False), fill=FG2)
    return img.resize((200, 100), Image.LANCZOS)


def make_banner() -> Image.Image:
    """800x200 sihirbaz banner'ı."""
    w, h = 800 * SS, 200 * SS
    img = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, h - 6 * SS, w, h), fill=ACCENT)
    mark = draw_mark(150).resize((150 * SS, 150 * SS), Image.LANCZOS)
    img.paste(mark, (30 * SS, 25 * SS), mark)
    d.text((210 * SS, 45 * SS), "AutoHome Web Setup", font=get_font(52 * SS), fill=ACCENT)
    d.text(
        (212 * SS, 115 * SS),
        "Ileri > Ileri > Kur  -  Otomatik Failover Web Sunucusu",
        font=get_font(22 * SS, False), fill=FG2,
    )
    return img.resize((800, 200), Image.LANCZOS)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    draw_mark(256).save(
        ASSETS / "icon.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    make_logo().save(ASSETS / "logo.png")
    make_banner().save(ASSETS / "banner.png")
    print("Olusturuldu:", ", ".join(p.name for p in (ASSETS / "icon.ico", ASSETS / "logo.png", ASSETS / "banner.png")))


if __name__ == "__main__":
    main()
