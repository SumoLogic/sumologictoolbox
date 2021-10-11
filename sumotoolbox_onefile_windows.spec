# -*- mode: python -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "dist\\windows"
block_cipher = None

from PyInstaller.utils.hooks import collect_all

datas = [
    ( 'data/*', 'data' ),
    ( 'qtmodern', 'qtmodern' ),
    ( 'modules/*', 'modules' )
    ]
hiddenimports = []
binaries = []
tmp_ret = collect_all('tzdata')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]




a = Analysis(['sumotoolbox.py'],
             pathex=['Z:\\Projects\\PycharmProjects\\sumologictoolbox'],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
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
          name='sumotoolbox_windows',
          debug=False,
          strip=None,
          upx=True,
          console=True )
