import PyInstaller.__main__
import os
icon='--add-data=Icon.ico;.' if os.name=='nt' else'--add-data=Icon.ico:.' 
style='--add-data=style.qss;.' if os.name=='nt' else'--add-data=style.qss:.' 
PyInstaller.__main__.run(
    [
        'main.py',
        '--name=Branch And Bound',
        '--windowed',
        '--onedir',
        '--icon=Icon.ico',
        icon,style
    ]
)