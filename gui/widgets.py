"""
Yeniden kullanılabilir özel tkinter widget'ları.

Koyu tema tutarlılığını sağlamak için standart tkinter widget'larının
stilize edilmiş sürümleri.
"""

import tkinter as tk
from tkinter import ttk

from gui import theme


class StyledLabel(tk.Label):
    """Temalı standart etiket."""

    def __init__(
        self,
        master,
        text: str = "",
        font=theme.FONT_NORMAL,
        fg: str = theme.FG_COLOR,
        bg: str = theme.BG_COLOR,
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            font=font,
            fg=fg,
            bg=bg,
            **kwargs
        )


class StyledEntry(tk.Entry):
    """Temalı metin girişi."""

    def __init__(
        self,
        master,
        width: int = theme.ENTRY_WIDTH,
        font=theme.FONT_NORMAL,
        show: str | None = None,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            font=font,
            bg=theme.ENTRY_BG,
            fg=theme.ENTRY_FG,
            insertbackground=theme.FG_COLOR,
            relief=tk.FLAT,
            highlightthickness=theme.BORDER_WIDTH,
            highlightbackground=theme.ENTRY_BORDER,
            highlightcolor=theme.ACCENT_COLOR,
            show=show if show else "",
            **kwargs
        )


class StyledText(tk.Text):
    """Temalı çok satırlı metin alanı."""

    def __init__(
        self,
        master,
        width: int = theme.LOG_WIDTH,
        height: int = theme.LOG_HEIGHT,
        font=theme.FONT_MONO_NORMAL,
        **kwargs
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
            highlightthickness=theme.BORDER_WIDTH,
            highlightbackground=theme.ENTRY_BORDER,
            highlightcolor=theme.ACCENT_COLOR,
            wrap=tk.WORD,
            state=tk.DISABLED,
            **kwargs
        )

    def append_text(self, text: str) -> None:
        """Metin alanına yeni log ekler ve en alta kaydırır."""
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text + "\n")
        self.see(tk.END)
        self.config(state=tk.DISABLED)

    def clear(self) -> None:
        """Metin alanını temizler."""
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED)


class StyledButton(tk.Button):
    """Temalı buton. Hover efekti destekler."""

    def __init__(
        self,
        master,
        text: str,
        command=None,
        font=theme.FONT_NORMAL,
        fg: str = theme.BUTTON_TEXT,
        bg: str = theme.BUTTON_BG,
        hover_bg: str | None = None,
        active_bg: str | None = None,
        width: int | None = theme.BUTTON_WIDTH,
        height: int = 1,
        **kwargs
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
            padx=theme.PADDING_MEDIUM,
            pady=theme.PADDING_SMALL,
            width=width,
            cursor="hand2",
            **kwargs
        )

        # Hover efektleri
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _event=None) -> None:
        if str(self["state"]) != "disabled":
            self.config(bg=self._hover_bg)

    def _on_leave(self, _event=None) -> None:
        self.config(bg=self._bg)

    def _on_press(self, _event=None) -> None:
        self.config(bg=self._active_bg)

    def _on_release(self, _event=None) -> None:
        self.config(bg=self._hover_bg)

    def set_state(self, state: str) -> None:
        """Buton durumunu değiştirir (normal/disabled)."""
        self.config(state=state)
        if state == "disabled":
            self.config(bg=theme.BUTTON_DISABLED_BG, fg=theme.BUTTON_DISABLED_TEXT)
        else:
            self.config(bg=self._bg, fg=theme.BUTTON_TEXT)


class PrimaryButton(StyledButton):
    """Birincil eylem butonu (mavi vurgulu)."""

    def __init__(self, master, text: str, command=None, font=theme.FONT_NORMAL, width=theme.BUTTON_WIDTH, **kwargs):
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
            **kwargs
        )


class SecondaryButton(StyledButton):
    """İkincil eylem butonu (gri vurgulu)."""

    def __init__(self, master, text: str, command=None, font=theme.FONT_NORMAL, width=theme.BUTTON_WIDTH, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            font=font,
            fg=theme.BUTTON_TEXT,
            bg=theme.BUTTON_BG,
            hover_bg=theme.BUTTON_HOVER,
            active_bg=theme.BUTTON_ACTIVE,
            width=width,
            **kwargs
        )


class HeaderFrame(tk.Frame):
    """
    Sihirbaz başlık çerçevesi.

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
        self._title_label.pack(anchor=tk.W, pady=(0, theme.PADDING_XS))

        if subtitle:
            self._subtitle_label = StyledLabel(
                self,
                text=subtitle,
                font=theme.FONT_NORMAL,
                fg=theme.FG_SECONDARY,
                bg=bg,
                wraplength=600,
                justify=tk.LEFT,
            )
            self._subtitle_label.pack(anchor=tk.W, pady=(0, theme.PADDING_MEDIUM))

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
            lightcolor=theme.PROGRESS_FILL,
            darkcolor=theme.PROGRESS_FILL,
            thickness=theme.PROGRESSBAR_HEIGHT,
        )

        super().__init__(
            master,
            style="Styled.Horizontal.TProgressbar",
            maximum=maximum,
            length=length,
            **kwargs
        )

    def set_progress(self, value: int) -> None:
        """İlerleme değerini ayarlar (0-100 arası)."""
        self["value"] = value


class CardFrame(tk.Frame):
    """Kart benzeri gruplama çerçevesi."""

    def __init__(self, master, bg: str = theme.BG_SECONDARY, padx: int = theme.PADDING_MEDIUM, pady: int = theme.PADDING_MEDIUM, **kwargs):
        super().__init__(
            master,
            bg=bg,
            padx=padx,
            pady=pady,
            **kwargs
        )