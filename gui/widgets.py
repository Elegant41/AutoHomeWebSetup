"""
Yeniden kullanılabilir özel tkinter widget'ları.

Modern koyu tema tutarlılığını sağlamak için geliştirilmiş
kartlar, butonlar, renkli log ekranı ve üst adım çubuğu (WizardStepBar).
"""

import tkinter as tk
from tkinter import ttk

from gui import theme
from utils.i18n import get_language, t


class StyledLabel(tk.Label):
    """Temalı standart etiket."""

    def __init__(
        self,
        master,
        text: str = "",
        font=theme.FONT_NORMAL,
        fg: str = theme.FG_COLOR,
        bg: str = theme.BG_COLOR,
        **kwargs,
    ):
        super().__init__(
            master,
            text=text,
            font=font,
            fg=fg,
            bg=bg,
            **kwargs,
        )


class StyledEntry(tk.Entry):
    """Temalı metin girişi (sağ tık Kes/Kopyala/Yapıştır menüsü destekli)."""

    def __init__(
        self,
        master,
        width: int = theme.ENTRY_WIDTH,
        font=theme.FONT_NORMAL,
        show: str | None = None,
        **kwargs,
    ):
        super().__init__(
            master,
            width=width,
            font=font,
            bg=theme.ENTRY_BG,
            fg=theme.ENTRY_FG,
            insertbackground=theme.ACCENT_COLOR,
            selectbackground=theme.BUTTON_PRIMARY_BG,
            selectforeground=theme.BUTTON_TEXT,
            relief=tk.FLAT,
            bd=4,
            highlightthickness=theme.BORDER_WIDTH,
            highlightbackground=theme.ENTRY_BORDER,
            highlightcolor=theme.ACCENT_COLOR,
            show=show if show else "",
            **kwargs,
        )
        self._bind_context_menu()

    def _bind_context_menu(self) -> None:
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=theme.BG_SECONDARY,
            fg=theme.FG_COLOR,
            activebackground=theme.BUTTON_PRIMARY_BG,
            activeforeground=theme.BUTTON_TEXT,
            bd=1,
            relief=tk.FLAT,
        )
        menu.add_command(label="Kes", command=lambda: self.event_generate("<<Cut>>"))
        menu.add_command(label="Kopyala", command=lambda: self.event_generate("<<Copy>>"))
        menu.add_command(label="Yapıştır", command=lambda: self.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Tümünü Seç", command=lambda: self.select_range(0, tk.END))

        def _popup(event):
            try:
                self.focus_set()
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        self.bind("<Button-3>", _popup)


class StyledText(tk.Text):
    """Temalı, renklendirilmiş çok satırlı terminal/log alanı."""

    def __init__(
        self,
        master,
        width: int = theme.LOG_WIDTH,
        height: int = theme.LOG_HEIGHT,
        font=theme.FONT_MONO_SMALL,
        **kwargs,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            font=font,
            bg=theme.LOG_BG,
            fg=theme.LOG_FG,
            insertbackground=theme.FG_COLOR,
            relief=tk.FLAT,
            padx=10,
            pady=8,
            highlightthickness=theme.BORDER_WIDTH,
            highlightbackground=theme.CARD_BORDER,
            highlightcolor=theme.ACCENT_COLOR,
            wrap=tk.WORD,
            state=tk.DISABLED,
            **kwargs,
        )
        self.tag_configure("success", foreground=theme.SUCCESS_COLOR)
        self.tag_configure("error", foreground=theme.ERROR_COLOR)
        self.tag_configure("warning", foreground=theme.WARNING_COLOR)
        self.tag_configure("info", foreground=theme.INFO_COLOR)
        self.tag_configure("muted", foreground=theme.FG_SECONDARY)

    def append_text(self, text: str) -> None:
        """Metin alanına içeriğe göre renklendirilmiş yeni log satırı ekler."""
        tag = None
        stripped = text.strip()
        if stripped.startswith("✓") or "başarıyla" in stripped.lower() or "tamamlandı" in stripped.lower():
            tag = "success"
        elif stripped.startswith("✕") or "[error]" in stripped.lower() or "hata" in stripped.lower():
            tag = "error"
        elif stripped.startswith("⚠") or "[warning]" in stripped.lower() or "iptal" in stripped.lower():
            tag = "warning"
        elif stripped.startswith("●") or "indiriliyor" in stripped.lower():
            tag = "info"

        self.config(state=tk.NORMAL)
        if tag:
            self.insert(tk.END, text + "\n", tag)
        else:
            self.insert(tk.END, text + "\n")
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def clear(self) -> None:
        """Metin alanını temizler."""
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)


