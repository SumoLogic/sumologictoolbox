# -*- mode: python -*-

block_cipher = None

added_files = [
    ( 'data/apiurls.json', 'data' ),
    ( 'data/sumotoolbox.ui', 'data' ),
    ( 'data/collectorcopy.ui', 'data' )
    ]

a = Analysis(['sumotoolbox.py'],
             pathex=['D:\\stuff\\pycharm_checkouts\\sumologictoolbox'],
             binaries=None,
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
