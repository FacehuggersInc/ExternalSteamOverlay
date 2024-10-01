import os
from steamworks import STEAMWORKS

os.add_dll_directory(os.getcwd())

steamworks = STEAMWORKS()