# -*- mode: python ; coding: utf-8 -*-
# Spec do PyInstaller para o Bot Vinculador PRO
# Gera um único .exe sem console, sem dependências externas.

a = Analysis(
    ['app_vinculador.py'],
    pathex=[],
    binaries=[],
    datas=[('web', 'web')],
    hiddenimports=[
        # Selenium
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.support.wait',
        'selenium.common.exceptions',
        # Selenium Manager (embutido no Selenium 4)
        'selenium.webdriver.common.selenium_manager',
        # Tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        # Requests (usado internamente pelo Selenium)
        'requests',
        'certifi',
        'urllib3',
        # CustomTkinter
        'customtkinter',
        'darkdetect',
        # Eel e dependências web
        'eel',
        'bottle',
        'bottle_websocket',
        'gevent',
        'geventwebsocket',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclui módulos pesados que não usamos
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'cv2',
        'PyQt5',
        'PyQt6',
        'wx',
        'gi',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BotVinculadorPRO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Sem janela preta de terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # Adicione um .ico aqui se quiser ícone personalizado
)