class StyledButton(tk.Button):
    """Temalı modern buton. Hover ve aktif durum efektlerini destekler."""

    def __init__(
        self,
        master,
        text: str,
        command=None,
        font=theme.FONT_NORMAL_BOLD,
        fg: str = theme.BUTTON_TEXT,
        bg: str = theme.BUTTON_BG,
        hover_bg: str | None = None,
        active_bg: str | None = None,
        width: int | None = theme.BUTTON_WIDTH,
        height: int = 1,
        padx: int = theme.PADDING_MEDIUM,
        pady: int = 6,
        **kwargs,
    ):
        self._bg = bg
        self._hover_bg = hover_bg or bg
        self._active_bg = active_bg or bg

        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            fg=fg,
            bg=bg,
            activeforeground=fg,
            activebackground=self._active_bg,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightcolor=theme.ACCENT_COLOR,
            highlightbackground=bg,
            padx=padx,
            pady=pady,
            width=width,
            height=height,
            cursor="hand2",
            **kwargs,
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Return>", lambda e: self.invoke())

    def _on_enter(self, _event=None) -> None:
        if str(self["state"]) != "disabled":
            self.config(bg=self._hover_bg, highlightbackground=self._hover_bg)

    def _on_leave(self, _event=None) -> None:
        if str(self["state"]) != "disabled":
            self.config(bg=self._bg, highlightbackground=self._bg)

    def _on_press(self, _event=None) -> None:
        if str(self["state"]) != "disabled":
            self.config(bg=self._active_bg, highlightbackground=self._active_bg)

    def _on_release(self, _event=None) -> None:
        if str(self["state"]) != "disabled":
            self.config(bg=self._hover_bg, highlightbackground=self._hover_bg)

    def set_state(self, state: str) -> None:
        """Buton durumunu değiştirir (normal/disabled)."""
        self.config(state=state)
        if state == "disabled":
            self.config(bg=theme.BUTTON_DISABLED_BG, highlightbackground=theme.BUTTON_DISABLED_BG, fg=theme.BUTTON_DISABLED_TEXT, cursor="arrow")
        else:
            self.config(bg=self._bg, highlightbackground=self._bg, fg=theme.BUTTON_TEXT, cursor="hand2")


class PrimaryButton(StyledButton):
    """Birincil eylem butonu (canlı mavi vurgulu)."""

    def __init__(self, master, text: str, command=None, font=theme.FONT_NORMAL_BOLD, width=theme.BUTTON_WIDTH, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            fg=theme.BUTTON_TEXT,
            bg=theme.BUTTON_PRIMARY_BG,
            hover_bg=theme.BUTTON_PRIMARY_HOVER,
            active_bg=theme.BUTTON_PRIMARY_ACTIVE,
            width=width,
            **kwargs,
        )


class SecondaryButton(StyledButton):
    """İkincil eylem butonu (modern koyu gri vurgulu)."""

    def __init__(self, master, text: str, command=None, font=theme.FONT_NORMAL, width=theme.BUTTON_WIDTH, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            fg=theme.FG_COLOR,
            bg=theme.BUTTON_BG,
            hover_bg=theme.BUTTON_HOVER,
            active_bg=theme.BUTTON_ACTIVE,
            width=width,
            **kwargs,
        )


class DangerButton(StyledButton):
    """Tehlikeli işlem butonu (kırmızı vurgulu, örn: Kurulumu Kaldır)."""

    def __init__(self, master, text: str, command=None, font=theme.FONT_NORMAL_BOLD, width=theme.BUTTON_WIDTH, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            fg=theme.BUTTON_TEXT,
            bg=theme.BUTTON_DANGER_BG,
            hover_bg=theme.BUTTON_DANGER_HOVER,
            active_bg=theme.BUTTON_DANGER_ACTIVE,
            width=width,
            **kwargs,
        )


