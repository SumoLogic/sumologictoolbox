# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "./dist/mac"

block_cipher = None

a = Analysis(['sumotoolbox.py'],
             binaries=[],
             datas=[( 'data/*', 'data' ),
                    ( 'qtmodern', 'qtmodern' ),
                    ( 'modules/*', 'modules' )],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sumotoolbox_mac',
          debug=False,
          strip=None,
          upx=True,
          console=False )
