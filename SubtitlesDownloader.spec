# -*- mode: python -*-

block_cipher = None


a = Analysis(['SubtitlesDownloader.py'],
             pathex=['C:\\Users\\Camilo Mart�nez\\OneDrive - Universidad de Los Andes\\Proyectos\\Programas - Python\\SubtitlesDownloader'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SubtitlesDownloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='C:\\Users\\Camilo Mart�nez\\OneDrive - Universidad de Los Andes\\Proyectos\\Programas - Python\\SubtitlesDownloader\\icon.ico')
