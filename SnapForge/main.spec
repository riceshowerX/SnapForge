# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# Analysis 部分
a = Analysis(
    ['main.py'],
    pathex=['.'],  # 添加脚本所在目录的路径
    binaries=[],
    datas=[
        ('resources/SnapForge.ico', 'resources')  # 包含资源文件
    ],
    hiddenimports=[],  # 如果有隐式导入的模块，添加到这里
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# PYZ 部分
pyz = PYZ(a.pure)

# EXE 部分
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 如果是 GUI 应用，将其更改为 False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 如果有其他需要处理的数据文件或资源，添加到 datas 中
