# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['WebCamCloneGUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('wc.ico', '.'),
        ('Install_virtual_cam', 'Install_virtual_cam'),
    ],
    hiddenimports=[
        'cv2',
        'pyvirtualcam',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'subprocess',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WebCamClone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='wc.ico',
    version='version_info.txt',
)
