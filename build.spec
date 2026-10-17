"""
AutoHomeWebSetup PyInstaller Build Spec

Build command:
    pyinstaller build.spec

Tek bir exe üretir: dist/AutoHomeWebSetup.exe
"""

import sys
from pathlib import Path

# Kullanıcı ortamında PyInstaller'ın block_cipher'ı
try:
    from PyInstaller.utils.hooks import collect_data_files
except ImportError:
    pass

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[SPECPATH],
    binaries=[],
    datas=[
        # Assets - icon, logo ve nssm.exe (HATA-06: nssm.exe eklendi)
        ('assets/icon.ico', 'assets'),
        ('assets/logo.png', 'assets'),
        ('assets/banner.png', 'assets'),
        ('assets/nssm.exe', 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        'queue',
        'threading',
        'ctypes',
        'json',
        'hashlib',
        'socket',
        'urllib.request',
        'zipfile',
        'shutil',
        're',
        'random',
        'string',
        'time',
        'datetime',
        'logging',
        'pathlib',
        'requests',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # NOT: 'inspect' (dataclasses buna bağımlı), 'pdb', 'doctest', 'pydoc'
        # stdlib içinde zincirleme import edildiği için exclude EDİLMEMELİDİR.
        'unittest',
        'test',
        'py_compile',
        'turtle',
        'turtledemo',
        'venv',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# HATA-09: onefile modunda COLLECT bloğu kaldırıldı.
# EXE içinde tüm veriler (a.binaries, a.zipfiles, a.datas) birleştirilir.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AHWS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Antivirüs false positive'lerini önlemek için UPX kapalı
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI uygulaması, terminal penceresi yok
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    uac_admin=True,  # UAC yönetici yetkisi manifest'i
)