class HeaderFrame(tk.Frame):
    """
    Sihirbaz sayfa başlık çerçevesi.

    Sayfa başlığı ve alt başlığı gösterir.
    """

    def __init__(self, master, title: str, subtitle: str = "", bg: str = theme.BG_COLOR):
        super().__init__(master, bg=bg)

        self._title_label = StyledLabel(
            self,
            text=title,
            font=theme.FONT_TITLE,
            fg=theme.FG_COLOR,
            bg=bg,
        )
        self._title_label.pack(anchor=tk.W, pady=(0, 2))

        if subtitle:
            self._subtitle_label = StyledLabel(
                self,
                text=subtitle,
                font=theme.FONT_NORMAL,
                fg=theme.FG_SECONDARY,
                bg=bg,
                wraplength=760,
                justify=tk.LEFT,
            )
            self._subtitle_label.pack(anchor=tk.W, pady=(0, theme.PADDING_XS))

    def set_title(self, title: str) -> None:
        self._title_label.config(text=title)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle_label.config(text=subtitle)


class StyledProgressbar(ttk.Progressbar):
    """Temalı ilerleme çubuğu."""

    def __init__(self, master, maximum: int = 100, length: int = 400, **kwargs):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Styled.Horizontal.TProgressbar",
            troughcolor=theme.PROGRESS_BG,
            background=theme.PROGRESS_FILL,
            bordercolor=theme.PROGRESS_BG,
            lightcolor=theme.ACCENT_COLOR,
            darkcolor=theme.PROGRESS_FILL,
            thickness=theme.PROGRESSBAR_HEIGHT,
        )

        super().__init__(
            master,
            style="Styled.Horizontal.TProgressbar",
            maximum=maximum,
            length=length,
            **kwargs,
        )

    def set_progress(self, value: int) -> None:
        """İlerleme değerini ayarlar (0-100 arası)."""
        self["value"] = value


class CardFrame(tk.Frame):
    """İnce kenarlıklı modern kart çerçevesi."""

    def __init__(
        self,
        master,
        bg: str = theme.BG_SECONDARY,
        padx: int = theme.PADDING_MEDIUM,
        pady: int = 12,
        border_color: str = theme.CARD_BORDER,
        **kwargs,
    ):
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", border_color)
        kwargs.setdefault("highlightcolor", border_color)
        super().__init__(
            master,
            bg=bg,
            padx=padx,
            pady=pady,
            **kwargs,
        )

    def set_active(self, active: bool) -> None:
        """Kartın seçili/aktif kenarlık rengini günceller."""
        color = theme.CARD_BORDER_ACTIVE if active else theme.CARD_BORDER
        self.config(highlightbackground=color, highlightcolor=color)


