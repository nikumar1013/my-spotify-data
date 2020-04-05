#!d:\programming\spotify-data-app\venv\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'coards==1.0.5','console_scripts','coards'
__requires__ = 'coards==1.0.5'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('coards==1.0.5', 'console_scripts', 'coards')()
    )
