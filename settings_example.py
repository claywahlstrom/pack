
"""
Settings

"""

import os as _os
import sys as _sys

from clay import env

IS_DEVELOPER = False

DEFAULT_BROWSER = 'firefox'
DOWNLOAD_CHUNK_SIZE = int(1e6) # bytes

DOCS_DIR = r'path-to-documents-folder'
FLASK_APP = 'app.py' # a common name for Flask web apps
HOME_DIR = _os.environ['HOME' if env.is_posix() else 'USERPROFILE']
PACKAGE_DIR = _os.path.join(_sys.prefix, 'Lib', 'site-packages', 'clay')
LOGS_DIR = _os.path.join(PACKAGE_DIR, 'logs')
TRASH = _os.path.join(HOME_DIR, 'Desktop', 'clay-trash')

CONSOLE_WIDTH = 80

JOBS_BREAK_SCHEDULES = {
    'WA': {'hours': 6, 'length': 0.5},
    'OR': {'hours': 5, 'length': 1.0}
}

JOBS_OVERTIME_RATES = {
    'WA': {'hours': 40, 'rate': 1.5},
    'OR': {'hours': 40, 'rate': 1.5}
}

NET_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept': 'text/html,text/plain,application/xhtml+xml,application/xml,application/_json;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Charset': 'Windows-1252,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8;q=0.5',
    'Connection': 'keep-alive'
}

SEARCH_EXCLUSIONS = [
    '.android', '.AndroidStudio1.5', 'eclipse', '.gradle', '.idlerc',
    '.jmc', '.matplotlib', '.oracle_jre_usage', '.pdfsam', '.phet',
    '3D Objects', 'AppData', 'Application Data', 'eclipse', 'Android',
    'NuGet'
]

SONG_TEMPO = 60 # default beats per minute
