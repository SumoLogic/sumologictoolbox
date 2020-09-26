# -*- mode: python -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "./dist/linux"

block_cipher = None

added_files = [
    ( 'data/*', 'data' ),
    ( 'qtmodern', 'qtmodern' )
    ]

a = Analysis(['sumotoolbox.py'],
             pathex=['/netstuff/projects/PycharmProjects/sumologictoolbox'],
             binaries=None,
             datas=added_files,
             hiddenimports=['pkg_resources.py2_warn'],
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
