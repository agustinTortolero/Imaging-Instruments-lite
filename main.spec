# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os

# Paths to your files and directories
assets_dir = 'C:\\AgustinTortolero_repos\\ImagingInstruments\\imaging-instruments-lite\\assets'
libs_dir = 'C:\\AgustinTortolero_repos\\ImagingInstruments\\imaging-instruments-lite\\libs'
haarcascade_path = 'C:\\AgustinTortolero_repos\\Python_tinker\\Python_Tkinter\\Python_Tkinter\\tkinter_env\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml'
gpu_filtering_dll_path = 'C:\\AgustinTortolero_repos\\ImagingInstruments\\imaging-instruments-lite\\libs\\opencv_cuda_lib.dll'
icon_path = 'C:\\AgustinTortolero_repos\\ImagingInstruments\\imaging-instruments-lite\\assets\\icon-Imaging-instruments-lite.png'

# Define the Analysis object
a = Analysis(
    ['main.py'],  # Your main script
    pathex=['C:\\AgustinTortolero_repos\\ImagingInstruments\\imaging-instruments-lite'],
    binaries=[
        (gpu_filtering_dll_path, 'libs')  # Add all DLLs here
    ],
    datas=[
        (haarcascade_path, 'cv2/data'),  # Haar Cascade path
        (icon_path, 'assets'),           # Icon path
        (assets_dir, 'assets'),          # Include the assets directory
        (libs_dir, 'libs')               # Include the libs directory
    ],
    hiddenimports=[
        'cv2',
        'matplotlib',
        'numpy'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    cipher=None,
    noarchive=False
)

# Define the PYZ object
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Define the EXE object
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='ImagingInstrumentsLite',  # Set your desired output name here
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_path  # Icon file path
)

# Define the COLLECT object
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ImagingInstrumentsLite'  # Set your desired output name here
)
