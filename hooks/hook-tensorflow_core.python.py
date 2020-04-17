# https://github.com/pyinstaller/pyinstaller/issues/4400#issuecomment-551147137
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('tensorflow_core')
