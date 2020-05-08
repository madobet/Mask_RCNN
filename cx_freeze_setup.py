import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "build_exe": "dist/",
    "optimize": 0
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "tf_detection",
        version = "0.1",
        description="Tensorflow Detection",
        options={ "build_exe": build_exe_options },
        executables = [Executable("tf_serving_client.py", base=base)])
