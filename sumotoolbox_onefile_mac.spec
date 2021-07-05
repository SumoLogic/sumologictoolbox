# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "./dist/mac"

block_cipher = None


a = Analysis(['sumotoolbox.py'],
             pathex=['/Users/tmacdonald/.local/share/virtualenvs/sumologictoolbox-FkMoZDI3/lib/python3.8/site-packages/PyQt5',
                     '/Users/tmacdonald/sumologictoolbox'],
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
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='sumotoolbox',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='sumotoolbox_mac')
app = BUNDLE(coll,
             name='sumotoolbox-mac.app',
             icon=None,
             bundle_identifier=None)
