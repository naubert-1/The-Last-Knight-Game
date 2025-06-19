import sys, os
from cx_Freeze import setup, Executable


script_principal = "main.py"  

# Dependências adicionais
includefiles = [
    "recursos/",  # pasta com imagens, sons, etc.
    "log.dat",    # arquivo de log
]

# Dependências adicionais
build_exe_options = {
    "packages": ["pygame", "random", "math", "os"],
    "include_files": [
    ],
}

setup(
    name="The last knight game",
    version="1.0",
    description="Um jogo em Pygame com obstáculos e bombas",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=None)], 
)