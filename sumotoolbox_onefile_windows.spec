# -*- mode: python -*-

block_cipher = None

added_files = [
    ( 'data/apiurls.json', 'data' ),
    ( 'data/sumotoolbox.ui', 'data' ),
    ]

added_dlls = [
    ( 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\10.0.18362.0\\ucrt\\DLLs\\x64\\api-ms-win-crt-convert-l1-1-0.dll', 'api-ms-win-crt-convert-l1-1-0.dll'),
    ]

a = Analysis(['sumotoolbox.py'],
             pathex=['Z:\\PycharmProjects\\sumologictoolbox'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sumotoolbox',
          debug=False,
          strip=None,
          upx=True,
          console=False )
