"""
AHWS logo, banner ve ikon üretici (Pillow gerekir).

Kullanım:  python tools/generate_assets.py
Çıktı:     assets/icon.ico, assets/logo.png, assets/banner.png
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"

BG_DARK = (24, 24, 37, 255)      # #181825
BG = (30, 30, 46, 255)           # #1e1e2e
CARD = (40, 40, 58, 255)         # #28283a
SURFACE = (49, 50, 68, 255)      # #313244
PRIMARY = (30, 102, 245, 255)    # #1e66f5
ACCENT = (137, 180, 250, 255)    # #89b4fa
CYAN = (137, 220, 235, 255)      # #89dceb
GREEN = (166, 227, 161, 255)     # #a6e3a1
FG = (205, 214, 244, 255)        # #cdd6f4
FG2 = (166, 173, 200, 255)       # #a6adc8
SS = 4  # supersampling


def draw_mark(size: int) -> Image.Image:
    """Modern HA Sunucu Kümesi İkonu: Çift sunucu katmanı + aktif durum LED'leri + senkron kalkanı."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Dış squircle gövde
    pad = int(s * 0.03)
    d.rounded_rectangle(
        (pad, pad, s - 1 - pad, s - 1 - pad),
        radius=int(s * 0.24),
        fill=BG_DARK,
        outline=ACCENT,
        width=max(2, int(s * 0.032)),
    )

    # İç hafif parlak çerçeve
    in_pad = int(s * 0.09)
    d.rounded_rectangle(
        (in_pad, in_pad, s - 1 - in_pad, s - 1 - in_pad),
        radius=int(s * 0.18),
        fill=CARD,
    )

    # Üst Sunucu Modülü (Primary Node)
    rx1, rx2 = int(s * 0.17), int(s * 0.83)
    ry1_top, ry2_top = int(s * 0.21), int(s * 0.44)
    d.rounded_rectangle(
        (rx1, ry1_top, rx2, ry2_top),
        radius=int(s * 0.06),
        fill=SURFACE,
        outline=ACCENT,
        width=max(2, int(s * 0.022)),
    )
    # Üst sunucu LED ve havalandırma çizgileri
    led_r = int(s * 0.038)
    led_cx = int(s * 0.27)
    led_cy_top = (ry1_top + ry2_top) // 2
    d.ellipse((led_cx - led_r, led_cy_top - led_r, led_cx + led_r, led_cy_top + led_r), fill=GREEN)
    d.rounded_rectangle(
        (int(s * 0.37), led_cy_top - int(s * 0.018), int(s * 0.73), led_cy_top + int(s * 0.018)),
        radius=int(s * 0.01),
        fill=ACCENT,
    )

    # Alt Sunucu Modülü (Secondary Failover Node)
    ry1_bot, ry2_bot = int(s * 0.52), int(s * 0.75)
    d.rounded_rectangle(
        (rx1, ry1_bot, rx2, ry2_bot),
        radius=int(s * 0.06),
        fill=SURFACE,
        outline=CYAN,
        width=max(2, int(s * 0.022)),
    )
    led_cy_bot = (ry1_bot + ry2_bot) // 2
    d.ellipse((led_cx - led_r, led_cy_bot - led_r, led_cx + led_r, led_cy_bot + led_r), fill=GREEN)
    d.rounded_rectangle(
        (int(s * 0.37), led_cy_bot - int(s * 0.018), int(s * 0.73), led_cy_bot + int(s * 0.018)),
        radius=int(s * 0.01),
        fill=CYAN,
    )

    # Sağ alt köşe HA Onay Rozeti
    badge_r = int(s * 0.16)
    bcx, bcy = int(s * 0.75), int(s * 0.74)
    d.ellipse(
        (bcx - badge_r, bcy - badge_r, bcx + badge_r, bcy + badge_r),
        fill=PRIMARY,
        outline=BG_DARK,
        width=max(2, int(s * 0.025)),
    )
    # Rozet içi tik işareti
    lw = max(2, int(s * 0.036))
    d.line(
        (
            (bcx - int(badge_r * 0.42), bcy + int(badge_r * 0.02)),
            (bcx - int(badge_r * 0.08), bcy + int(badge_r * 0.36)),
            (bcx + int(badge_r * 0.46), bcy - int(badge_r * 0.32)),
        ),
        fill=GREEN,
        width=lw,
        joint="curve",
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
    """220x76 kompakt yatay marka logosu (Hoşgeldiniz ekranı için, #1e1e2e arkaplan uyumlu)."""
    w, h = 220 * SS, 76 * SS
    img = Image.new("RGBA", (w, h), BG)
    mark = draw_mark(68).resize((68 * SS, 68 * SS), Image.LANCZOS)
    img.paste(mark, (4 * SS, 4 * SS), mark)
    d = ImageDraw.Draw(img)
    d.text((82 * SS, 10 * SS), "AHWS", font=get_font(30 * SS, True), fill=FG)
    d.text((84 * SS, 46 * SS), "HIGH AVAILABILITY", font=get_font(11 * SS, True), fill=ACCENT)
    return img.resize((220, 76), Image.LANCZOS)


def make_banner() -> Image.Image:
    """760x110 modern sihirbaz üst banner görseli."""
    w, h = 760 * SS, 110 * SS
    img = Image.new("RGBA", (w, h), CARD)
    d = ImageDraw.Draw(img)
    # Alt vurgu çizgisi
    d.rectangle((0, h - 3 * SS, w, h), fill=PRIMARY)
    mark = draw_mark(82).resize((82 * SS, 82 * SS), Image.LANCZOS)
    img.paste(mark, (22 * SS, 14 * SS), mark)
    d.text((122 * SS, 20 * SS), "AutoHome Web Setup", font=get_font(30 * SS, True), fill=FG)
    d.text(
        (124 * SS, 62 * SS),
        "Otonom Yedekli (Failover) Web Sunucusu Kurulum Sihirbazi",
        font=get_font(15 * SS, False),
        fill=ACCENT,
    )
    return img.resize((760, 110), Image.LANCZOS)


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
