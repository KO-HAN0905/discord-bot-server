# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['bot.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('cogs', 'cogs'),
        ('data', 'data'),
        ('utils', 'utils'),
        ('credentials.json', '.'),
        ('config.py', '.'),
        ('updater.py', '.'),
        ('version.json', '.'),
    ],
    hiddenimports=[
        'discord',
        'discord.ext.commands',
        'dotenv',
        'gspread',
        'google.auth',
        'google.auth.transport.requests',
        'openpyxl',
        'requests',
        'APScheduler',
        'gtts',
        'pydub',
        'nacl',
        'google.generativeai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Discord-Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Discord-Bot'
)