class WizardStepBar(tk.Frame):
    """
    Üst navigasyon ve 5 adımlı sihirbaz ilerleme çubuğu.

    Sol: AHWS marka rozeti
    Orta: 1. Başlangıç -> 2. Rol & Eşleşme -> 3. Sunucu & Tünel -> 4. Kurulum -> 5. Durum Paneli
    Sağ: Aktif dili gösteren TR | EN dil seçici
    """

    STEP_ORDER = [
        ("welcome", "step_nav_1"),
        ("sync_settings", "step_nav_2"),
        ("server_settings", "step_nav_3"),
        ("install", "step_nav_4"),
        ("finish", "step_nav_5"),
    ]

    def __init__(self, master, controller):
        super().__init__(master, bg=theme.BG_HEADER, height=48)
        self.controller = controller
        self._step_labels: dict[str, tk.Label] = {}

        inner = tk.Frame(self, bg=theme.BG_HEADER, padx=theme.PADDING_LARGE, pady=8)
        inner.pack(fill=tk.X)

        # Sol: Marka
        brand_frame = tk.Frame(inner, bg=theme.BG_HEADER)
        brand_frame.pack(side=tk.LEFT)

        brand_dot = tk.Label(
            brand_frame,
            text="●",
            font=("Segoe UI", 12, "bold"),
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_HEADER,
        )
        brand_dot.pack(side=tk.LEFT, padx=(0, 6))

        brand_lbl = tk.Label(
            brand_frame,
            text="AHWS",
            font=("Segoe UI", 12, "bold"),
            fg=theme.FG_COLOR,
            bg=theme.BG_HEADER,
        )
        brand_lbl.pack(side=tk.LEFT)

        ver_lbl = tk.Label(
            brand_frame,
            text="v1.0",
            font=theme.FONT_SMALL,
            fg=theme.ACCENT_COLOR,
            bg=theme.BG_TERTIARY,
            padx=6,
            pady=1,
        )
        ver_lbl.pack(side=tk.LEFT, padx=(6, 0))

        # Sağ: TR | EN Dil Seçici
        lang_frame = tk.Frame(inner, bg=theme.BG_TERTIARY, padx=2, pady=2)
        lang_frame.pack(side=tk.RIGHT)

        current_lang = get_language()
        self.btn_tr = tk.Button(
            lang_frame,
            text="TR",
            command=lambda: self.controller.change_language("tr"),
            font=theme.FONT_SMALL_BOLD,
            fg=theme.BUTTON_TEXT if current_lang == "tr" else theme.FG_SECONDARY,
            bg=theme.BUTTON_PRIMARY_BG if current_lang == "tr" else theme.BG_TERTIARY,
            activebackground=theme.BUTTON_PRIMARY_HOVER,
            activeforeground=theme.BUTTON_TEXT,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
        )
        self.btn_tr.pack(side=tk.LEFT)

        self.btn_en = tk.Button(
            lang_frame,
            text="EN",
            command=lambda: self.controller.change_language("en"),
            font=theme.FONT_SMALL_BOLD,
            fg=theme.BUTTON_TEXT if current_lang == "en" else theme.FG_SECONDARY,
            bg=theme.BUTTON_PRIMARY_BG if current_lang == "en" else theme.BG_TERTIARY,
            activebackground=theme.BUTTON_PRIMARY_HOVER,
            activeforeground=theme.BUTTON_TEXT,
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
        )
        self.btn_en.pack(side=tk.LEFT)

        # Orta: Adım Göstergeleri
        steps_frame = tk.Frame(inner, bg=theme.BG_HEADER)
        steps_frame.pack(side=tk.TOP, pady=(2, 0))

        for idx, (page_name, i18n_key) in enumerate(self.STEP_ORDER):
            lbl = tk.Label(
                steps_frame,
                text=t(i18n_key),
                font=theme.FONT_SMALL,
                fg=theme.FG_DISABLED,
                bg=theme.BG_HEADER,
                padx=8,
                pady=3,
            )
            lbl.pack(side=tk.LEFT)
            self._step_labels[page_name] = lbl

            if idx < len(self.STEP_ORDER) - 1:
                sep = tk.Label(
                    steps_frame,
                    text="›",
                    font=theme.FONT_NORMAL_BOLD,
                    fg=theme.FG_DISABLED,
                    bg=theme.BG_HEADER,
                    padx=2,
                )
                sep.pack(side=tk.LEFT)

        # Alt ince ayırıcı çizgi
        divider = tk.Frame(self, bg=theme.CARD_BORDER, height=1)
        divider.pack(fill=tk.X, side=tk.BOTTOM)

    def set_active_step(self, current_page_name: str) -> None:
        """Aktif sayfaya göre adım göstergelerini renklendirir."""
        order_names = [name for name, _ in self.STEP_ORDER]
        try:
            active_idx = order_names.index(current_page_name)
        except ValueError:
            active_idx = 0

        for idx, (page_name, i18n_key) in enumerate(self.STEP_ORDER):
            lbl = self._step_labels.get(page_name)
            if not lbl:
                continue
            base_text = t(i18n_key)
            if idx < active_idx:
                # Tamamlanan adım
                step_title = base_text.split(".", 1)[-1].strip()
                lbl.config(
                    text=f"✓ {step_title}",
                    fg=theme.SUCCESS_COLOR,
                    bg=theme.BG_HEADER,
                    font=theme.FONT_SMALL_BOLD,
                )
            elif idx == active_idx:
                # Aktif adım
                lbl.config(
                    text=base_text,
                    fg=theme.BUTTON_TEXT,
                    bg=theme.BUTTON_PRIMARY_BG,
                    font=theme.FONT_SMALL_BOLD,
                )
            else:
                # Gelecek adım
                lbl.config(
                    text=base_text,
                    fg=theme.FG_DISABLED,
                    bg=theme.BG_HEADER,
                    font=theme.FONT_SMALL,
                )